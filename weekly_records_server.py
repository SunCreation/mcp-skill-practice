"""고정된 주간 업무 기록을 읽는 MCP 서버. 보고서 판정은 하지 않습니다."""

import json
from pathlib import Path
from typing import Any

from mcp.server import MCPServer

mcp = MCPServer("weekly-records")
DATA_DIR = Path(__file__).with_name("data")
WEEK_FILES = {
    "week-one": "week-one.json",
    "week-two": "week-two.json",
}


def load_weekly_records(week: str) -> dict[str, Any]:
    """허용한 주차의 예시 파일만 읽습니다. 파일 경로를 입력받지 않습니다."""
    selected_week = week.strip().lower()
    if selected_week not in WEEK_FILES:
        raise ValueError("week는 week-one 또는 week-two를 사용하세요.")

    with (DATA_DIR / WEEK_FILES[selected_week]).open(encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        raise ValueError("주간 데이터는 records 목록이 있는 객체여야 합니다.")
    if data.get("week") != selected_week:
        raise ValueError("요청한 주차와 데이터의 week가 다릅니다.")
    return data


@mcp.tool()
def get_weekly_records(week: str) -> dict[str, Any]:
    """week-one 또는 week-two의 가상 팀 업무 기록을 읽습니다.

    반환값은 주차, 팀 이름, 기간 시작일, 보고 기준일, 업무 기록 목록입니다.
    파일을 수정하지 않으며 완료·진행·위험 판정이나 보고서 작성은 하지 않습니다.
    """
    return load_weekly_records(week)
