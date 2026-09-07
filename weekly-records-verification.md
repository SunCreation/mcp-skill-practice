# 업무 기록 MCP 검증 기록

검증일: 2026-09-06. Python 3.13.13 / MCP Python SDK 2.1.1에서 수행했습니다. 데이터는 실습을 위해 만든 가상 기록이며 실제 날짜의 업무 사실이 아닙니다.

## 실행과 발견

SDK 클라이언트에서 별도 stdio 서버 프로세스를 시작했습니다. 서버 실행 명령의 형태는 다음과 같습니다.

```bash
mcp run weekly_records_server.py --transport stdio
```

호스트가 서버를 실행하는 실습에서는 이 명령을 별도 터미널에서 계속 실행해 둘 필요가 없습니다. README의 호스트 등록 경로를 사용합니다.

`tools/list`에서 `get_weekly_records` 도구 하나를 확인했습니다. `week`는 필수 문자열 입력입니다. dict 반환은 `structuredContent`의 최상위 필드로 직접 전달되었습니다.

## 실제 호출

| 입력 | 확인한 결과 |
| --- | --- |
| `{"week": "week-one"}` | 원본 JSON과 동일; 기준일 2026-09-04; TASK-101, 102, 103, 104 총 4건 |
| `{"week": "week-two"}` | 원본 JSON과 동일; 기준일 2026-09-11; TASK-201, 202, 102, 204 총 4건 |
| `{"week": " WEEK-ONE "}` | 공백·대문자 정규화 후 week-one과 동일 |
| `{"week": ""}` | MCP 오류 결과 |
| `{"week": "week-three"}` | MCP 오류 결과 |
| `{"week": "../README.md"}` | MCP 오류 결과; 허용된 주차 외의 경로를 읽지 않음 |
| `{"week": 1}` | 입력 자료형 오류 |
| `{}` | 필수 입력 누락 오류 |

정상 3건과 거절 5건을 확인했습니다. 검증 전후 데이터 파일의 SHA-256이 같아 파일 내용이 바뀌지 않았음을 확인했습니다. 각 항목의 필드 전체를 원본 JSON과 대조했으며 요약 건수만 확인한 것은 아닙니다.

SDK는 함수 내부 `ValueError`를 `isError: true`로 전달하며 상세 이유를 숨기고 일반 오류를 보여 줄 수 있습니다. 입력 제약의 상세 이유는 서버 로그에서 확인합니다. SDK의 입력 검증과 함수 내부의 허용 주차 검사는 서로 다른 단계입니다.

## Skill 검증 범위

`team-weekly-report/SKILL.md`는 Skill 형식 검사에 통과했습니다. 본문에서 실제 `references/team-rules.md`를 참조하며, 빈 참고 파일은 없습니다. 두 주차의 보고서 분류 기준은 `report-checks.md`에 있습니다.

이 검증은 **서버의 실제 MCP 응답과 Skill의 파일 형식**을 확인한 것입니다. Claude Code·OpenCode의 자동 Skill 선택, Tool Search의 문맥 절약 효과, 모델이 작성한 보고서의 정확도를 시험한 기록은 아닙니다. 학생은 자신의 호스트에서 별도로 인식과 산출물을 확인합니다.
