from __future__ import absolute_import, unicode_literals
import logging
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
from django.core.exceptions import ImproperlyConfigured

app = Celery('fntch')
app.config_from_object('django.conf:settings', namespace='CELERY')
logger = logging.getLogger('celery')

BASE_DIR = Path(__file__).resolve().parent.parent
secret_file = os.path.join(BASE_DIR, 'secret.json')
with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

@shared_task
def send_sms():
    try:
        for up in UserProduct.objects.all():
            user = User.objects.get(user_id = up.user_id)

            product = Product.objects.get(product_id = up.product_id)

            exr_date = up.exr_date.strftime("%Y년 %m월 %d일")

            before_one_week = up.exr_date - datetime.timedelta(weeks=1)
            before_one_week = before_one_week.strftime("%Y년 %m월 %d일")

            now = datetime.datetime.today().strftime("%Y년 %m월 %d일")
            if before_one_week == now:
                payment_url = "http://localhost:3000/payment?uid=" + str(user.user_id) + "&product=" + str(
                    product.product_id)

                message1 = "안녕하세요 {}님! 이용중인 {} 만료일은 {} 입니다." \
                    .format(user.name, product.product_name, exr_date)
                message2 = "다음 링크로 간편 연장하세요! {}" \
                    .format(payment_url)

                sms.apply_async((user.phone, message2))
                sms.apply_async((user.phone, message1))
                logger.info("send_sms to" + str(user.phone))
    except Exception as e:
        logger.error("send sms error >> " + str(e))


@app.task
def sms(mem_phone, message):
    try:
        url = "https://sens.apigw.ntruss.com"
        uri = "/sms/v2/services/" + get_secret("NCP_SMS_SERVICE_ID") + "/messages"
        api_url = url + uri
        timestamp = str(int(time.time() * 1000))
        string_to_sign = "POST " + uri + "\n" + timestamp + "\n" + get_secret("NCP_ACCESS_KEY")
        signature = make_signature(string_to_sign)

        headers = {
            'Content-Type': "application/json; charset=UTF-8",
            'x-ncp-apigw-timestamp': timestamp,
            'x-ncp-iam-access-key': get_secret("NCP_ACCESS_KEY"),
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
        logger.info("ncp sms complete!!" + str(mem_phone))
    except Exception as e:
        logger.error("ncp sms error >> " + str(e))


def make_signature(string):
    try:
        secret_key = bytes(get_secret("NCP_SECRET_KEY"), 'UTF-8')
        string = bytes(string, 'UTF-8')
        string_hmac = hmac.new(secret_key, string, digestmod=hashlib.sha256).digest()
        string_base64 = base64.b64encode(string_hmac).decode('UTF-8')
        return string_base64
    except Exception as e:
        logger.error("make signature error >> " + str(e))
