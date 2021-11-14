import json
from config import *
from auth import *
from flask import Flask, render_template, request
from script import *


#! Flask app init
app = Flask(__name__)

#! Index page
@app.route("/", methods=["GET"])
def index():
    return render_template('index.html', TRADE_SYMBOL=TRADE_SYMBOL)

#! Webhook connection route
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "POST":
        quantityEntry = TRADE_QUANTITY  # TODO-> User entry mechanism required!

        data = json.loads(request.data)

        if data['token'] != get_token():
            return {
                "code": "error",
                "message": "Invalid token"
            }

        if data['strategy'] == "buy":
            # * Buy order structure
            print("**BUY ORDER**\n")
            close_positions = close_all_positions(client)
            buyOrder = open_position(client,market=TRADE_SYMBOL,leverage=3,order_side="BUY")

            if buyOrder:
                print("Buy Order Confirmed")
                telegram_bot_sendtext("***BUY ORDER CONFIRMED*** \n"+"`Symbol: {} Price: {}`".format(TRADE_SYMBOL, data['bar']['open']))
                return {
                    "code": "success",
                    "message": "Buy Order Executed"
                }
            else:
                print("Order Failure")
                telegram_bot_sendtext("***BUY ORDER FAILED*** \n"+"`Symbol: {} Price: {}`".format(TRADE_SYMBOL, data['bar']['open']))
                return{
                    "code": "error",
                    "message": "Buy Order Failed"
                }
        else:
            # * Sell order structure
            print("**SELL ORDER**\n")
            close_positions = close_all_positions(client)
            sellOrder = open_position(client,market=TRADE_SYMBOL,leverage=3,order_side="SELL")
            if sellOrder:
                print("Sell Order Confirmed")
                telegram_bot_sendtext("***SELL ORDER CONFIRMED*** \n"+"`Symbol: {} Price: {}`".format(TRADE_SYMBOL, data['bar']['open']))
                return {
                    "code": "success",
                    "message": "Sell Order Executed"
                }

            else:
                print("Order Failure")
                telegram_bot_sendtext("***SELL ORDER FAILED!!*** \n"+"`Symbol: {} Price: {}`".format(TRADE_SYMBOL, data['bar']['open']))
                return{
                    "code": "error",
                    "message": "Sell Order Failed"
                }

    return "**Webhook Get**"


if __name__ == '__main__':
    app.run(debug=True)
