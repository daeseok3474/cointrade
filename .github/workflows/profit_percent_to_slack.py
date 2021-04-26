from numpy.lib.function_base import percentile
import pyupbit
import datetime
import pprint
import websocket, json, time, requests
import hashlib, jwt, uuid
from urllib.parse import urlencode
#from dotenv import load_dotenv, find_dotenv
from numpy import average
import os

#업비트 API키 로그인
f = open("upbit_key.txt")
lines = f.readlines()
API_KEY = lines[0].strip() #access key  
SECRET_KEY = lines[1].strip() #secret key  
f.close()
upbit = pyupbit.Upbit(API_KEY, SECRET_KEY) #class instance, object

# try:
#     import thread
# except ImportError:
#     import _thread as thread

### 기준값 목록 설정 ###

#주거래코인 설정
select_coin = "KRW-MBL" #코인 코드 표기 (KRW-BTC, KRW-XRP)

#코인 현재가격
current_price = pyupbit.get_current_price(select_coin)

#평균 매수가
avg_buy_price = upbit.get_avg_buy_price(select_coin)

#현재 보유 코인잔고
balance = upbit.get_balance(select_coin)

#현재 보유 원화잔고
krw_balance = upbit.get_balance("KRW")

#거래 여부
op_mode = True  #False = 거래중지 , True = 거래시작

#코인 보유여부
hold = False #False = 보유안함, True = 보유중

#익절 % 설정
profit_rate = 3.5

#손절 % 설정
loss_rate = -1.5

#현재시간
now = datetime.datetime.now()
now1 = now.strftime("%y.%m.%d %H:%M:%S")

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#


#변수 설정 (매수 기준가격)
# def cal_target1(select_coin):
#     recent_price = pyupbit.get_ohlcv(select_coin, "minute5") #분봉 : munute1,3,5,10,15,30,60,240, 일봉 : day, 주봉 : week, 월봉 :
#     avg_start = 1 #시작일자 1=하루전 2=이틀전
#     avg_times = 2 #평균값 몇일간
#     center_price = average(recent_price.iloc[-1-avg_start:-1-avg_start-avg_times:-1]['close']) #avg_start일자부터 avg_times일간 평균 종가 / #고가 : high, 시가 : start, 저가 : low, 종가 : close, 거래량 : volume
#     return(center_price)

# def cal_target2(select_coin):
#     recent_price = pyupbit.get_ohlcv(select_coin, "minute5") #분봉 : munute1,3,5,10,15,30,60,240, 일봉 : day, 주봉 : week, 월봉 :
#     avg_start = 1 #시작일자 1=하루전 2=이틀전
#     avg_times = 4 #평균값 몇일간
#     center_price = average(recent_price.iloc[-1-avg_start:-1-avg_start-avg_times:-1]['close']) #avg_start일자부터 avg_times일간 평균 종가 / #고가 : high, 시가 : start, 저가 : low, 종가 : close, 거래량 : volume
#     return(center_price)

# target1 = cal_target1(select_coin)
# target2 = cal_target2(select_coin)


while True:
    #주거래코인 설정
    select_coin = "KRW-ETH" #코인 코드 표기 (KRW-BTC, KRW-XRP)

    #코인 현재가격
    current_price = pyupbit.get_current_price(select_coin)

    #평균 매수가
    avg_buy_price = upbit.get_avg_buy_price(select_coin)

    #현재 보유 코인잔고
    balance = upbit.get_balance(select_coin)

    #현재 보유 원화잔고
    krw_balance = upbit.get_balance("KRW")

    #거래 여부
    op_mode = True  #False = 거래중지 , True = 거래시작

    #코인 보유여부
    hold = False #False = 보유안함, True = 보유중

    #익절 % 설정
    profit_rate = 3.5

    #손절 % 설정
    loss_rate = -1.5

    #현재시간
    now = datetime.datetime.now()
    now1 = now.strftime("%y.%m.%d %H:%M:%S")

    def cal_target1(select_coin):
        recent_price = pyupbit.get_ohlcv(select_coin, "minute5") #분봉 : munute1,3,5,10,15,30,60,240, 일봉 : day, 주봉 : week, 월봉 :
        avg_start = 1 #시작일자 1=하루전 2=이틀전
        avg_times = 10 #평균값 몇일간
        center_price = average(recent_price.iloc[-1-avg_start:-1-avg_start-avg_times:-1]['close']) #avg_start일자부터 avg_times일간 평균 종가 / #고가 : high, 시가 : start, 저가 : low, 종가 : close, 거래량 : volume
        return(center_price)

    def cal_target2(select_coin):
        recent_price = pyupbit.get_ohlcv(select_coin, "minute5") #분봉 : munute1,3,5,10,15,30,60,240, 일봉 : day, 주봉 : week, 월봉 :
        avg_start = 1 #시작일자 1=하루전 2=이틀전
        avg_times = 20 #평균값 몇일간
        center_price = average(recent_price.iloc[-1-avg_start:-1-avg_start-avg_times:-1]['close']) #avg_start일자부터 avg_times일간 평균 종가 / #고가 : high, 시가 : start, 저가 : low, 종가 : close, 거래량 : volume
        return(center_price)

    target1 = cal_target1(select_coin)
    target2 = cal_target2(select_coin)
    
    def profit_per1():
        if balance >= 0.0000000001:
            a = current_price - avg_buy_price
            b = a / avg_buy_price
            c = b * 100
            return(c)
        else:
            a = 0
            return(a)
    
    profit_per = profit_per1()
    
    if balance >= 0.0000000001:
            slacker_message3 = (f"{now1}""""
            """f"{select_coin}현재가:{current_price}""""
            """f"coin:{balance}""""
            """f"KRW:{krw_balance}""""
            """f"수익률:{profit_per}%")
    
            def post_message(token, channel, text):
                response = requests.post("https://slack.com/api/chat.postMessage",
                headers={"Authorization": "Bearer "+token},
                data={"channel": channel,"text": text}
            )

            myToken = "xoxb-1977392976102-1990420459204-ZarxVCu4xJvXWdbThGwo5aWu"

            post_message(myToken,"#coin",slacker_message3)
            
            time.sleep(600)
    
    time.sleep(0.5)