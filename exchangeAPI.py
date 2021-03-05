# 정부 공공데이터

# import requests
# import json
# from datetime import datetime

# currentdate = str(datetime.today().strftime('%Y-%m-%d'))
# print(currentdate)

# url = 'https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?authkey=wWklJ0hG9j35WMRKkfZlAvq3snQVcbhm&searchdate={currentdate}&data=AP01'.format(
#     currentdate=currentdate)

# res = requests.get(url)
# print(res.json())

import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


def upbit_get_usd_krw():
    url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
    exchange = requests.get(url, headers=headers).json()
    return exchange[0]['basePrice']


print(upbit_get_usd_krw())
