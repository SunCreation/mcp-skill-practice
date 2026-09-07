# Google 읽기 MCP 실제 호출 — 2026-09-06

신규 개인용 OAuth 앱으로 인증한 뒤 `google_auth_check.py`에서 공개 Google 예제 표 조회를 확인했습니다. 이어서 동일 토큰으로 MCP SDK Client → stdio → `mcp run google_sheet_reader.py` → `read_sheet_header`를 실제 호출했습니다.

- 발견된 도구: `read_sheet_header` 1개.
- 입력: Google 공식 공개 예제 표 ID `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`.
- 결과: 오류 없음, 제목 `Example Spreadsheet`, 시트 `Class Data`, 범위 `'Class Data'!A1:C3`.
- 첫 행: `Student Name`, `Gender`, `Class Level`.
- 인증 JSON과 토큰 파일: 모두 POSIX 권한 `0600`. 저장된 scope는 `https://www.googleapis.com/auth/spreadsheets.readonly` 하나.
- 인증 정보 원문이나 개인 표 데이터는 검증 기록에 넣지 않았습니다.

위 Google 검증도 Claude Code/OpenCode 모델을 경유한 호출 기록은 아닙니다. OAuth 반환 탭에 `ERR_BLOCKED_BY_CLIENT`가 나타났지만 인증 확인 프로그램은 종료 코드 0과 API 조회 결과를 반환했고, 뒤이은 실제 MCP 읽기도 성공했습니다. 반환 탭의 표시와 프로그램·API 실행 결과를 구분해 기록합니다.
