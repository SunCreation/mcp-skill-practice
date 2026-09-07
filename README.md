# MCP와 Skill 실습 자료

기본 경로는 **업무 기록 조회 MCP → 팀 주간 보고서 Skill**입니다. Google credential이나 Colab 연결 토큰은 포함하지 않습니다.

## 기본 실습 파일

| 파일 | 역할 |
| --- | --- |
| `pyproject.toml` | 기본 MCP 의존성과 Google 추가 의존성을 선언한 uv 프로젝트 설정 |
| `uv.lock` | 직접·간접 의존성의 확정 버전; uv가 생성하고 관리하는 파일 |
| `.python-version` | 실습 기본 Python 3.13 선택 |
| `weekly_records_server.py` | 선택한 주의 업무 기록을 읽는 MCP 서버 |
| `data/week-one.json`, `data/week-two.json` | 각각 업무 4건이 들어 있는 가상 팀 데이터 |
| `team-weekly-report/SKILL.md` | 팀 주간 보고서 작성에 적용할 Skill |
| `team-weekly-report/references/team-rules.md` | 완료 기준, 기한 판정, 보고서 형식 등 팀 고유 규칙 |
| `report-checks.md` | 학생이 결과를 확인할 기준; Skill에 넣지 않는 평가 자료 |
| `weekly-records-verification.md` | MCP 서버 검증 범위와 결과 |

### 1. 업무 기록 조회

압축을 푼 폴더는 uv 프로젝트로 준비되어 있습니다. `.python-version`은 Python 3.13을 선택하며, `pyproject.toml`과 `uv.lock`으로 MCP SDK 2.1.1 및 필요한 패키지를 준비합니다. Claude Code 또는 OpenCode로 이 폴더를 열고 먼저 요청합니다.

> 이 폴더를 uv로 실행할 수 있게 준비해 줘. Python과 패키지 버전도 확인하자.

<details>
<summary>수동으로 uv 환경 준비하기</summary>

uv가 없다면 [공식 설치 안내](https://docs.astral.sh/uv/getting-started/installation/)를 먼저 따릅니다. 압축을 푼 폴더에서 실행합니다.

```bash
uv sync --locked
uv run --locked python --version
uv run --locked python -c "import sys; from importlib.metadata import version; print(sys.executable); print(version('mcp'))"
```

`uv sync`는 이 프로젝트의 `.venv`를 준비하고 잠금 파일에 맞춰 패키지를 설치합니다. `--locked`는 프로젝트 설정과 잠금 파일이 어긋나면 자동으로 잠금 파일을 바꾸지 않고 알려 줍니다. `uv run`은 준비한 프로젝트 환경에서 명령을 실행하므로 가상환경 활성화가 필요하지 않습니다. 이미 프로젝트 파일이 있으므로 `uv init`을 다시 실행하지 않습니다.

</details>

그다음 MCP 연결을 요청합니다.

> 이 폴더의 업무 기록 서버를 uv로 실행하는 MCP로 연결해 줘. 첫 주 기록이 나오는지 확인하자.

서버 이름은 `weekly-records`, 도구는 `get_weekly_records`, 입력은 `{"week": "week-one"}`입니다. 반환값의 `records`에 4건이 있는지 확인합니다. 이 서버는 원래 기록만 읽습니다. ‘개발 완료’를 팀 보고서의 ‘완료’로 판단하는 일은 서버 코드에 넣지 않았습니다.

<details>
<summary>수동으로 설정하기 — 업무 기록 조회 MCP</summary>

아래는 uv로 위 환경 준비를 마친 상태입니다. `/압축을/푼/실제폴더`를 실제 절대 경로로 바꿉니다. 이미 등록된 다른 서버 설정은 유지합니다.

**Claude Code**

```bash
claude mcp add --transport stdio --scope project weekly-records -- uv --directory "/압축을/푼/실제폴더" run --locked mcp run weekly_records_server.py --transport stdio
```

**OpenCode V1** — `opencode.json` 또는 `opencode.jsonc`의 기존 `mcp` 안에 추가합니다.

```json
{
  "mcp": {
    "weekly-records": {
      "type": "local",
      "command": ["uv", "--directory", "/압축을/푼/실제폴더", "run", "--locked", "mcp", "run", "weekly_records_server.py", "--transport", "stdio"],
      "enabled": true
    }
  }
}
```

**OpenCode V2**는 위 `weekly-records` 객체를 `mcp.servers` 아래에 넣고 `enabled`를 제거합니다. `type`과 `command` 배열은 유지합니다. V2의 `disabled` 기본값은 `false`, `codemode` 기본값은 `true`입니다. [V2 공식 등록 안내](https://opencode.ai/v2/docs/mcp-servers)를 함께 확인합니다.

호스트가 설정을 다시 읽게 한 뒤 연결 상태와 호출을 확인합니다. Python 환경은 호스트가 실행한 환경과 같아야 합니다.

</details>

### 2. 실제 보고서에서 필요한 규칙 찾기

Skill 설치 전 첫 주 기록과 `team-weekly-report/references/team-rules.md`를 일반 자료로 제공해 보고서를 요청합니다. 먼저 학생이 기록과 팀 규칙을 읽고 업무의 분류를 판단한 뒤, AI의 초안과 비교합니다. 개발이 끝난 일과 배포·운영 확인까지 끝난 일, 보고 기준일과 기한이 같은 일을 구분해 봅니다.

잘못된 부분이 있다면 원본과 규칙을 근거로 수정합니다. 처음부터 정확하면 어떤 기준이 적용됐는지 확인합니다. 첫 보고서는 `first-week-report.md`, 판단 근거와 수정 이유는 `report-work-notes.md` 같은 파일에 남길 수 있습니다. 특정 주의 정답과 다음 주에도 쓸 팀 기준을 구분해 봅니다.

### 3. 규칙을 Skill로 재사용

`team-weekly-report`는 참고할 완성 예제입니다. 팀 규칙을 직접 바꿨다면 그 기준으로 자신의 Skill을 만들고 예제와 비교합니다.

> 방금 사용한 팀 보고 기준을 스킬로 만들어 줘. 다음 주에도 같은 방식으로 쓰고 싶어.

Skill을 설치할 때는 `SKILL.md` 하나만 옮기지 말고 **폴더 전체**를 복사합니다. 본문에서 사용하는 `references/team-rules.md`도 필요합니다.

<details>
<summary>수동으로 설정하기 — 팀 보고서 Skill</summary>

- Claude Code 프로젝트: `.claude/skills/team-weekly-report/`
- OpenCode 프로젝트: `.opencode/skills/team-weekly-report/`

위 폴더 안에 `SKILL.md`와 `references/team-rules.md`가 있도록 복사합니다. 두 호스트를 함께 쓴다면 OpenCode가 지원하는 `.claude/skills` 경로를 공유할 수도 있습니다. 설치 후 새 대화를 시작합니다.

Claude Code에서는 `/team-weekly-report`로 명시 호출할 수 있습니다. OpenCode에서는 “team-weekly-report 스킬로 둘째 주 보고서를 작성해 줘”라고 요청할 수 있습니다. 자연어 자동 선택을 관찰할 때에는 스킬 이름을 생략해 봅니다.

공식 안내: [Agent Skills 형식](https://agentskills.io/specification), [Claude Code Skills](https://code.claude.com/docs/en/skills), [OpenCode Skills](https://opencode.ai/docs/skills/).

</details>

새 대화에서 요청합니다.

> 둘째 주 팀 진행 보고서를 작성해 줘.

실제 Skill·팀 규칙 파일 로드, `week-two` 조회, 작성 결과를 확인합니다. **MCP 없이도** `data/week-two.json`의 로컬 파일 경로를 주면 같은 보고서를 만들 수 있습니다. Skill이 MCP 연결에 종속되지 않는다는 것을 비교할 수 있습니다. 사용한 호스트에서 로드 기록을 볼 수 없으면 관찰하지 못한 것으로 표시합니다.

`report-checks.md`를 보고 분류와 건수를 대조합니다. 둘째 주에는 배포했지만 검증을 기다리는 일과, 첫 주 이후 실제로 완료된 일이 있습니다. 첫 주 답변을 복사하는 대신 새 기록에 같은 기준을 적용해야 합니다.

### 기본 산출물

업무 조회 도구의 실제 입력·결과 한 건, 자신이 만든 `SKILL.md`와 사용한 팀 규칙, 첫째·둘째 주 Markdown 보고서, Skill 인식과 분류 결과의 관찰 기록을 남깁니다. 서버 구현을 직접 했다면 `weekly_records_server.py`와 데이터 파일도 함께 제출합니다. 인증 정보는 제출하지 않습니다.

## 프로젝트 설정과 추가 의존성

`pyproject.toml`이 설치 요구 사항의 기준이며 `uv.lock`은 그 요구 사항을 만족하는 직접·간접 패키지 버전을 기록합니다. `.python-version`의 3.13은 기본 실행 버전이고 `requires-python = ">=3.10"`은 코드가 허용하는 범위입니다. 잠금 파일은 패키지 버전을 고정하며 Python의 패치 버전까지 고정하지는 않습니다.

Google 실습에서는 `uv sync --locked --extra google`로 같은 환경에 추가 패키지를 준비합니다. Google 프로그램을 실행할 때에도 `uv run --locked --extra google ...`처럼 해당 묶음을 명시합니다. 자세한 인증 절차와 MCP 등록은 `GOOGLE_AUTH_README.md`를 따릅니다. Colab MCP는 별도 공개 프로그램이므로 교안의 `uvx` 경로를 사용하며 이 프로젝트의 기본 의존성에 넣지 않았습니다.

기존 `requirements.txt`와 `requirements-google.txt`는 이전 pip 방식의 직접 의존성 목록을 참고할 수 있도록 보관했습니다. 현재 실습은 uv 프로젝트 경로로 진행합니다. 학생이 기능을 추가해 의존성을 바꿀 때에는 AI에게 `pyproject.toml`과 `uv.lock`도 함께 갱신하도록 요청합니다. `.venv`와 캐시는 공유하지 않고 프로젝트 파일과 잠금 파일을 함께 전달합니다.
