"""Google 공식 OAuth 예제를 바탕으로 한 읽기 전용 인증 확인용 프로그램."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
DEFAULT_DIR = Path.home() / ".config" / "google-workspace"
SAMPLE_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"


def configured_path(name: str, filename: str) -> Path:
    return Path(os.environ.get(name, str(DEFAULT_DIR / filename))).expanduser()


def save_private(path: Path, text: str) -> None:
    """토큰은 소유자만 읽는 임시 파일에 쓴 뒤 교체합니다(POSIX 0600)."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix=".oauth-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check_scopes(creds: Credentials) -> None:
    # 기존의 넓은 권한 토큰을 읽기 전용 실습용으로 오인하지 않습니다.
    actual = creds.granted_scopes if creds.granted_scopes is not None else creds.scopes
    if isinstance(actual, str):
        actual = actual.split()
    if set(actual or []) != set(SCOPES):
        raise ValueError("실습용 읽기 권한과 다른 토큰입니다. 새 실습 앱으로 인증하세요.")


def load_token(path: Path) -> Credentials:
    """MCP에서도 사용하는 함수. 브라우저를 열거나 새 동의를 요청하지 않습니다."""
    if not path.is_file():
        raise ValueError("인증 토큰이 없습니다. google_auth_check.py를 먼저 실행하세요.")
    # scopes 인자를 덮어쓰지 않아 저장된 넓은 권한을 발견할 수 있습니다.
    creds = Credentials.from_authorized_user_file(str(path))
    check_scopes(creds)
    if not creds.valid:
        if not creds.refresh_token:
            raise ValueError("재인증이 필요합니다. google_auth_check.py --reauth를 실행하세요.")
        creds.refresh(Request())
        check_scopes(creds)
        save_private(path, creds.to_json())
    return creds


class PrivateURLFlow(InstalledAppFlow):
    """표준 loopback 흐름을 유지하면서 생성된 로그인 URL만 별도 파일에 둡니다."""

    auth_url_file: Path | None = None
    wrote_url = False

    def authorization_url(self, **kwargs):
        url, state = super().authorization_url(**kwargs)
        if self.auth_url_file is not None:
            path = self.auth_url_file
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            # 기존 파일을 덮어쓰지 않습니다. URL은 로그/표준 출력에 쓰지 않습니다.
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(url)
            self.wrote_url = True
            print(f"로그인 URL을 별도 파일에 준비했습니다: {path}", file=sys.stderr)
        return url, state


def authenticate(credentials_path: Path, token_path: Path, *, no_browser=False,
                 auth_url_file: Path | None = None, timeout=300) -> Credentials:
    flow = PrivateURLFlow.from_client_secrets_file(str(credentials_path), SCOPES)
    flow.auth_url_file = auth_url_file
    try:
        creds = flow.run_local_server(
            host="localhost", bind_addr="127.0.0.1", port=0,
            open_browser=not no_browser,
            authorization_prompt_message="",
            success_message="Authentication complete. You can close this tab.",
            timeout_seconds=timeout,
            prompt="consent",
        )
        check_scopes(creds)
        save_private(token_path, creds.to_json())
        return creds
    finally:
        if flow.wrote_url and auth_url_file is not None:
            auth_url_file.unlink(missing_ok=True)


def read_header(creds: Credentials, spreadsheet_id: str) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", spreadsheet_id):
        raise ValueError("표 URL 전체가 아닌 spreadsheet_id를 입력하세요.")
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)
    try:
        metadata = service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            fields="properties(title),sheets(properties(title))",
        ).execute()
        sheets = metadata.get("sheets", [])
        if not sheets:
            raise ValueError("읽을 시트가 없습니다.")
        title = sheets[0]["properties"]["title"]
        # 시트 이름의 공백/작은따옴표를 A1 표기법에 맞게 처리합니다.
        selected_range = "'" + title.replace("'", "''") + "'!A1:C3"
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=selected_range,
        ).execute()
        return {"title": metadata["properties"]["title"], "sheet": title,
                "range": result.get("range", selected_range),
                "values": result.get("values", [])}
    finally:
        service.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--auth-url-file", type=Path)
    parser.add_argument("--reauth", action="store_true")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    if args.no_browser and args.auth_url_file is None:
        parser.error("--no-browser에는 --auth-url-file이 필요합니다.")
    if args.timeout < 1:
        parser.error("--timeout은 1초 이상이어야 합니다.")
    credential_path = configured_path("CREDENTIALS_PATH", "credentials.json")
    token_path = configured_path("TOKEN_PATH", "token.json")
    url_path = args.auth_url_file.expanduser() if args.auth_url_file else None
    if url_path and url_path.resolve() in {credential_path.resolve(), token_path.resolve()}:
        parser.error("로그인 URL 파일은 인증 JSON·토큰과 다른 경로여야 합니다.")
    try:
        creds = (load_token(token_path) if token_path.exists() and not args.reauth else
                 authenticate(credential_path, token_path, no_browser=args.no_browser,
                              auth_url_file=url_path, timeout=args.timeout))
        # 항상 공개된 Google 예제만 읽습니다. 사용자 자료를 검색하지 않습니다.
        print(json.dumps(read_header(creds, SAMPLE_ID), ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        # API 예외 원문에는 URL/인증 응답이 들어갈 수 있어 출력하지 않습니다.
        print(f"인증 또는 읽기 확인 실패 ({type(error).__name__}). "
              "파일 경로, API 활성화, 테스트 사용자, 동의 범위를 확인하세요. "
              "만료·철회된 토큰은 --reauth로 다시 인증하세요.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
