import os
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://casper.hyundai.com/ev-guide/eco-incentive"


def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        },
        timeout=30
    )


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    context = browser.new_context()

    page = context.new_page()

    page.goto(URL)

    page.get_by_role("button", name="닫기").click()

    page.get_by_role("textbox", name="시/도 선택").click()

    page.get_by_role("listitem").filter(
        has_text="경북"
    ).click()

    page.get_by_role("textbox", name="시/군 선택").click()

    page.get_by_role("listitem").filter(
        has_text="칠곡군"
    ).click()

    page.get_by_role(
        "button",
        name="조회하기"
    ).click()

    page.wait_for_timeout(3000)
    status = ""

    if page.get_by_text("가능").count() > 0:
        status = "가능"

    elif page.get_by_text("임시중단/마감").count() > 0:
        status = "임시중단/마감"

    else:
        status = "알수없음"

    print(status)

    if status == "가능":
        send(
            "🚗 칠곡군 전기차 보조금 신청 가능합니다!\n\n"
            "https://casper.hyundai.com/ev-guide/eco-incentive"
        )

    context.close()

    browser.close()    
