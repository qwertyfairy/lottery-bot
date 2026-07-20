import os
import sys
from typing import Optional
import requests
from dotenv import load_dotenv

import auth
import lotto645
import win720
import notification
import time


def _normalize_webhook(webhook_url: Optional[str]) -> Optional[str]:
    if webhook_url and webhook_url.startswith("YOUR_"):
        return None
    return webhook_url


def _load_accounts():
    load_dotenv(override=True)
    account_specs = [
        {
            "label": "하람쥐💛",
            "env_suffix": "",
        },
        {
            "label": "규람쥐❤️",
            "env_suffix": "_KYU",
        },
    ]
    accounts = []

    for spec in account_specs:
        suffix = spec["env_suffix"]
        username = os.environ.get(f'USERNAME{suffix}')
        password = os.environ.get(f'PASSWORD{suffix}')
        count = os.environ.get(f'COUNT{suffix}')
        slack_webhook_url = _normalize_webhook(os.environ.get(f'SLACK_WEBHOOK_URL{suffix}'))
        discord_webhook_url = _normalize_webhook(os.environ.get(f'DISCORD_WEBHOOK_URL{suffix}'))
        telegram_bot_token = _normalize_webhook(os.environ.get(f'TELEGRAM_BOT_TOKEN{suffix}'))

        if not username or not password:
            continue

        webhook_url = slack_webhook_url or discord_webhook_url
        accounts.append({
            "label": spec["label"],
            "username": username,
            "password": password,
            "count": int(count) if count else None,
            "webhook_url": webhook_url,
            "telegram_bot_token": telegram_bot_token,
        })

    return accounts


def _setup_and_login(account: dict):
    username = account["username"]
    password = account["password"]
    webhook_url = account["webhook_url"]

    auth_ctrl = auth.AuthController()
    auth_ctrl.login(username, password)

    return auth_ctrl, username, webhook_url

def buy_lotto645(authCtrl: auth.AuthController, cnt: int, mode: str):
    lotto = lotto645.Lotto645()
    _mode = lotto645.Lotto645Mode[mode.upper()]
    response = lotto.buy_lotto645(authCtrl, cnt, _mode)
    response['balance'] = authCtrl.get_user_balance()
    return response

def check_winning_lotto645(authCtrl: auth.AuthController) -> dict:
    lotto = lotto645.Lotto645()
    item = lotto.check_winning(authCtrl)
    item['balance'] = authCtrl.get_user_balance()
    return item

def buy_win720(authCtrl: auth.AuthController, username: str):
    pension = win720.Win720()
    response = pension.buy_Win720(authCtrl, username)
    response['balance'] = authCtrl.get_user_balance()
    return response

def check_winning_win720(authCtrl: auth.AuthController) -> dict:
    pension = win720.Win720()
    item = pension.check_winning(authCtrl)
    item['balance'] = authCtrl.get_user_balance()
    return item

def send_message(mode: int, lottery_type: int, response: dict, webhook_url: str, account_label: str):
    notify = notification.Notification()

    if mode == 0:
        if lottery_type == 0:
            notify.send_lotto_winning_message(response, webhook_url, account_label)
        else:
            notify.send_win720_winning_message(response, webhook_url, account_label)
    elif mode == 1: 
        if lottery_type == 0:
            notify.send_lotto_buying_message(response, webhook_url, account_label)
        else:
            notify.send_win720_buying_message(response, webhook_url, account_label)

def _for_each_account(task_label: str, action, fail_only_if_all: bool):
    accounts = _load_accounts()
    failures = 0
    for index, account in enumerate(accounts):
        try:
            action(account)
        except requests.RequestException as error:
            failures += 1
            notification.Notification().send_failure_message(
                account["webhook_url"], account["label"], task_label, error)

        if index < len(accounts) - 1:
            time.sleep(10)

    # 구매는 전 계정 실패일 때만 실패 처리(다음날 재시도 시 이중 구매 방지),
    # 조회는 한 계정이라도 실패하면 실패 처리(재조회는 무해)
    if failures and (not fail_only_if_all or failures == len(accounts)):
        sys.exit(1)

def _buy_lotto_for(account):
    count = account["count"]
    if count is None:
        raise ValueError(f"{account['label']} 계정의 COUNT 설정이 필요합니다.")

    auth_ctrl, _, webhook_url = _setup_and_login(account)
    response = buy_lotto645(auth_ctrl, count, "AUTO")
    send_message(1, 0, response=response, webhook_url=webhook_url, account_label=account["label"])

def _check_lotto_for(account):
    auth_ctrl, _, webhook_url = _setup_and_login(account)
    response = check_winning_lotto645(auth_ctrl)
    send_message(0, 0, response=response, webhook_url=webhook_url, account_label=account["label"])

def _buy_win720_for(account):
    auth_ctrl, username, webhook_url = _setup_and_login(account)
    response = buy_win720(auth_ctrl, username)
    send_message(1, 1, response=response, webhook_url=webhook_url, account_label=account["label"])

def _check_win720_for(account):
    auth_ctrl, _, webhook_url = _setup_and_login(account)
    response = check_winning_win720(auth_ctrl)
    send_message(0, 1, response=response, webhook_url=webhook_url, account_label=account["label"])

_COMMANDS = {
    "buy": ("로또 구매", _buy_lotto_for, True),
    "buy_lotto": ("로또 구매", _buy_lotto_for, True),
    "check": ("로또 당첨 확인", _check_lotto_for, False),
    "check_lotto": ("로또 당첨 확인", _check_lotto_for, False),
    "buy_win720": ("연금복권 구매", _buy_win720_for, True),
    "check_win720": ("연금복권 당첨 확인", _check_win720_for, False),
}

def run():
    if len(sys.argv) < 2 or sys.argv[1] not in _COMMANDS:
        print("Usage: python controller.py [buy|check|buy_lotto|check_lotto|buy_win720|check_win720]")
        return

    task_label, action, fail_only_if_all = _COMMANDS[sys.argv[1]]
    _for_each_account(task_label, action, fail_only_if_all)
  

if __name__ == "__main__":
    run()
