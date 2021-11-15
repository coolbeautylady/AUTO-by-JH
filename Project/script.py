import requests, pprint, requests, time
from config import *
from binance.client import Client
from binance.enums import *
from binance.streams import BinanceSocketManager
from twisted.internet import reactor

"""
          .-.         .--''-.
        .'   '.     /'       `.
        '.     '. ,'          |
     o    '.o   ,'        _.-'
      \.--./'. /.:. :._:.'
     .'    '._-': ': ': ': ':
    :(#) (#) :  ': ': ': ': ':>-
     ' ____ .'_.:' :' :' :' :'
      '\__/'/ | | :' :' :'
            \  \ \
            '  ' '      The Bzzman.
"""


#! Client init
client = Client(API_KEY, SECRET_KEY)

currentPrice = {'error' : False}

#! Global variables for trading purposes
TRADE_SYMBOL = 'BTCUSDT' # enter a symbol like: SOLBUSD or ETHUSDT
TRADE_QUANTITY = 1  # enter your amount     #! Be careful! You have to give a value larger than 'MIN_NOTIONAL'  

#! Live coin price
def live_message(msg):
    if msg['e'] != 'error':
        currentPrice['price'] = msg['p']
    else:
        currentPrice['error'] = True


#! Telegram Notification
def telegram_bot_sendtext(bot_message):
    bot_token = BOT_TOKEN
    bot_chatID = BOT_CHATID
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + \
                '&parse_mode=Markdown&text=' + bot_message

    requests.get(send_text)


#! Limit Buy Order
def limitBuyOrder(symbol, quantity, price):
    try:
        print("**Sending Limit Buy Order**")
        order = client.order_limit_buy(
            symbol=symbol,
            quantity=quantity,
            price=price
        )
        pprint.pprint(order)

    except Exception as e:
        print("Exception occured: {}".format(e))
        return False

    return True


#! Limit Sell Order
def limitSellOrder(symbol, quantity, price):
    try:
        print("**Sending Limit Sell Order**")
        order = client.order_limit_sell(
            symbol=symbol,
            quantity=quantity,
            price=price
        )
        pprint.pprint(order)

    except Exception as e:
        print("Exception occured: {}".format(e))
        return False

    return True


#! Market Buy Order
def marketBuyOrder(symbol, quantity):
    try:
        print("**Sending Market Buy Order**")
        order = client.order_market_buy(
            symbol=symbol,
            quantity=quantity
        )
        pprint.pprint(order)

    except Exception as e:
        print("Exception occured: {}".format(e))
        return False
    
    return True


#! Market Sell Order
def marketSellOrder(symbol, quantity):
    try:
        print("**Sending Market Sell Order**")
        order = client.order_market_sell(
            symbol=symbol,
            quantity=quantity
        )
        pprint.pprint(order)

    except Exception as e:
        print("Exception occured: {}".format(e))
        return False
    
    return True


#! Web Socket for live prices
def WebSocketManager(client):
    #* Live coin prices via Binance Socket Manager
    bsm = BinanceSocketManager(client=client, user_timeout=60)
    conn_key = bsm.start_trade_socket(TRADE_SYMBOL, live_message)
    bsm.start()

    #* Terminating WebSocket after 3 secs
    time.sleep(3)
    bsm.stop_socket(conn_key=conn_key)
    reactor.stop()





# --------new_functions--------#


def get_all_positons(client):
    positions = client.futures_position_information()
    return positions



# close all opened position
def close_all_positions(client):
    positions = get_all_positons(client)
    for position in positions:
        _market = position['symbol']
        _qty = float(position['positionAmt'])
        if int(_qty) != 0:
            _side = "BUY"
            if _qty > 0.0:
                _side = "SELL"

            if _qty < 0.0:
                _qty = _qty * -1

            _qty = str(_qty)

            execute_order(client, _market=_market, _qty=_qty, _side=_side)



# Execute an order, this can open and close a trade
def execute_order(
    client,
    _market,
    _type="MARKET",
    _side="BUY",
    _position_side="BOTH",
    _qty=1.0,
):
    client.futures_create_order(
        symbol=_market,
        type=_type,
        side=_side,
        positionSide=_position_side,
        quantity=str(_qty),
    )


# Init the market we want to trade. First we change leverage type
# then we change margin type
def initialise_futures(client, _market, _leverage=1, _margin_type="ISOLATED"):
    try:
        client.futures_change_leverage(symbol=_market, leverage=_leverage)
        client.futures_change_margin_type(symbol=_market,
                                          marginType=_margin_type)
    except Exception as e:
        if "No need to change margin type" in str(e):
            return
        msg = "Adjust margin/leaverage: " + str(e)
        raise Exception(msg)



# Get futures balances. We are interested in USDT by default as this is what we use as margin.
def get_futures_balance(client, _asset="USDT"):
    balances = client.futures_account_balance()
    asset_balance = 0
    for balance in balances:
        if balance['asset'] == _asset:
            asset_balance = balance['balance']
            break
    return asset_balance




# change leverage
def calculate_position(client, _market, _leverage=1):
    usdt = get_futures_balance(client, _asset="USDT")
    quantity = float(usdt['free']) * 0.35
    return quantity



# get the current market price
def get_market_price(client, _market):
    price = client.futures_mark_price(symbol=_market)
    price = float(price['markPrice'])
    return price




def open_position(
    client,
    market="BTCUSDT",
    leverage=3,
    order_side="BUY",
    stop_side="SELL",
):
    initialise_futures(client, _market=market, _leverage=leverage)
    #blockPrint() 일단 지움
    qty = calculate_position(client, market, _leverage=leverage)
    #enablePrint() 일단 지웠음
    execute_order(client, _market=market, _side=order_side, _qty=qty)
