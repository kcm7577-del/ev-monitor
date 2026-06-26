import os
import json
import base64
import requests
from playwright.sync_api import sync_playwright

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
GH_TOKEN = os.environ["GH_TOKEN"]
REPO = os.environ["GITHUB_REPOSITORY"]

URL = "https://casper.hyundai.com/ev-guide/eco-incentive"

STATUS_FILE = "status.json"


def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        },
        timeout=30
    )
    print("Telegram:", r.status_code)
    print(r.text)

def github_headers():
    return {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github+json"
    }


def read_status():

    api = f"https://api.github.com/repos/{REPO}/contents/{STATUS_FILE}"

    r = requests.get(api, headers=github_headers())

    if r.status_code == 404:
        return None

    r.raise_for_status()

    data = r.json()

    text = base64.b64decode(data["content"]).decode()

    return json.loads(text), data["sha"]


def save_status(status, sha=None):

    api = f"https://api.github.com/repos/{REPO}/contents/{STATUS_FILE}"

    content = base64.b64encode(
        json.dumps(
            {"status": status},
            ensure_ascii=False,
            indent=2
        ).encode()
    ).decode()

    body = {
        "message": f"update status : {status}",
        "content": content
    }

    if sha:
        body["sha"] = sha

    r = requests.put(
        api,
        headers=github_headers(),
        json=body
    )

    r.raise_for_status()


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(URL)

    page.wait_for_load_state("networkidle")

    try:
        page.get_by_role("button", name="닫기").click(timeout=3000)
    except:
        pass

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

    status = page.locator(
        "div.subsidy-status-wrap span"
    ).inner_text().strip()
    print(status)
    status = page.locator(
        "div.subsidy-status-wrap span"
    ).inner_text().strip()

    print(status)

    if status == "가능":
        send(
            "🚗 칠곡군 전기차 보조금 신청 가능합니다!\n\n"
            "https://casper.hyundai.com/ev-guide/eco-incentive"
        )

    browser.close()
