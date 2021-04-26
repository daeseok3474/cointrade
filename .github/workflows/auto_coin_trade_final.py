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

#try:
#    import thread
#except ImportError:
#    import _thread as thread

### 기준값 목록 설정 ###

#주거래코인 설정
select_coin = "KRW-ETH" #코인 코드 표기 (KRW-BTC, KRW-XRP)

#코인 현재가격
current_price = pyupbit.get_current_price(select_coin)
#def currently_price():
#    def on_message(ws, message):
#        json_data = json.loads(message) #실시간 데이터 호출
#        buy_price = json_data['trade_price']
#        print(buy_price)
#    
#    def on_error(ws, error):
#        print(error)
#
#    def on_close(ws):
#        print("### closed ###")
#
#    def on_open(ws):
#        def run(*args):
#            ws.send(json.dumps(
#                [{"ticket": "test"}, {"type": "ticker", "codes": ["KRW-ETH"]}]))
#        thread.start_new_thread(run, ())
#    
#
#    websocket.enableTrace(True)
#    ws = websocket.WebSocketApp("ws://api.upbit.com/websocket/v1",
#                                on_message=on_message,
#                                on_error=on_error,
#                                on_close=on_close)
#    ws.on_open = on_open
#    print(ws.on_open)
#    ws.run_forever()
#
#current_price = currently_price()

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
profit_rate = 2.5

#손절 % 설정
loss_rate = -0.9

#현재시간
now = datetime.datetime.now()
now1 = now.strftime("%y.%m.%d %H:%M:%S")

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

print("거래시작")

slacker_message3 = ("""거래시작
"""f"현재시간: {now1}""")

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
    headers={"Authorization": "Bearer "+token},
    data={"channel": channel,"text": text}
)

myToken = "xoxb-1977392976102-1990420459204-ZarxVCu4xJvXWdbThGwo5aWu"

post_message(myToken,"#coin",slacker_message3)

while True:
    #현재시간
    now = datetime.datetime.now()
    now1 = now.strftime("%y.%m.%d %H:%M:%S")

    #평균 매수가
    avg_buy_price = upbit.get_avg_buy_price(select_coin)

    #현재 보유 코인잔고
    balance = upbit.get_balance(select_coin)

    #현재 보유 원화잔고
    krw_balance = upbit.get_balance("KRW")

    #코인 현재가격
    current_price = pyupbit.get_current_price(select_coin)

    #변수 설정 (매수 기준가격)
    def cal_target1(select_coin):
        recent_price = pyupbit.get_ohlcv(select_coin, "minute1") #분봉 : munute1,3,5,10,15,30,60,240, 일봉 : day, 주봉 : week, 월봉 :
        avg_start = 1 #시작일자 1=하루전 2=이틀전
        avg_times = 25 #평균값 몇일간
        center_price = average(recent_price.iloc[-1-avg_start:-1-avg_start-avg_times:-1]['close']) #avg_start일자부터 avg_times일간 평균 종가 / #고가 : high, 시가 : start, 저가 : low, 종가 : close, 거래량 : volume
        return(center_price)

    def cal_target2(select_coin):
        recent_price = pyupbit.get_ohlcv(select_coin, "minute1") #분봉 : munute1,3,5,10,15,30,60,240, 일봉 : day, 주봉 : week, 월봉 :
        avg_start = 1 #시작일자 1=하루전 2=이틀전
        avg_times = 99 #평균값 몇일간
        center_price = average(recent_price.iloc[-1-avg_start:-1-avg_start-avg_times:-1]['close']) #avg_start일자부터 avg_times일간 평균 종가 / #고가 : high, 시가 : start, 저가 : low, 종가 : close, 거래량 : volume
        return(center_price)

    target1 = cal_target1(select_coin)
    target2 = cal_target2(select_coin)
    
    # def profit_per1():
    #     if balance >= 0.0000000001:
    #         a = current_price - avg_buy_price
    #         b = a / avg_buy_price
    #         c = b * 100
    #         return(c)
    #     else:
    #         a = 0
    #         return(a)
    
    profit_per = 0

    if balance >= 0.000000001:
        profit_per = ((current_price - avg_buy_price) / avg_buy_price) * 100

    print(1)                

    #매수 신호
    if op_mode is True and hold is False:
        if target1 > target2 and (current_price - target2) / target2 * 100 < 1 and (current_price - target2) / target2 * 100 > 0.5:
            print(upbit.buy_market_order(select_coin, krw_balance*0.9)) #보유한 금액의 비중만큼 시장가 매수
            hold = True
            slacker_message2 = ("""매수 주문.
            """f"현재시간: {now1}""""
            """f"매수가: {current_price} 매수금액: {krw_balance}원")
    
            def post_message(token, channel, text):
                response = requests.post("https://slack.com/api/chat.postMessage",
                headers={"Authorization": "Bearer "+token},
                data={"channel": channel,"text": text}
            )

            myToken = "xoxb-1977392976102-1990420459204-ZarxVCu4xJvXWdbThGwo5aWu"

            post_message(myToken,"#coin",slacker_message2)
    print(3)
        
    #매도 신호
    if op_mode is True and hold is True:  #거래환경 확인 (거래, 코인보유 여부)
        if profit_rate < profit_per or profit_per < loss_rate:   #매도 여부 확인 
            print(upbit.sell_market_order(select_coin, balance)) #코인 보유잔고 시장가 매도
            hold = False
            op_mode = False
            slacker_message1 = ("""매도 주문.
            """f"현재시간: {now1}""""
            """f"매도가: {current_price} 수익률: {profit_per}%")
    
            def post_message(token, channel, text):
                response = requests.post("https://slack.com/api/chat.postMessage",
                headers={"Authorization": "Bearer "+token},
                data={"channel": channel,"text": text}
            )

            myToken = "xoxb-1977392976102-1990420459204-ZarxVCu4xJvXWdbThGwo5aWu"

            post_message(myToken,"#coin",slacker_message1)

            time.sleep(1800) #매도 경우 1시간(1800초) 대기
    
            op_mode = True #time.sleep 이후 거래환경 시작
    
    print(f"현재시간: {now1} / 현재가격: {current_price} / 기준가: {target1},{target2}")   
    
    time.sleep(0.5)
