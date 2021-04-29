import requests
# 인증
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *

'''
 출금 계좌 조회 
    - 파라미터 : user_id 
    - 응답 :  게좌, 상품명, 가격 
'''
@api_view(['GET'])
def get_payment_info(request):
    try:
        uid = request.query_params.get('user_id', None)
        user = User.objects.get(user_id=uid)
        params = {'user_seq_no': user.user_seqnum}
        api_url = 'https://testapi.openbanking.or.kr/v2.0/user/me'
        headers = {'Authorization': 'Bearer {}'.format(user.access_token)}
        resp = requests.get(api_url, params=params, headers=headers)
        resp.raise_for_status()
        result = resp.json()

        product_one = UserProduct.objects.filter(user_id=user)[0].product_id
        product_price = product_one.price
        product_name = product_one.product_name

        return Response({'account': result['res_list'][0]['account_num_masked'],
                         'product_name': product_name,
                         'product_price': product_price
                         })
    except Exception as e:
        print(str(e))
        return requests.Response({'user_info': None}, status.HTTP_400_BAD_REQUEST)
