from datetime import datetime
import time
import MetaTrader5 as mt5
import sys
from enum import Enum
import importlib

calc = importlib.import_module("Trading Tool")


# FIXME     python -m PyQt5.uic.pyuic -x [FILENAME].ui -o [FILENAME].py
#    Important script for converting .ui to .py


# TODO
#   Create an error message for when order send calls fail
#   Create a function that sets a TP corresponding to a specific risk : reward
#   Create a Auto BE function
#   Make ' or " consistent
#   Look into the enumerate function auto starting at 1 rather than the count + 1 in get_positions and get_orders
#   Think about if we want modify_order() to use the inbuilt modify call or if we want to 'modify'
#       by cancelling the order and 're-ordering'. This would allow a modification of volume too
#   Check which requests need deviation and/or type_time and type_filling
#   Getter doesnt want to return 3dp, will have to do it in place and check if 2dp is okay
#   Check if setting TP to 0 will leave the TP empty. If not, what does
#   Maybe add 'doc strings' and 'func strings'


class TradeSession:

    def __init__(self, magic):
        mt5.initialize()
        self.magic = magic
        self.symbol = "GBPJPY"

    class Orders(Enum):
        BUY = 0
        SELL = 1
        BUY_LIMIT = 2
        SELL_LIMIT = 3
        BUY_STOP = 4
        SELL_STOP = 5
        BUY_STOP_LIMIT = 6
        SELL_STOP_LIMIT = 7
        CLOSE_BY = 8

    class OpenPrice:
        def __init__(self):
            self._opn = float

        @property
        def price(self):
            return self._opn

        @price.setter
        def price(self, value):
            self._opn = value

    class StopLoss:
        def __init__(self):
            self._sl = float

        @property
        def sl(self):
            return self._sl

        @sl.setter
        def sl(self, value):
            self._sl = value

    class TakeProfit:
        def __init__(self):
            self._tp = float

        @property
        def tp(self):
            return self._tp

        @tp.setter
        def tp(self, value):
            self._tp = value

    class Deviation:
        def __init__(self):
            self._dev = float

        @property
        def dev(self):
            return self._dev

        @dev.setter
        def dev(self, value):
            self._dev = value

    class Risk:
        def __init__(self):
            self._risk = float

        @property
        def risk(self):
            return self._risk

        @risk.setter
        def risk(self, value):
            self._risk = value

    class Volume:
        def __init__(self):
            self._vol = float

        @property
        def volume(self):
            return self._vol

        @volume.setter
        def volume(self, value):
            self._vol = value

    class OrderType:
        def __init__(self):
            self._orderType = float

        @property
        def order_type(self):
            return self._orderType

        @order_type.setter
        def order_type(self, value):
            self._orderType = value

    @staticmethod
    def get_info(symbol):
        return mt5.symbol_info(symbol)

    def get_positions(self):
        for count, order in enumerate(mt5.positions_get()):
            print(f"   Position {count + 1} - {self.Orders(mt5.TradePosition(order).type).name}")
            print(f"Ticket      : {mt5.TradePosition(order).ticket}")
            print(f"Volume      : {mt5.TradePosition(order).volume}")
            print(f"Open Price  : {mt5.TradePosition(order).price_open}")
            print(f"TP          : {mt5.TradePosition(order).tp}")
            print(f"SL          : {mt5.TradePosition(order).sl}")
            print("----------------------------")

    def get_orders(self):
        for count, order in enumerate(mt5.orders_get()):
            print(f"Position {count + 1} - {self.Orders(mt5.TradeOrder(order).type).name}")
            print(f"Ticket      : {mt5.TradeOrder(order).ticket}")
            print(f"Volume      : {mt5.TradeOrder(order).volume_initial}")
            print(f"Open Price  : {mt5.TradeOrder(order).price_open}")
            print(f"TP          : {mt5.TradeOrder(order).tp}")
            print(f"SL          : {mt5.TradeOrder(order).sl}")
            print("----------------------------")

    def check_order(self, action, symbol, open_price, lot):
        # FIXME handle if Sl and TP hasn't been provided yet
        if action == mt5.ORDER_TYPE_BUY:
            price = mt5.symbol_info_tick(symbol).ask
            request = {
                "action":       mt5.TRADE_ACTION_DEAL,
                "symbol":       symbol,
                "volume":       lot,
                "type":         action,
                "price":        price,
                "sl":           self.StopLoss.sl,
                "tp":           self.TakeProfit.tp,
                "deviation":    self.Deviation.dev,
                "type_time":    mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
                "magic":        self.magic,
                "comment":      "python check buy order",

            }
        elif action == mt5.ORDER_TYPE_SELL:
            price = mt5.symbol_info_tick(symbol).bid
            request = {
                "action":       mt5.TRADE_ACTION_DEAL,
                "symbol":       symbol,
                "volume":       lot,
                "type":         action,
                "price":        price,
                "sl":           self.StopLoss.sl,
                "tp":           self.TakeProfit.tp,
                "deviation":    self.Deviation.dev,
                "type_time":    mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
                "magic":        self.magic,
                "comment":      "python check sell order",

            }

        print(f"Action              :   {self.Orders(Trader.OrderType.order_type).name} {symbol}")
        print(f"Volume              :   {lot} @ {self.Risk.risk}%")
        print(f"Leverage            :   {leverage}")
        print(f"Required Margin     :   {round((lot * 100000) / leverage, 1)}")
        print(f"Desired Price       :   {open_price:.3f} ∓ {self.Deviation.dev}")
        print(f"Current Price       :   {price:.3f}")
        if request['type'] == 0:
            print(f"Stop Loss           :   {self.StopLoss.sl:.3f}")
            print(f"Take Profit         :   {self.TakeProfit.tp:.3f}")
        elif request['type'] == 1:
            print(f"Stop Loss           :   {self.StopLoss.sl:.3f}")
            print(f"Take Profit         :   {self.TakeProfit.tp:.3f}")




    def open_trade(self, action, symbol, lot):

        if action == "BUY":
            trade_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask
            request = {
                "action":       mt5.TRADE_ACTION_DEAL,
                "symbol":       symbol,
                "volume":       lot,
                "type":         trade_type,
                "price":        price,
                "sl":           self.StopLoss.sl,
                "tp":           self.TakeProfit.tp,
                "deviation":    self.Deviation.dev,
                "type_time":    mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
                "magic":        self.magic,
                "comment":      "python script long",

            }
        elif action == "SELL":
            trade_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
            request = {
                "action":       mt5.TRADE_ACTION_DEAL,
                "symbol":       symbol,
                "volume":       lot,
                "type":         trade_type,
                "price":        price,
                "sl":           self.StopLoss.sl,
                "tp":           self.TakeProfit.tp,
                "deviation":    self.Deviation.dev,
                "type_time":    mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
                "magic":        self.magic,
                "comment":      "python script short",

            }

        result = mt5.order_send(request)
        self.order_error_check(result)

    def place_order(self, action, symbol, open_price, lot):
        point = mt5.symbol_info(symbol).point
        price = open_price

        if action == "BUY LIMIT":
            trade_type = mt5.ORDER_TYPE_BUY_LIMIT

            request = {
                "action":       mt5.TRADE_ACTION_PENDING,
                "symbol":       symbol,
                "volume":       lot,
                "type":         trade_type,
                "price":        price,
                "sl":           self.StopLoss.sl,
                "tp":           self.StopLoss.sl,
                "type_time":    mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
                "magic":        self.magic,
                "comment":      "python buy limit",

            }

        elif action == "SELL LIMIT":
            trade_type = mt5.ORDER_TYPE_SELL_LIMIT

            request = {
                "action":       mt5.TRADE_ACTION_PENDING,
                "symbol":       symbol,
                "volume":       lot,
                "type":         trade_type,
                "price":        price,
                "sl":           self.StopLoss.sl,
                "tp":           self.TakeProfit.tp,
                "type_time":    mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
                "magic":        self.magic,
                "comment":      "python sell limit",

            }

        elif action == "BUY STOP":
            trade_type = mt5.ORDER_TYPE_BUY_STOP

            request = {
                "action":       mt5.TRADE_ACTION_PENDING,
                "symbol":       symbol,
                "volume":       lot,
                "type":         trade_type,
                "price":        price,
                "sl":           self.StopLoss.sl,
                "tp":           self.TakeProfit.tp,
                "type_time":    mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
                "magic":        self.magic,
                "comment":      "python buy stop",

            }
        elif action == "SELL STOP":
            trade_type = mt5.ORDER_TYPE_SELL_STOP

            request = {
                "action":       mt5.TRADE_ACTION_PENDING,
                "symbol":       symbol,
                "volume":       lot,
                "type":         trade_type,
                "price":        price,
                "sl":           self.StopLoss.sl,
                "tp":           self.TakeProfit.tp,
                "type_time":    mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
                "magic":        self.magic,
                "comment":      "python sell stop",

            }
        result = mt5.order_send(request)

    def modify_order(self, ticket, open_price):
        mt5.initialize()
        order = mt5.orders_get(ticket=ticket)[0]
        symbol = mt5.TradeOrder(order).symbol

        request = {
            "action":       mt5.TRADE_ACTION_MODIFY,
            "order":        ticket,
            "price":        open_price,
            "sl":           self.StopLoss.sl,
            "tp":           self.TakeProfit.tp,
            "type_time":    mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
            "magic":        self.magic,
            "comment":      f"python modify {symbol}"
        }
        result = mt5.order_send(request)

    def close_all(self):
        while mt5.positions_total():
            pos = mt5.positions_get()[0]  # FIXME Im sure this could be better. Try not to use indexing
            position_id = mt5.TradePosition(pos).ticket
            symbol = mt5.TradePosition(pos).symbol

            order = mt5.TradePosition(pos).type
            if order == 0:  # Buy
                price = mt5.symbol_info_tick(symbol).bid
                # TODO Check if deviation even needs to be in this request
                request = {
                    "action":       mt5.TRADE_ACTION_DEAL,
                    "symbol":       symbol,
                    "position":     position_id,
                    "volume":       mt5.TradePosition(pos).volume,
                    "type":         mt5.ORDER_TYPE_SELL,
                    "price":        price,
                    "deviation":    0,
                    "type_time":    mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_RETURN,
                    "magic":        self.magic,
                    "comment":      f"python close all {symbol}",
                }
            elif order == 1:  # Sell
                price = mt5.symbol_info_tick(symbol).ask
                request = {
                    "action":       mt5.TRADE_ACTION_DEAL,
                    "symbol":       symbol,
                    "position":     position_id,
                    "volume":       mt5.TradePosition(pos).volume,
                    "type":         mt5.ORDER_TYPE_BUY,
                    "price":        price,
                    "deviation":    0,
                    "type_time":    mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_RETURN,
                    "magic":        self.magic,
                    "comment":      f"python close all {symbol}",
                }
            result = mt5.order_send(request)
        print("No Open Positions")

    def cancel_all(self):
        # TODO Do I need these nested ifs, just have while orders_get(), send close requests
        while mt5.orders_get():
            pos = mt5.orders_get()[0]  # FIXME Again check if this can be done better without [0]
            position_id = mt5.TradeOrder(pos).ticket

            order = mt5.TradeOrder(pos).type
            if order == 2:  # Buy limit
                request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order":  position_id,
                    "magic":  self.magic
                }
            elif order == 3:  # Sell limit
                request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order":  position_id,
                    "magic":  self.magic
                }
            elif order == 4:  # Buy stop
                request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order":  position_id,
                    "magic":  self.magic
                }
            elif order == 5:  # Sell Stop
                request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order":  position_id,
                    "magic":  self.magic
                }
            result = mt5.order_send(request)
        print("No Pending Orders")

    def close_half(self, ticket=1):
        if ticket == 1:
            # If no ticket specified, close half of all positions
            for pos in mt5.positions_get():
                position_id = mt5.TradePosition(pos).ticket
                symbol = mt5.TradePosition(pos).symbol
                sell_vol = round(mt5.TradePosition(pos).volume / 2, 2)
                order = mt5.TradePosition(pos).type
                # TODO check if deviation needs to be in these requests
                if order == 0:
                    price = mt5.symbol_info_tick(symbol).bid
                    request = {
                        "action":       mt5.TRADE_ACTION_DEAL,
                        "symbol":       symbol,
                        "position":     position_id,
                        "volume":       sell_vol,
                        "type":         mt5.ORDER_TYPE_SELL,
                        "price":        price,
                        "deviation":    0,
                        "type_time":    mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                        "magic":        self.magic,
                        "comment":      f"python close half {symbol}"
                    }
                if order == 1:
                    price = mt5.symbol_info_tick(symbol).ask
                    request = {
                        "action":       mt5.TRADE_ACTION_DEAL,
                        "symbol":       symbol,
                        "position":     position_id,
                        "volume":       sell_vol,
                        "type":         mt5.ORDER_TYPE_BUY,
                        "price":        price,
                        "deviation":    0,
                        "type_time":    mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                        "magic":        self.magic,
                        "comment":      f"python close half {symbol}"
                    }
                result = mt5.order_send(request)
        else:
            for pos in mt5.positions_get(ticket=ticket):
                position_id = mt5.TradePosition(pos).ticket
                symbol = mt5.TradePosition(pos).symbol
                sell_vol = round(mt5.TradePosition(pos).volume / 2, 2)
                order = mt5.TradePosition(pos).type

                if order == 0:
                    price = mt5.symbol_info_tick(symbol).bid
                    request = {
                        "action":       mt5.TRADE_ACTION_DEAL,
                        "symbol":       symbol,
                        "position":     position_id,
                        "volume":       sell_vol,
                        "type":         mt5.ORDER_TYPE_SELL,
                        "price":        price,
                        "deviation":    0,
                        "type_time":    mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                        "magic":        self.magic,
                        "comment":      f"python close half {symbol}"
                    }
                if order == 1:
                    price = mt5.symbol_info_tick(symbol).ask
                    request = {
                        "action":       mt5.TRADE_ACTION_DEAL,
                        "symbol":       symbol,
                        "position":     position_id,
                        "volume":       sell_vol,
                        "type":         mt5.ORDER_TYPE_BUY,
                        "price":        price,
                        "deviation":    0,
                        "type_time":    mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                        "magic":        self.magic,
                        "comment":      f"python close half {symbol}"
                    }
                result = mt5.order_send(request)

    def close_custom_pct(self, percent_close, ticket=1):
        if ticket == 1:
            # If no ticket specified, close half of all positions
            for pos in mt5.positions_get():
                position_id = mt5.TradePosition(pos).ticket
                symbol = mt5.TradePosition(pos).symbol
                sell_vol = round(
                    mt5.TradePosition(pos).volume - ((mt5.TradePosition(pos).volume / 100) * percent_close), 2)
                order = mt5.TradePosition(pos).type

                if order == 0:
                    price = mt5.symbol_info_tick(symbol).bid
                    request = {
                        "action":       mt5.TRADE_ACTION_DEAL,
                        "symbol":       symbol,
                        "position":     position_id,
                        "volume":       sell_vol,
                        "type":         mt5.ORDER_TYPE_SELL,
                        "price":        price,
                        "deviation":    0,
                        "type_time":    mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                        "magic":        self.magic,
                        "comment":      f"python close half {symbol}"
                    }
                if order == 1:
                    price = mt5.symbol_info_tick(symbol).ask
                    request = {
                        "action":       mt5.TRADE_ACTION_DEAL,
                        "symbol":       symbol,
                        "position":     position_id,
                        "volume":       sell_vol,
                        "type":         mt5.ORDER_TYPE_BUY,
                        "price":        price,
                        "deviation":    0,
                        "type_time":    mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                        "magic":        self.magic,
                        "comment":      f"python close half {symbol}"
                    }
                result = mt5.order_send(request)
        else:
            for pos in mt5.positions_get(ticket=ticket):
                position_id = mt5.TradePosition(pos).ticket
                symbol = mt5.TradePosition(pos).symbol
                sell_vol = round(mt5.TradePosition(pos).volume / 2, 2)
                order = mt5.TradePosition(pos).type

                if order == 0:
                    price = mt5.symbol_info_tick(symbol).bid
                    request = {
                        "action":       mt5.TRADE_ACTION_DEAL,
                        "symbol":       symbol,
                        "position":     position_id,
                        "volume":       sell_vol,
                        "type":         mt5.ORDER_TYPE_SELL,
                        "price":        price,
                        "deviation":    0,
                        "type_time":    mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                        "magic":        self.magic,
                        "comment":      f"python close half {symbol}"
                    }
                if order == 1:
                    price = mt5.symbol_info_tick(symbol).ask
                    request = {
                        "action":       mt5.TRADE_ACTION_DEAL,
                        "symbol":       symbol,
                        "position":     position_id,
                        "volume":       sell_vol,
                        "type":         mt5.ORDER_TYPE_BUY,
                        "price":        price,
                        "deviation":    0,
                        "type_time":    mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                        "magic":        self.magic,
                        "comment":      f"python close half {symbol}"
                    }
                result = mt5.order_send(request)

    def close_custom_volume(self, vol, ticket=1):
        if ticket == 1:
            # If no ticket specified, close half of all positions
            for pos in mt5.positions_get():
                position_id = mt5.TradePosition(pos).ticket
                symbol = mt5.TradePosition(pos).symbol
                sell_vol = round(vol, 2)
                order = mt5.TradePosition(pos).type

                if order == 0:
                    price = mt5.symbol_info_tick(symbol).bid
                    request = {
                        "action":       mt5.TRADE_ACTION_DEAL,
                        "symbol":       symbol,
                        "position":     position_id,
                        "volume":       sell_vol,
                        "type":         mt5.ORDER_TYPE_SELL,
                        "price":        price,
                        "deviation":    0,
                        "type_time":    mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                        "magic":        self.magic,
                        "comment":      f"python close half {symbol}"
                    }
                if order == 1:
                    price = mt5.symbol_info_tick(symbol).ask
                    request = {
                        "action":       mt5.TRADE_ACTION_DEAL,
                        "symbol":       symbol,
                        "position":     position_id,
                        "volume":       sell_vol,
                        "type":         mt5.ORDER_TYPE_BUY,
                        "price":        price,
                        "deviation":    0,
                        "type_time":    mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                        "magic":        self.magic,
                        "comment":      f"python close half {symbol}"
                    }
                result = mt5.order_send(request)
        else:
            for pos in mt5.positions_get(ticket=ticket):
                position_id = mt5.TradePosition(pos).ticket
                symbol = mt5.TradePosition(pos).symbol
                sell_vol = round(mt5.TradePosition(pos).volume / 2, 2)
                order = mt5.TradePosition(pos).type

                if order == 0:
                    price = mt5.symbol_info_tick(symbol).bid
                    request = {
                        "action":       mt5.TRADE_ACTION_DEAL,
                        "symbol":       symbol,
                        "position":     position_id,
                        "volume":       sell_vol,
                        "type":         mt5.ORDER_TYPE_SELL,
                        "price":        price,
                        "deviation":    0,
                        "type_time":    mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                        "magic":        self.magic,
                        "comment":      f"python close half {symbol}"
                    }
                if order == 1:
                    price = mt5.symbol_info_tick(symbol).ask
                    request = {
                        "action":       mt5.TRADE_ACTION_DEAL,
                        "symbol":       symbol,
                        "position":     position_id,
                        "volume":       sell_vol,
                        "type":         mt5.ORDER_TYPE_BUY,
                        "price":        price,
                        "deviation":    0,
                        "type_time":    mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_RETURN,
                        "magic":        self.magic,
                        "comment":      f"python close half {symbol}"
                    }
                result = mt5.order_send(request)

    def half_risk(self, ticket=1):
        # TODO Probably remove the ticket implementation
        if ticket == 1:
            for pos in mt5.positions_get():
                position_id = mt5.TradePosition(pos).ticket
                symbol = mt5.TradePosition(pos).symbol
                tp = mt5.TradePosition(pos).tp
                sl = mt5.TradePosition(pos).sl
                order = mt5.TradePosition(pos).type
                price = mt5.TradePosition(pos).price_open

                if order == 0:  # Buy
                    diff = round(price - sl, 3)
                    request = {
                        "action":   mt5.TRADE_ACTION_SLTP,
                        "symbol":   symbol,
                        "position": position_id,
                        "sl":       round(sl + (diff / 2), 3),
                        "tp":       tp,
                        "magic":    self.magic,
                        "comment":  f"python half risk {symbol}"
                    }
                if order == 1:  # Sell
                    diff = round(sl - price, 3)
                    request = {
                        "action":   mt5.TRADE_ACTION_SLTP,
                        "symbol":   symbol,
                        "position": position_id,
                        "sl":       round(sl - (diff / 2), 3),
                        "tp":       tp,
                        "magic":    self.magic,
                        "comment":  f"python half risk {symbol}"
                    }

            else:
                for pos in mt5.positions_get(ticket=ticket):
                    position_id = ticket
                    symbol = mt5.TradePosition(pos).symbol
                    tp = mt5.TradePosition(pos).tp
                    sl = mt5.TradePosition(pos).sl
                    order = mt5.TradePosition(pos).type
                    price = mt5.TradePosition(pos).price_open

                    if order == 0:  # Buy
                        diff = round(price - sl, 3)
                        request = {
                            "action":   mt5.TRADE_ACTION_SLTP,
                            "symbol":   symbol,
                            "position": position_id,
                            "sl":       round(sl + (diff / 2), 3),
                            "tp":       tp,
                            "magic":    self.magic,
                            "comment":  f"python half risk {symbol}"
                        }
                    if order == 1:  # Sell
                        diff = round(sl - price, 3)
                        request = {
                            "action":   mt5.TRADE_ACTION_SLTP,
                            "symbol":   symbol,
                            "position": position_id,
                            "sl":       round(sl - (diff / 2), 3),
                            "tp":       tp,
                            "magic":    self.magic,
                            "comment":  f"python half risk {symbol}"
                        }
            result = mt5.order_send(request)

    def runner2(self):
        # Automatically closes 75% of position, sets SL to open price + 20 points and tp to local high/low
        # TODO Double check the TP levels are being calculated correctly
        for pos in mt5.positions_get():
            position_id = mt5.TradePosition(pos).ticket
            symbol = mt5.TradePosition(pos).symbol
            order = mt5.TradePosition(pos).type
            point = mt5.symbol_info(symbol).point
            tp = mt5.TradePosition(pos).tp
            price = mt5.TradePosition(pos).price_open
            bid = mt5.symbol_info_tick(symbol).bid
            ask = mt5.symbol_info_tick(symbol).ask
            current_price = mt5.TradePosition(pos).price_current
            pct_close = 75
            sl_points = 50
            tp_points = 500

            if order == 0:  # Buy
                new_sl = round(price + 20 * point, 3)
                if current_price < new_sl:
                    print("Desired SL is under current price")
                    sys.exit(0)
                else:
                    self.close_custom_pct(pct_close, ticket=position_id)
                    request = {
                        "action":   mt5.TRADE_ACTION_SLTP,
                        "symbol":   symbol,
                        "position": position_id,
                        "sl":       new_sl,
                        "tp":       round(ask + tp_points * point, 3),
                        "magic":    self.magic,
                        "comment":  f"python runner {symbol}"
                    }
            if order == 1:  # Sell
                new_sl = round(price - sl_points * point, 3)
                if current_price > new_sl:
                    print("Desired SL is over current price")
                    sys.exit(0)
                else:
                    self.close_custom_pct(pct_close, ticket=position_id)
                    request = {
                        "action":   mt5.TRADE_ACTION_SLTP,
                        "symbol":   symbol,
                        "position": position_id,
                        "sl":       new_sl,
                        "tp":       round(bid - (tp_points * point), 3),
                        "magic":    self.magic,
                        "comment":  f"python runner {symbol}"
                    }

            try:
                result = mt5.order_send(request)
            except UnboundLocalError:
                print(f"Desired SL      : {new_sl}")
                print(f"Current Price   : {mt5.TradePosition(pos).price_current}")

    def order_error_check(self, result):
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order_send failed.  Retcode :   {result.retcode}")
            result_dict = result._asdict()
            for field in result_dict.keys():
                print(f"{field}  -   {result_dict[field]}")
                if field == "request":
                    traderequest_dict = result_dict[field]._asdict()
                    for item in traderequest_dict:
                        print(f"Trade request: {item}   -   {traderequest_dict[item]}")
        print("Order_send complete")


def runner(self, percent_close, sl_points, tp_points, ticket=1):
    if ticket == 1:
        for pos in mt5.positions_get():
            position_id = mt5.TradePosition(pos).ticket
            symbol = mt5.TradePosition(pos).symbol
            order = mt5.TradePosition(pos).type
            point = mt5.symbol_info(symbol).point
            tp = mt5.TradePosition(pos).tp
            price = mt5.TradePosition(pos).price_open

            if order == 0:  # Buy
                new_sl = round(price + sl_points * point, 3)
                if mt5.TradePosition(pos).price_current < new_sl:
                    print("Desired SL is under current price")
                    sys.exit(0)
                else:
                    self.close_custom_pct(percent_close, ticket=position_id)
                    request = {
                        "action":   mt5.TRADE_ACTION_SLTP,
                        "symbol":   symbol,
                        "position": position_id,
                        "sl":       new_sl,
                        "tp":       round(tp + tp_points * point, 3),
                        "magic":    self.magic,
                        "comment":  f"python runner {symbol}"
                    }
            if order == 1:  # Sell
                new_sl = round(price - sl_points * point, 3)
                if mt5.TradePosition(pos).price_current > new_sl:
                    print("Desired SL is over current price")
                    mt5.shutdown()
                    sys.exit(0)
                else:
                    self.close_custom_pct(percent_close, ticket=position_id)
                    request = {
                        "action":   mt5.TRADE_ACTION_SLTP,
                        "symbol":   symbol,
                        "position": position_id,
                        "sl":       new_sl,
                        "tp":       round(tp - (tp_points * point), 3),
                        "magic":    self.magic,
                        "comment":  f"python runner {symbol}"
                    }

        else:
            for pos in mt5.positions_get(ticket=ticket):
                position_id = ticket
                symbol = mt5.TradePosition(pos).symbol
                order = mt5.TradePosition(pos).type
                point = mt5.symbol_info(symbol).point
                tp = mt5.TradePosition(pos).tp
                price = mt5.TradePosition(pos).price_open

                if order == 0:  # Buy
                    new_sl = round(price + sl_points * point, 3)
                    if mt5.TradePosition(pos).price_current < new_sl:
                        print("Desired SL is under current price")
                        sys.exit(0)
                    else:
                        self.close_custom_pct(percent_close, ticket=position_id)
                        request = {
                            "action":   mt5.TRADE_ACTION_SLTP,
                            "symbol":   symbol,
                            "position": position_id,
                            "sl":       new_sl,
                            "tp":       round(tp + tp_points * point, 3),
                            "magic":    self.magic,
                            "comment":  f"python runner {symbol}"
                        }
                if order == 1:  # Sell
                    new_sl = round(price - sl_points * point, 3)
                    if mt5.TradePosition(pos).price_current > new_sl:
                        print("Desired SL is over current price")
                        mt5.shutdown()
                        sys.exit(0)
                    else:
                        self.close_custom_pct(percent_close, ticket=position_id)
                        request = {
                            "action":   mt5.TRADE_ACTION_SLTP,
                            "symbol":   symbol,
                            "position": position_id,
                            "sl":       new_sl,
                            "tp":       round(tp - (tp_points * point), 3),
                            "magic":    self.magic,
                            "comment":  f"python runner {symbol}"
                        }
        try:
            result = mt5.order_send(request)
        except UnboundLocalError:
            print(f"Desired SL      : {new_sl}")
            print(f"Current Price   : {mt5.TradePosition(pos).price_current}")


Trader = TradeSession(916848650)

mt5.initialize()

balance = mt5.account_info()._asdict()['balance']
leverage = mt5.account_info()._asdict()['leverage']

demo = calc.TradingTool(balance=balance, leverage=leverage)

# buy 134.150
# Trader.StopLoss.sl = 133.950
# Trader.TakeProfit.tp = 134.350
# Trader.Deviation.dev = 1
# Trader.OpenPrice.price = 134.000
# Trader.OrderType.order_type = mt5.ORDER_TYPE_BUY
# Trader.Risk.risk = 1.0

# lot = demo.position_size(Trader.OpenPrice.price, Trader.StopLoss.sl, Trader.Risk.risk)

# Trader.open_trade('SELL', 'GBPJPY', lot, sl, 133.800, 5)
# Trader.check_order("BUY", 'GBPJPY', Trader.OpenPrice.price, lot)
# Trader.close_all()
# Trader.runner(75, 5, 500)

# print(Trader.Orders(Trader.OrderType.order_type).name)