# Google 인증 확인과 읽기 도구

개인 Google 계정용 실습입니다. Google 공식 Python 예제의 OAuth 흐름을 이용합니다.
인증 확인 프로그램은 공개된 Google 예제 표만 읽고, MCP 도구는 학생이 지정한 표의 첫 시트 `A1:C3`과 제목만 읽습니다.

## 준비

1. Google Cloud 프로젝트에서 Google Sheets API를 켭니다.
2. Google Auth platform에서 External / Testing으로 설정하고 자신의 이메일을 Test users에 추가합니다.
3. Data Access에서 `https://www.googleapis.com/auth/spreadsheets.readonly`를 선택합니다.
4. Desktop app 클라이언트를 만들고 다운로드한 JSON을 `~/.config/google-workspace/credentials.json`에 둡니다.
5. 다른 앱의 기존 토큰을 복사하지 않습니다. 이번 앱에서 새로 동의합니다.

저장 위치는 프로젝트 밖입니다. 경로 변경이 필요할 때만 `CREDENTIALS_PATH`, `TOKEN_PATH` 환경변수를 사용합니다. 인증 JSON과 토큰 내용은 채팅·과제·캡처에 넣지 않습니다. 토큰과 로그인 URL 파일은 POSIX에서 소유자만 읽을 수 있는 권한으로 생성합니다. Windows에서는 개인 사용자만 접근 가능한 폴더를 사용합니다.

## 먼저 터미널에서 인증 확인

실습 폴더의 uv 프로젝트를 사용합니다. `.python-version`은 Python 3.13을 선택합니다. `pyproject.toml`의 `google`은 Google API용 추가 패키지 묶음입니다.

> 이 프로젝트의 Google 실습 환경을 uv로 준비하고 첫 로그인을 도와줘.

<details>
<summary>수동으로 Google 추가 패키지 설치와 인증 실행</summary>

압축을 푼 폴더에서 실행합니다.

```bash
uv sync --locked --extra google
uv run --locked --extra google python google_auth_check.py
```

기본 MCP 환경에 Google 패키지를 더합니다. `.venv`가 없으면 uv가 만들고, 이미 있으면 필요한 상태로 맞춥니다. `uv venv`나 `uv init`을 따로 실행하지 않습니다. `--locked`는 설정과 잠금 파일이 어긋나면 알려 주며, `--extra google`은 실행할 때에도 Google 패키지가 준비되도록 합니다. 기본 실습과 같은 폴더를 사용하되 인증 파일과 토큰은 앞에서 안내한 개인 설정 폴더에 둡니다.

</details>

기본 브라우저에서 계정·앱 이름·읽기 권한을 확인하고 동의합니다. 완료하면 `token.json`을 개인 설정 폴더에 저장하고, 공개 예제 표의 제목과 `A1:C3` 결과를 출력합니다. 로그인 URL과 토큰은 출력하지 않습니다. Chrome으로 진행하려면 Chrome을 기본 브라우저로 지정합니다. OAuth 자체가 Chrome 전용인 것은 아닙니다.

인증이 만료되거나 철회되면 `--reauth`를 붙여 다시 실행합니다. External/Testing 앱의 이 권한은 갱신 토큰이 7일 후 만료됩니다. 읽기 전용 scope도 사용자가 접근할 수 있는 모든 Google 표에 대한 범위이며, OAuth 권한 자체가 표 하나로 제한되는 것은 아닙니다.

### 자동으로 브라우저를 열 수 없는 환경

```bash
uv run --locked --extra google python google_auth_check.py --no-browser --auth-url-file ~/.config/google-workspace/login-url.txt
```

프로그램을 켜 둔 채 같은 컴퓨터의 브라우저에서 해당 파일의 URL을 엽니다. 로그인 URL은 비공개 파일로만 전달하고 채팅이나 로그에 복사하지 않습니다. 기본 대기 시간은 300초이며 `--timeout`으로 변경합니다. 인증 성공 또는 실패 뒤 URL 파일을 삭제합니다. 이미 유효한 토큰이 있으면 URL 파일 없이 읽기 확인만 수행합니다. 새 로그인 화면이 필요하면 `--reauth`를 함께 사용합니다.

## MCP 연결은 에이전트에게 요청

인증 확인을 먼저 마친 다음 Claude Code 또는 OpenCode에서 이 폴더를 열고 요청합니다.

> 이 Google Sheets 읽기 도구를 uv로 실행하는 MCP로 연결해 줘. 인증 파일 내용은 출력하지 마.

<details>
<summary>수동으로 설정하기 — Google Sheets 읽기 MCP</summary>

먼저 `uv sync --locked --extra google`로 의존성을 준비하고 `google_auth_check.py`에서 최초 인증을 마칩니다. 아래 `/내/실습폴더`는 압축을 푼 실제 절대 경로로 바꿉니다. Claude Code 명령의 경로를 감싼 큰따옴표는 공백이 있는 폴더 이름도 하나의 경로로 전달하도록 유지합니다.

**Claude Code**

```bash
claude mcp add --transport stdio --scope project google-sheets-reader -- uv --directory "/내/실습폴더" run --locked --extra google mcp run google_sheet_reader.py --transport stdio
```

**OpenCode V1** — 앞에서 확인한 설치 버전이 V1이면 기존 `mcp` 객체에 추가합니다.

```json
{
  "mcp": {
    "google-sheets-reader": {
      "type": "local",
      "command": ["uv", "--directory", "/내/실습폴더", "run", "--locked", "--extra", "google", "mcp", "run", "google_sheet_reader.py", "--transport", "stdio"],
      "enabled": true
    }
  }
}
```

**OpenCode V2** — 설치 버전이 V2라면 위 V1 객체 대신 다음처럼 `mcp.servers` 아래에 서버를 추가합니다. 기존 다른 서버 설정은 함께 유지합니다. V2에는 `enabled` 필드가 없으며, `disabled`를 생략하면 기본값 `false`로 연결합니다. `codemode`도 생략하면 기본값 `true`이므로 앞에서 배운 Code Mode 경로로 도구를 제공합니다. [OpenCode V2 MCP 설정](https://opencode.ai/v2/docs/mcp-servers)

```json
{
  "mcp": {
    "servers": {
      "google-sheets-reader": {
        "type": "local",
        "command": ["uv", "--directory", "/내/실습폴더", "run", "--locked", "--extra", "google", "mcp", "run", "google_sheet_reader.py", "--transport", "stdio"]
      }
    }
  }
}
```

서버를 실행하는 명령은 같고, 호스트가 설정을 읽는 위치와 켜기·끄기 항목이 달라진 것입니다. Google 사용자 OAuth는 앞에서 실행한 Python 프로그램이 처리합니다. 이 로컬 MCP 설정에 원격 MCP용 OAuth 항목을 추가하는 단계는 아닙니다.

기본 인증 파일 위치는 `~/.config/google-workspace/`입니다. 위치를 바꿨다면 최초 인증 프로그램에는 `CREDENTIALS_PATH`와 `TOKEN_PATH`를 지정하고, MCP 서버에는 `TOKEN_PATH`를 지정합니다. Claude Code는 서버 설정의 `env`, OpenCode는 `environment`에 넣습니다. 아래는 환경변수 부분의 예시이며 전체 서버 설정은 아닙니다.

```json
{
  "TOKEN_PATH": "/내/개인설정/google/token.json"
}
```

이 변수 이름은 첨부한 실습 코드 기준입니다. 다른 MCP에서는 해당 도구의 문서를 따릅니다. 인증 파일 내용을 설정에 복사하지 않습니다.

</details>

에이전트가 이 README와 `google_sheet_reader.py`를 읽고 현재 호스트에 맞게 등록하도록 합니다. 학생은 변경한 설정 위치, 서버 파일, 연결 상태를 확인합니다. 인증 파일을 다른 폴더에 보관했다면 내용 대신 경로만 알려줍니다.

구현 참고: 최초 인증 프로그램은 `CREDENTIALS_PATH`와 `TOKEN_PATH`를 지원하고, MCP는 `TOKEN_PATH`의 기존 토큰만 읽습니다. 기본 위치는 앞서 설명한 개인 설정 폴더입니다. 두 프로그램이 같은 토큰을 쓰는지 에이전트가 확인하도록 합니다. MCP 내부에서는 로그인 화면을 열지 않습니다.

> 이 연습용 표의 제목과 처음 세 줄을 읽어 줘. 화면과 결과를 비교하자.

표 URL을 함께 주고 호출된 `read_sheet_header`의 입력과 실제 결과를 확인합니다. 이 함수는 수정·검색 도구를 제공하지 않습니다.

## 코드를 읽는 순서

- `google_auth_check.py`: `SCOPES`는 읽기 권한, `authenticate()`는 최초 동의, `load_token()`은 저장된 인증 재사용입니다. `PrivateURLFlow`는 표준 OAuth 처리를 바꾸지 않고 생성된 URL을 비공개 파일에 보관하는 부분만 추가합니다.
- `read_header()`: 지정한 표의 제목과 첫 시트 이름을 받은 뒤 `A1:C3`을 읽습니다.
- `google_sheet_reader.py`: `@mcp.tool()`이 위 읽기 함수를 에이전트가 호출할 도구로 공개합니다.

## 실제 확인 기록 — 2026-09-06

신규 개인 계정용 OAuth 앱에서 인증을 완료한 뒤, `google_auth_check.py`와 MCP SDK의 stdio 클라이언트로 공개 Google 예제 표를 실제로 읽었습니다. 제목은 `Example Spreadsheet`, 첫 시트는 `Class Data`이며, 반환 범위는 `'Class Data'!A1:C3`이었습니다. MCP의 `read_sheet_header` 호출은 오류 없이 완료했습니다.

인증 JSON과 토큰 파일의 권한 `0600`, 저장된 scope가 `spreadsheets.readonly` 하나임을 확인했습니다. 인증 정보 원문은 검증 기록에 포함하지 않았습니다. 이는 **SDK 클라이언트의 직접 호출 검증**이며 Claude Code/OpenCode 모델이 도구를 선택한 기록은 아닙니다. 학생은 자신의 호스트에서 실제 호출 입력·결과도 확인합니다.

이 환경에서는 인증 반환 탭에 `ERR_BLOCKED_BY_CLIENT`가 보였지만 인증 프로그램은 종료 코드 0과 실제 API 조회 결과를 반환했습니다. 같은 화면 오류가 보이면 브라우저 메시지만으로 성공·실패를 단정하지 말고 프로그램 종료 상태와 실제 읽기 결과를 함께 확인합니다.

근거: [Google Sheets Python 시작 예제](https://developers.google.com/workspace/sheets/api/quickstart/python), [개인 계정용 동의 화면 설정](https://developers.google.com/workspace/guides/configure-oauth-consent), [Sheets 권한 범위](https://developers.google.com/workspace/sheets/api/scopes).
