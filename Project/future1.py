from binance.client import Client
import pandas as pd
import sys, os
import config as cfg
import math
from datetime import datetime, timedelta
import time
import numpy as np
import talib
from binance.helpers import round_step_size
from binance_f import RequestClient



"""# create a binance request client
def init_client():
    client = Client(api_key=cfg.getPublicKey(), api_secret=cfg.getPrivateKey())
    return client"""



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

    return qty, side, msg
