"""미리 인증한 읽기 전용 토큰으로 지정한 표의 첫 시트 A1:C3만 읽습니다."""
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from google_auth_check import configured_path, load_token, read_header

mcp = MCPServer("google-sheets-reader")


@mcp.tool()
def read_sheet_header(spreadsheet_id: str) -> dict:
    """지정한 Google 표의 제목과 첫 시트 A1:C3을 읽습니다. 생성·수정하지 않습니다.

    spreadsheet_id는 표 URL의 /d/와 /edit 사이 ID입니다.
    인증이 안 되어 있으면 터미널에서 google_auth_check.py를 먼저 실행하세요.
    """
    try:
        token = load_token(configured_path("TOKEN_PATH", "token.json"))
        return read_header(token, spreadsheet_id)
    except Exception as error:
        raise ToolError(
            "Google 읽기 실패. 인증 확인 스크립트와 지정 표의 접근 권한을 확인하세요 "
            f"({type(error).__name__})."
        ) from None
