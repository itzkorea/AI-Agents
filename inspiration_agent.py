"""
Inspiration Agent (영감 靈感)
매일 오전 9시(KST)에 영감을 주는 주제·문장·단어·뉴스를 이메일로 보고하는 에이전트.

환경 변수:
  ANTHROPIC_API_KEY  : Anthropic API 키
  SMTP_HOST          : SMTP 서버 (기본: smtp.gmail.com)
  SMTP_PORT          : SMTP 포트 (기본: 587)
  SMTP_USER          : 발신 계정 (예: yourname@gmail.com)
  SMTP_PASSWORD      : 앱 비밀번호 (Gmail은 2단계 인증 후 앱 비밀번호 발급)
  MAIL_TO            : 수신자 (쉼표로 복수 지정 가능)
"""

import os
import smtplib
import sys
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import anthropic

KST = timezone(timedelta(hours=9))
TODAY = datetime.now(KST).strftime("%Y년 %m월 %d일 (%a)")

SYSTEM_PROMPT = """당신은 '영감(靈感) 큐레이터'입니다.
매일 아침 독자에게 지적 자극과 창조적 영감을 주는 리포트를 작성합니다.
독자는 소프트웨어 프로토타이핑과 연구를 병행하는 창작자입니다.

반드시 아래 4개 섹션을 포함한 HTML 본문(<body> 내부 내용만)을 작성하세요.
마크다운 백틱이나 <html>, <head>, <body> 태그 없이 순수 HTML 조각만 출력합니다.

1. 오늘의 주제 (하나의 큰 질문 또는 개념 — 2~3문단의 짧은 에세이)
2. 오늘의 문장 (동서양 고전·과학자·예술가의 명언 1개 + 원문/출처 + 짧은 해설)
3. 오늘의 단어 (한자어 또는 외국어 단어 1개 — 어원, 의미의 층위, 오늘 이 단어를 고른 이유)
4. 오늘의 뉴스 (웹 검색으로 찾은 최근 48시간 이내의 과학·기술·문화 뉴스 2~3건 — 각각 한 줄 요약 + 왜 영감이 되는지 한 줄 + 출처 링크)

스타일 규칙:
- 전체 분량은 이메일 한 화면에서 읽기 좋게 (한국어 기준 800~1200자)
- 인라인 CSS만 사용 (이메일 클라이언트 호환)
- 색상: 제목 #1a1a2e, 강조 #c0392b, 본문 #333, 배경 없음
- 섹션 제목은 <h2>, 뉴스 링크는 <a href> 사용
- 매일 다른 분야(철학/과학/예술/역사/언어)를 순환하며 신선함 유지
"""


def generate_report() -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 4}],
        messages=[
            {
                "role": "user",
                "content": (
                    f"오늘은 {TODAY}입니다. "
                    "웹 검색으로 최신 과학·기술·문화 뉴스를 찾은 뒤, "
                    "오늘의 영감 리포트를 HTML로 작성해 주세요."
                ),
            }
        ],
    )

    html = "".join(
        block.text for block in message.content if block.type == "text"
    ).strip()

    # 혹시 모를 마크다운 펜스 제거
    if html.startswith("```"):
        html = html.split("```")[1]
        if html.startswith("html"):
            html = html[4:]
        html = html.strip()

    if not html:
        raise RuntimeError("Claude가 빈 응답을 반환했습니다.")
    return html


def build_email(html_body: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"☀️ 오늘의 영감(靈感) — {TODAY}"
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["MAIL_TO"]

    wrapper = f"""
    <div style="max-width:640px;margin:0 auto;font-family:'Apple SD Gothic Neo',
                'Malgun Gothic',sans-serif;line-height:1.7;color:#333;padding:16px;">
      <p style="color:#888;font-size:13px;margin-bottom:24px;">
        {TODAY} · Inspiration Agent
      </p>
      {html_body}
      <hr style="border:none;border-top:1px solid #eee;margin-top:32px;">
      <p style="color:#aaa;font-size:12px;">
        이 리포트는 Claude API로 자동 생성되었습니다.
      </p>
    </div>
    """
    msg.attach(MIMEText(wrapper, "html", "utf-8"))
    return msg


def send_email(msg: MIMEMultipart) -> None:
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    recipients = [r.strip() for r in os.environ["MAIL_TO"].split(",")]

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(user, recipients, msg.as_string())


def main() -> None:
    print(f"[{TODAY}] 영감 리포트 생성 중...")
    html = generate_report()
    print("리포트 생성 완료. 메일 발송 중...")
    send_email(build_email(html))
    print("발송 완료 ✅")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"오류 발생: {e}", file=sys.stderr)
        sys.exit(1)
