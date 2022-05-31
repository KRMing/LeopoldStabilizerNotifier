import os
import time
from datetime import datetime
import requests
import urllib
import gc
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from bs4 import BeautifulSoup

SITE_URL = "https://www.leopold.co.kr/Shop/Item.php?ItId=1512545919"
TELE_API_URL = "https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&text={2}"
DIR = r"./"
TOKEN_FILE_NAME = r"TELEGRAM_TOKEN.txt"
USER_LIST_FILE_NAME = r"USER_LIST.txt"
CHECK_INTERVAL_IN_SECONDS = 15 * 60 # 15 minutes
INTERVAL_AFTER_SENT_IN_SECONDS = 24 * 60 * 60 # one day

def send_to_telegram(token, text_to_send, user_id_list):
    parsed_text = urllib.parse.quote_plus(text_to_send)
    for chat_id in user_id_list:
        requests.get(TELE_API_URL.format(token, chat_id, parsed_text))

def check_lines(s, token, sent_flag, user_id_list):
    # get response
    try:
        site_response = s.get(SITE_URL)

        site = BeautifulSoup(site_response.content, 'html.parser')

        text = site.find('table').find_all('tr')[1].text

        if "품절" in text:
            return False

        if not sent_flag:
            text_to_send = '=' * 25 + '\n' + "막 용두 알리미\n\n\n 막 용두 재고 찼음!!!\n\n" + '=' * 25 + '\n\n' + SITE_URL + '\n'
            for _ in range(5):
                send_to_telegram(token, text_to_send, user_id_list)
            return True
    except:
        pass

    return False

if __name__ == "__main__":
    with requests.Session() as s:
        # fetch telegram user tokens
        user_id_list = []

        with open(DIR + USER_LIST_FILE_NAME, "r") as file:
            for line in file.readlines():
                user_id_list.append(line.strip())

        with open(DIR + TOKEN_FILE_NAME, "r") as file:
            token = file.readline().strip()

        sent_flag = False

        while True:
            sent_flag = check_lines(s, token, sent_flag, user_id_list)

            if sent_flag:
                time.sleep(INTERVAL_AFTER_SENT_IN_SECONDS)
            else:
                time.sleep(CHECK_INTERVAL_IN_SECONDS)
