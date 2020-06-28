import importlib
from enum import Enum
import MetaTrader5 as mt5
import os
from datetime import date

calc = importlib.import_module("Trading Tool")


# FIXME     python -m PyQt5.uic.pyuic -x [FILENAME].ui -o [FILENAME].py
#    Important script for converting .ui to .py


# TODO
#   We need a get_tickets function that returns the tickets of all open orders and all pending orders
#   Think about if we want modify_order() to use the inbuilt modify call or if we want to 'modify'
#       by cancelling the order and 're-ordering'. This would allow a modification of volume too
#   Check which requests need deviation and/or type_time and type_filling
#       Close and modify do not require symbol
#   Make the functions lead to a GUI pop rather than a console print
#   Implement the GTC feature where you can alter the contract fill time
#   Double check the TP levels are being calculated correctly in runner
#   Think about moving the position size calculator from Trading Tool.py to spooksFX
#   Reorder everything in all files to make more sense
#   Change everything to use the self.symbol so it is attached to the class
#   Make get_pos and got_orders a gui popup rather than console print
#   Make all functions that do some sort of opening / closing to have the error popup
#   To act on a specific order, have a drop down or some menu to select in-GUI which order by number?
#   Go through and refactor a lot of code
#   Think about 'auto' functions. E.G. Automatic runner at TP, automatic BE at TP
#   Maybe a reverse position function

class TradeSession:

    def __init__(self, magic, symbol):
        mt5.initialize()
        self.magic = magic
        self.symbol = symbol
        self.no_orders = mt5.orders_total()
        self.balance = mt5.account_info()._asdict()['balance']
        self.leverage = mt5.account_info()._asdict()['leverage']

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
        """Returns all of the required information for the given symbol"""
        return mt5.symbol_info(symbol)

    def get_positions(self):
        """Returns open positions"""
        for count, order in enumerate(mt5.positions_get(), 1):
            pip_diff = abs((mt5.TradePosition(order).price_open - mt5.TradePosition(order).sl) * 100)
            max_loss = round(
                (pip_diff * (mt5.TradePosition(order).volume * (0.01 / mt5.TradePosition(order).sl))) * 100000, 2)
            current_risk = round((max_loss / self.balance) * 100, 2)
            print(f"   Position {count} - {self.Orders(mt5.TradePosition(order).type).name}")
            print(f"Ticket      : {mt5.TradePosition(order).ticket}")
            print(f"Volume      : {mt5.TradePosition(order).volume} @ {current_risk}% Risk")
            print(f"Open Price  : {mt5.TradePosition(order).price_open:.3f}")
            print(f"TP          : {mt5.TradePosition(order).tp:.3f}")
            print(f"SL          : {mt5.TradePosition(order).sl:.3f}")
            print("----------------------------")

    def get_orders(self):
        """Returns pending orders"""
        for count, order in enumerate(mt5.orders_get(), 1):
            print(f"Position {count} - {self.Orders(mt5.TradeOrder(order).type).name}")
            print(f"Ticket      : {mt5.TradeOrder(order).ticket}")
            print(f"Volume      : {mt5.TradeOrder(order).volume_initial} @ {self.Risk.risk}% Risk")
            print(f"Open Price  : {mt5.TradeOrder(order).price_open:.3f}")
            print(f"TP          : {mt5.TradeOrder(order).tp:.3f}")
            print(f"SL          : {mt5.TradeOrder(order).sl:.3f}")
            print("----------------------------")

    def check_order(self, action, symbol, open_price, lot):
        """Returns a rundown of the desired order. Allows checking before execution"""
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

        print(f"Action              :   {self.Orders(self.OrderType.order_type).name} {symbol}")
        print(f"Volume              :   {lot} @ {self.Risk.risk}%")
        print(f"Leverage            :   {self.leverage}")
        print(f"Required Margin     :   {round((lot * 100000) / self.leverage, 1)}")
        print(f"Desired Price       :   {open_price:.3f} ∓ {self.Deviation.dev}")
        print(f"Current Price       :   {price:.3f}")
        if request['type'] == 0:
            print(f"Stop Loss           :   {self.StopLoss.sl:.3f}")
            print(f"Take Profit         :   {self.TakeProfit.tp:.3f}")
        elif request['type'] == 1:
            print(f"Stop Loss           :   {self.StopLoss.sl:.3f}")
            print(f"Take Profit         :   {self.TakeProfit.tp:.3f}")

    def open_trade(self, action, symbol, lot):
        """Returns an order request and checks its validity. For instant execution of a trade"""
        mt5.initialize()
        if not all(isinstance(i, float) for i in [self.TakeProfit.tp, self.Deviation.dev]):
            return -1
        if action == mt5.ORDER_TYPE_BUY:
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
                "deviation":    int(self.Deviation.dev),
                "type_time":    mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
                "magic":        self.magic,
                "comment":      "python script long",

            }
        elif action == mt5.ORDER_TYPE_SELL:
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
                "deviation":    int(self.Deviation.dev),
                "type_time":    mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_RETURN,
                "magic":        self.magic,
                "comment":      "python script short",

            }
        result = mt5.order_send(request)
        return self.order_error_check(result)

    def place_order(self, action, symbol, open_price, lot, expiration):
        """Returns an order request and checks its validity. Places a pending order"""
        price = open_price
        if action == mt5.ORDER_TYPE_BUY_LIMIT:
            trade_type = mt5.ORDER_TYPE_BUY_LIMIT

        elif action == mt5.ORDER_TYPE_SELL_LIMIT:
            trade_type = mt5.ORDER_TYPE_SELL_LIMIT

        elif action == mt5.ORDER_TYPE_BUY_STOP:
            trade_type = mt5.ORDER_TYPE_BUY_STOP

        elif action == mt5.ORDER_TYPE_SELL_STOP:
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
            "datetime":     expiration,
            "type_filling": mt5.ORDER_FILLING_RETURN,
            "magic":        self.magic,
            "comment":      f"python {self.Orders(trade_type).name}",
        }
        result = mt5.order_send(request)
        return self.order_error_check(result)

    def modify_order(self, ticket, open_price):
        """Modifies a currently pending order"""
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

    def modify_order2(self, ticket):
        # This will delete the current order and re-order using new criteria
        mt5.initialize()
        pass

    def close_all(self):
        """Close all currently open positions, regardless of symbol and order type"""
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
        """Cancels all pending orders regardless of symbol and order type"""
        while mt5.orders_get():
            pos = mt5.orders_get()[0]  # FIXME Again check if this can be done better without [0]
            position_id = mt5.TradeOrder(pos).ticket
            request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order":  position_id,
                "magic":  self.magic
            }
            # order = mt5.TradeOrder(pos).type
            # if order == 2:  # Buy limit
            #     request = {
            #         "action": mt5.TRADE_ACTION_REMOVE,
            #         "order":  position_id,
            #         "magic":  self.magic
            #     }
            # elif order == 3:  # Sell limit
            #     request = {
            #         "action": mt5.TRADE_ACTION_REMOVE,
            #         "order":  position_id,
            #         "magic":  self.magic
            #     }
            # elif order == 4:  # Buy stop
            #     request = {
            #         "action": mt5.TRADE_ACTION_REMOVE,
            #         "order":  position_id,
            #         "magic":  self.magic
            #     }
            # elif order == 5:  # Sell Stop
            #     request = {
            #         "action": mt5.TRADE_ACTION_REMOVE,
            #         "order":  position_id,
            #         "magic":  self.magic
            #     }

            result = mt5.order_send(request)
        print("No Pending Orders")

    def close_half(self, ticket=1):
        """Returns a order request that closes 50% of a selected position by volume
            ticket: the position ID that will be modified. (Currently not implemented)
            When ticket=1, it will close half of ALL currently open positions"""
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
        """Returns an order request that closes a specified percentage of a specific position
            ticket: position ID
            When ticket=1, closes specified percentage of ALL currently open positions"""
        if ticket == 1:
            # If no ticket specified, close half of all positions
            for pos in mt5.positions_get():
                position_id = mt5.TradePosition(pos).ticket
                symbol = mt5.TradePosition(pos).symbol
                sell_vol = round(((mt5.TradePosition(pos).volume / 100) * percent_close), 2)
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
                self.order_error_check(result)

    def close_custom_volume(self, vol, ticket=1):
        """Returns an order request that closes a position by a specified volume
            Currently not implemented within the GUI"""
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

    def half_risk(self):
        """Returns an order request that halves the initial risk of an open position
            Will have a ticket system implemented that will allow a position to be specified"""
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

            result = mt5.order_send(request)
            self.order_error_check(result)

    def runner(self):
        """Returns an order request. Will automatically close 'pct_close' percent of all positions and set the stoploss
            to the opening price + 'sl_points'

            Will implement a ticket system to allow specification of a position"""
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
            pct_close = 80
            sl_points = 30
            tp_points = 500

            if order == 0:  # Buy
                new_sl = round(price + sl_points * point, 3)
                if current_price < new_sl:
                    print("Desired SL is under current price")
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
                    # sys.exit(0)
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
                self.order_error_check(result)
            except UnboundLocalError:
                print(f"Desired SL      : {new_sl}")
                print(f"Current Price   : {mt5.TradePosition(pos).price_current}")

    @staticmethod
    def order_error_check(result):
        """Returns the result of an order request. If it fails, it will give a break down of the specified parameters"""
        if result is not None and result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order_send failed.  Retcode :   {result.retcode}")
            result_dict = result._asdict()
            return result_dict
        # elif result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
        #     print("Order_send() successful")

    def auto_be(self):
        """Returns an order request. Sets all open positions to break even + a few points to ensure no loss is taken"""
        for pos in mt5.positions_get():
            position_id = mt5.TradePosition(pos).ticket
            symbol = mt5.TradePosition(pos).symbol
            tp = mt5.TradePosition(pos).tp
            sl = mt5.TradePosition(pos).sl
            order = mt5.TradePosition(pos).type
            price = mt5.TradePosition(pos).price_open
            point = mt5.symbol_info(symbol).point
            order = mt5.TradePosition(pos).type

            if order == 1:
                request = {
                    "action":   mt5.TRADE_ACTION_SLTP,
                    "symbol":   symbol,
                    "position": position_id,
                    "sl":       round(price - 5 * point, 3),
                    "tp":       tp,
                    "magic":    self.magic,
                    "comment":  f"python auto BE {symbol}"
                }

            elif order == 0:
                request = {
                    "action":   mt5.TRADE_ACTION_SLTP,
                    "symbol":   symbol,
                    "position": position_id,
                    "sl":       round(price + 5 * point, 3),
                    "tp":       tp,
                    "magic":    self.magic,
                    "comment":  f"python auto BE {symbol}"
                }

            result = mt5.order_send(request)
            self.order_error_check(result)

    def risk_to_xreward(self, x):
        """Returns the required take profit level to ensure at least a 1:1 trade is taken"""
        if not isinstance(self.StopLoss.sl, float):
            return -1
        sl = float(self.StopLoss.sl)
        if isinstance(self.OpenPrice.price, float):
            # if price has been given
            price = float(self.OpenPrice.price)
            pip_diff = round(abs(price - sl), 3)
        else:
            if self.OrderType.order_type in {mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP}:
                price = mt5.symbol_info_tick(self.symbol).ask
                pip_diff = round(abs(price - sl), 3)
            elif self.OrderType.order_type in {mt5.ORDER_TYPE_SELL, mt5.ORDER_TYPE_SELL_LIMIT,
                                               mt5.ORDER_TYPE_SELL_STOP}:
                price = mt5.symbol_info_tick(self.symbol).bid
                pip_diff = round(abs(price - sl), 3)
        if self.OrderType.order_type in {mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP}:
            self.TakeProfit.tp = round(price + (x * pip_diff), 3)
        elif self.OrderType.order_type in {mt5.ORDER_TYPE_SELL, mt5.ORDER_TYPE_SELL_LIMIT, mt5.ORDER_TYPE_SELL_STOP}:
            self.TakeProfit.tp = round(price - (x * pip_diff), 3)

    def get_open_tickets(self):
        pass

    def get_pending_tickets(self):
        tickets = list()
        for order in mt5.orders_get():
            tickets.append(str(order._asdict()['ticket']))
        return tickets

        # pos = mt5.orders_get()[0]  # FIXME Again check if this can be done better without [0]
        #     tickets.append(mt5.TradeOrder(pos).ticket)
        # return tickets
