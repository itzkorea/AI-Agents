# Inspiration Agent (영감 靈感)

매일 오전 9시(KST)에 영감을 주는 주제·문장·단어·뉴스를 이메일로 보내는 에이전트.

## 동작 방식

```
GitHub Actions (매일 00:00 UTC = 09:00 KST)
        │
        ▼
inspiration_agent.py
        │  Claude API 호출 (웹 검색 도구 포함)
        ▼
오늘의 영감 리포트 생성 (주제 / 문장 / 단어 / 뉴스)
        │
        ▼
SMTP로 HTML 메일 발송
```

## 설정 (5분)

### 1. GitHub 리포지토리 생성 후 이 파일들을 푸시

```bash
git init && git add . && git commit -m "inspiration agent"
git remote add origin https://github.com/<계정>/inspiration-agent.git
git push -u origin main
```

### 2. Gmail 앱 비밀번호 발급 (Gmail 사용 시)

1. Google 계정 → 보안 → 2단계 인증 활성화
2. https://myaccount.google.com/apppasswords 에서 앱 비밀번호 생성
3. 16자리 비밀번호를 복사

### 3. GitHub Secrets 등록

리포지토리 → Settings → Secrets and variables → Actions → New repository secret

| 이름 | 값 |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API 키 (console.anthropic.com) |
| `SMTP_USER` | 발신 Gmail 주소 |
| `SMTP_PASSWORD` | 위에서 발급한 앱 비밀번호 |
| `MAIL_TO` | 수신 주소 (쉼표로 여러 명 가능) |

Gmail이 아닌 경우 워크플로 env에 `SMTP_HOST`, `SMTP_PORT`를 추가하면 됩니다.

### 4. 테스트

리포지토리 → Actions → "Daily Inspiration Report" → **Run workflow** 버튼으로 즉시 실행해 메일이 오는지 확인.

## 커스터마이징

- **시간 변경**: `daily-inspiration.yml`의 cron 수정 (UTC 기준. 예: 오전 7시 KST → `0 22 * * *`)
- **내용 변경**: `inspiration_agent.py`의 `SYSTEM_PROMPT` 수정 — 섹션 추가/삭제, 분야 지정, 분량 조절 모두 여기서
- **뉴스 검색량**: `max_uses` 값 조정 (검색 횟수 = 비용에 영향)

## 비용

- GitHub Actions: 퍼블릭 리포 무료 / 프라이빗도 월 2,000분 무료 (하루 1~2분 사용)
- Claude API: 웹 검색 포함 1회 실행당 대략 $0.02~0.05 수준
