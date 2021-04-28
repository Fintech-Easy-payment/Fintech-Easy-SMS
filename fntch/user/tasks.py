from __future__ import absolute_import, unicode_literals
import logging
import sys
from pathlib import Path
from celery import shared_task, Celery
from .models import *
import datetime
import base64
import hashlib
import hmac
import time
import requests
import json
import os

app = Celery('fntch')
app.config_from_object('django.conf:settings', namespace='CELERY')
logger = logging.getLogger('celery')

BASE_DIR = Path(__file__).resolve().parent.parent
SECRETS_PATH = os.path.join(BASE_DIR, 'secret.json')
secrets = json.loads(open(SECRETS_PATH).read())

for key, value in secrets.items():
    setattr(sys.modules[__name__], key, value)


@shared_task
def send_sms():
    try:
        for up in UserProduct.objects.all():
            user = up.user_id
            product = up.product_id
            exr_date = up.exr_date.strftime("%Y년 %m월 %d일")
            now = datetime.datetime.today().strftime("%Y년 %m월 %d일")
            # 만료일 임박 (-7일)이면 메세지 보내기
            # before_one_week = datetime.datetime.today() - datetime.timedelta(weeks=1)
            # before_one_week = before_one_week.strftime("%Y년 %m월 %d일")
            # if exr_date == before_one_week :
            # TODO: 시간 설정
            if exr_date == now:

                payment_url = "http://localhost:3000/payment?uid=" + str(user.user_id) + "&product=" + str(
                    product.product_id)

                message1 = "안녕하세요 {}님! 이용중인 {} 만료일은 {} 입니다." \
                    .format(user.name, product.product_name, exr_date)
                message2 = "다음 링크로 간편 연장하세요! {}" \
                    .format(payment_url)

                sms.apply_async((user.phone, message1))
                sms.apply_async((user.phone, message2))
                logger.info("send_sms to" + str(user.phone))
            else:
                print("not")
    except Exception as e:
        logger.error("error >> " + str(e))
        print("send_sms error" + str(e))


@app.task
def sms(mem_phone, message):
    try:
        url = "https://sens.apigw.ntruss.com"
        uri = "/sms/v2/services/" + "NCP_SMS_SERVICE_ID" + "/messages"
        api_url = url + uri
        timestamp = str(int(time.time() * 1000))
        string_to_sign = "POST " + uri + "\n" + timestamp + "\n" + "NCP_ACCESS_KEY"
        signature = make_signature(string_to_sign)

        headers = {
            'Content-Type': "application/json; charset=UTF-8",
            'x-ncp-apigw-timestamp': timestamp,
            'x-ncp-iam-access-key': "NCP_ACCESS_KEY",
            'x-ncp-apigw-signature-v2': signature
        }

        body = {
            "type": "SMS",
            "contentType": "COMM",
            "from": "01058995384",
            "content": message,
            "messages": [{"to": mem_phone}]
        }

        body = json.dumps(body)
        response = requests.post(api_url, headers=headers, data=body)
        response.raise_for_status()
        logger.info("sms complete!!" + str(mem_phone))
    except Exception as e:
        print("sms error" + str(e))


def make_signature(string):
    try:
        secret_key = bytes("NCP_SECRET_KEY", 'UTF-8')
        string = bytes(string, 'UTF-8')
        string_hmac = hmac.new(secret_key, string, digestmod=hashlib.sha256).digest()
        string_base64 = base64.b64encode(string_hmac).decode('UTF-8')
        return string_base64
    except Exception as e:
        # logger.error(str(e) + "error >> " + str(slug))
        print("sms error")
