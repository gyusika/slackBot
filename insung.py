import ccxtpro
import asyncio
import nest_asyncio
from time import *

nest_asyncio.apply()

upbit = ccxtpro.upbit(
    {
        'apiKey': 'lawQbU9NfqWc6QWxy1EzoXx0sp89aEeI5gMQx8ky',
        'secret': 'Hx6Vodbg76ySgtX1topajJFZF5o5E95lmmznEBxY'
    }
)

upbit.options['createMarketBuyOrderRequiresPrice'] = False

binance = ccxtpro.binance(
    {
        'apiKey': 'Gf9LUIQa2J1uJEeeI90Q4qEtJGNVag2aOINGtLT3TNBdw9DqZWue3JT2a4ZmiqMk',
        'secret': '6ePSbvRSFtl1XVeR1IznZYoeLBpiWK5rb0V4diyorAH7getNOzfWZi9Gzo6Bhica'
    }
)


async def getUpbitBalance(coin):
    remain_bal = 0
    try:
        balance = await upbit.fetchBalance()
        remain_bal = balance[coin]['total']
        return remain_bal
    except:
        return 0


async def getBinanceBalance(coin):
    remain_bal = 0
    try:
        balance = await binance.fetchBalance()
        remain_bal = balance[coin]['total']
        return remain_bal
    except:
        return 0


async def main():
    exchange_rate = 1126.5  # 환율
    KR_SELL_PR = 0.038  # 김프가 높게 껴서 한국에서 팔 때
    KR_BUY_PR = 0.035  # 김프가 낮게 껴서 한국에서 살 때
    emergency_ratio = 0.2  # 여유현금 비율

    binance_price_unit = 0.0001  # 바이낸스 호가단위
    upbit_price_unit = 5  # 업비트 호가단위

    fix_quantity = 100  # 총 들고있는 코인 수량
    target_coin = 'ENJ'  # 거래하고자 하는 코인
    target_market_upbit = 'ENJ/KRW'  # 업비트의 거래하고자 하는 시장
    target_market_binance = 'ENJ/USDT'  # 바이낸스의 거래하고자 하는 시장

    position = 1  # 0:Binance에는 COIN, Upbit에는 MONEY  // 1: Binance에는 MONEY, Upbit에는 COIN


#     upbit_ticker_load = await upbit.watchTicker(target_market_upbit) #watchTicker은 websocket 방식
#     upbit_ticker = upbit_ticker_load['close']
#     binance_ticker_load = await binance.watchTicker(target_market_binance) #watchTicker은 websocket 방식
#     binance_ticker = binance_ticker_load['close']

    # fetchTicker은 서버에 요청해서 받는 방식 (빗썸은 웹소켓 구현 안돼있음)
    upbit_ticker_load = await upbit.fetchTicker(target_market_upbit)
    upbit_ticker = upbit_ticker_load['close']
    # fetchTicker은 서버에 요청해서 받는 방식 (빗썸은 웹소켓 구현 안돼있음)
    binance_ticker_load = await binance.fetchTicker(target_market_binance)
    binance_ticker = binance_ticker_load['close']
    print('업비트 현재가: {}, 바이낸스 현재가: {}'.format(upbit_ticker, binance_ticker))

    upbit_KRW_bal = await getUpbitBalance('KRW')
    upbit_coin_bal = await getUpbitBalance(target_coin)

    binance_USDT_bal = await getBinanceBalance('USDT')
    binance_coin_bal = await getBinanceBalance(target_coin)

    upbit_money = upbit_KRW_bal + upbit_coin_bal*upbit_ticker
    binance_money = (binance_USDT_bal + binance_coin_bal *
                     binance_ticker)*exchange_rate

    print('binance_money(원화환산): ', binance_money,
          '  upbit_money(원화환산): ', upbit_money)
    print('binance_target_coin: ', binance_coin_bal,
          '  upbit_target_coin: ', upbit_coin_bal)

    if(upbit_money < upbit_ticker*fix_quantity*(1+emergency_ratio) or binance_money < binance_ticker*fix_quantity*(1+emergency_ratio)):
        print("안전 현금이 마련되지 않았습니다. 프로그램을 종료합니다.")
        return
    else:
        print("양쪽 시장 다 안전 현금을 만족시킵니다.")

    while True:
        await asyncio.sleep(0.2)

#         upbit_ticker_load = await upbit.watchTicker(target_market_upbit) #watchTicker은 websocket 방식
#         upbit_ticker = upbit_ticker_load['close']
#         binance_ticker_load = await binance.watchTicker(target_market_binance) #watchTicker은 websocket 방식
#         binance_ticker = binance_ticker_load['close']
        upbit_orderbook = await upbit.watchOrderBook(target_market_upbit, 5)
        upbit_ask_wall_price = upbit_orderbook['asks'][0][0]
        upbit_bid_wall_price = upbit_orderbook['bids'][0][0]
#         print('업비트 매도벽:{}  / 업비트 매수벽:{}'.format(upbit_ask_wall_price,upbit_bid_wall_price))

        binance_orderbook = await binance.watchOrderBook(target_market_binance, 5)
        binance_ask_wall_price = binance_orderbook['asks'][0][0]
        binance_bid_wall_price = binance_orderbook['bids'][0][0]
#         print('바이낸스 매도벽:{} / 바이낸스 매수벽:{}'.format(binance_ask_wall_price,binance_bid_wall_price))

        if(position == 0):  # 업비트에서 코인 매수, 바이낸스에서 판매 해야되는 포지션(업비트에 현금있음)
            Upbit_Buy_Premium = (upbit_ask_wall_price-binance_bid_wall_price *
                                 exchange_rate)/(binance_bid_wall_price*exchange_rate)
            print('업비트 매도벽: {}, 바이낸스 매수벽: {}, 업비트 구매시 프리미엄: {}'.format(
                upbit_ask_wall_price, binance_bid_wall_price, Upbit_Buy_Premium))
            if(Upbit_Buy_Premium <= KR_BUY_PR):
                upbit_bid_price_for_market = upbit_ask_wall_price*1.1 - \
                    ((upbit_ask_wall_price*1.1) %
                     upbit_price_unit) + upbit_price_unit
                if(upbit_price_unit >= 1):
                    upbit_bid_price_for_market = int(
                        upbit_bid_price_for_market)

                binance_ask_price_for_market = binance_bid_wall_price*0.9 - \
                    ((binance_bid_wall_price*0.9) %
                     binance_price_unit) - binance_price_unit
                if(binance_price_unit >= 1):
                    binance_ask_price_for_market = int(
                        binance_ask_price_for_market)

                order_upbit = await upbit.create_limit_buy_order(target_market_upbit, fix_quantity, upbit_bid_price_for_market)
                order_binance = await binance.create_limit_sell_order(target_market_binance, fix_quantity, binance_ask_price_for_market)

                while True:
                    try:
                        resp_upbit = await upbit.fetch_order(order_upbit['id'], target_market_upbit)
                        resp_binance = await binance.fetch_order(order_binance['id'], target_market_binance)
                        if(resp_upbit['status'] == 'closed' and resp_binance['status'] == 'closed'):
                            Actual_Kimchi_Premium = (
                                resp_upbit['average']-resp_binance['average']*exchange_rate)/(resp_binance['average']*exchange_rate)
                            print('업비트 시장가 구매, {}포지션에서 {}개가 {}원에 거래되었습니다. 실거래가 김프: {}'.format(
                                resp_upbit['side'], resp_upbit['filled'], resp_upbit['average'], Actual_Kimchi_Premium))
                            print('바이낸스 시장가 판매, {}포지션에서 {}개가 {}달러에 거래되었습니다. 실거래가 김프: {}'.format(
                                resp_binance['side'], resp_binance['filled'], resp_binance['average'], Actual_Kimchi_Premium))
                            break
                    except:
                        pass

                position = 1  # 포지션 변경

        elif(position == 1):  # 업비트에서 코인 매도, 바이낸스에서 매수 해야되는 포지션(업비트에 코인있음)
            Upbit_Sell_Premium = (upbit_bid_wall_price-binance_ask_wall_price *
                                  exchange_rate)/(binance_ask_wall_price*exchange_rate)
            print('업비트 매수벽: {}, 바이낸스 매도벽: {}, 업비트 판매시 프리미엄: {}'.format(
                upbit_bid_wall_price, binance_ask_wall_price, Upbit_Sell_Premium))
            if(Upbit_Sell_Premium >= KR_SELL_PR):
                upbit_ask_price_for_market = upbit_bid_wall_price*0.9 - \
                    ((upbit_bid_wall_price*0.9) %
                     upbit_price_unit) + upbit_price_unit
                if(upbit_price_unit >= 1):
                    upbit_ask_price_for_market = int(
                        upbit_ask_price_for_market)

                binance_bid_price_for_market = binance_ask_wall_price*1.1 - \
                    ((binance_ask_wall_price*1.1) %
                     binance_price_unit) - binance_price_unit
                if(binance_price_unit >= 1):
                    binance_bid_price_for_market = int(
                        binance_bid_price_for_market)

                order_upbit = await upbit.create_limit_sell_order(target_market_upbit, fix_quantity, upbit_ask_price_for_market)
                order_binance = await binance.create_limit_buy_order(target_market_binance, fix_quantity, binance_bid_price_for_market)

                complete = 0
                while True:
                    try:
                        resp_upbit = await upbit.fetch_order(order_upbit['id'], target_market_upbit)
                        resp_binance = await binance.fetch_order(order_binance['id'], target_market_binance)
                        if(resp_upbit['status'] == 'closed' and resp_binance['status'] == 'closed'):
                            Actual_Kimchi_Premium = (
                                resp_upbit['average']-resp_binance['average']*exchange_rate)/(resp_binance['average']*exchange_rate)
                            print('업비트 시장가 판매, {}포지션에서 {}개가 {}원에 거래되었습니다. 실거래가 김프: {}'.format(
                                resp_upbit['side'], resp_upbit['filled'], resp_upbit['average'], Actual_Kimchi_Premium))
                            print('바이낸스 시장가 구매, {}포지션에서 {}개가 {}달러에 거래되었습니다. 실거래가 김프: {}'.format(
                                resp_binance['side'], resp_binance['filled'], resp_binance['average'], Actual_Kimchi_Premium))
                            break
                    except:
                        pass

                position = 0  # 포지션 변경

asyncio.get_event_loop().run_until_complete(main())
