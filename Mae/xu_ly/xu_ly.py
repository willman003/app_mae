import requests
import json
from datetime import datetime

client_key = '62bee939365a425b93c13bca9882041c'

def Lay_token_xac_thuc(client_key=client_key):
    url = "https://sapi.sendo.vn/shop/authentication"

    payload = 'Content-Type=application/x-www-form-urlencoded&Cache-Control=no-cache&grant_type=password&username=' + client_key + '&password=9397f820941f37f2d28383cc419ea34632022b54'
    headers = {
    'Authorization': 'Bearer PuAM0B2qJ_JCoaW5zpQlxuksc0PINGBFvEaRl5d3a1LWBGJ8ZJ8FX6RmDol2KsP6bo9kMKcQW-1bVXJN00SK9baDHR7lO8p3wGocK_QbSXkfm0_R3FQZUSlvfSV7VxSkMUGEcFfL4luB1MGynz1bnA0xrSan4gjYXZw1KcEIN9WGPV61CYA7xF619YfMotauQzc49T6rCfRPg-hrkRi9bvD_Wgd9XUF2r2n6yU8Au5GFbI8A4P26chvWVdEwMwvpaH4KxxHl7Y8VVaR5WeJynirsMP_xPeWbN2EYenFGK-y9GC-2XbiMpqJnBynLT0a0-im6GE1TH2rRM9_d0Uvl_Mzc8Nr_Sc4gT-9N_qvX2s4FCD2s2WALQUXV1YdA-57YS6YIRUyW6C3gdE6JZG2B06mR1zZ26IlZqn8hLfbCyHYQ6zuAnDRpP3QRLHQXf8AfkczracLm07fA6uQi9tsoDIDW2vH3PmH4xOwtS7KR1Y4kIum5UX1JmvZ7EwVns183Xy8frfXwjeAwXG2skIU4F9ZsJEZ65iuBC7fgiHcaPt57_ai5_wIugY886IQd70u0RCS-EQ',
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data = payload)
    result = json.loads(response.text)
    return result['access_token']

def Lay_danh_sach_order():
    ngay=datetime.now().date()
    today = str(ngay.year) + "/" + str(ngay.month) + "/" + str(ngay.day)
    url = "http://sapi.sendo.vn/shop/salesOrder/Merchant?frDate="+today+"&ttDate="+today+"&offset=0&limit=50"
    
    payload = {}
    headers = {
    'Authorization': 'Bearer ' + Lay_token_xac_thuc(),
    'Cache-Control': 'no-cache',
    'Postman-token': '9c32433d-dcb0-f837-a0f2-69ba8257d27b'
    }

    response = requests.request("GET", url, headers=headers, data = payload)
    result = json.loads(response.text)
    list_order = result['result']['data']
   
    return list_order

def Lay_thong_tin_chi_tiet_order(order_number):
    url = "http://sapi.sendo.vn/shop/salesorder?orderNumber=" + order_number

    payload = {}
    headers = {
    'Authorization': 'Bearer ' + Lay_token_xac_thuc(),
    }

    response = requests.request("GET", url, headers=headers, data = payload)
    result = json.loads(response.text)
    return result['result']




