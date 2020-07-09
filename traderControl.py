import sys
import importlib
import MetaTrader5 as mt5
import threading
import datetime

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTime, QDateTime
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QFont

UI = importlib.import_module("traderUI12")
trade = importlib.import_module("spooksFX")
# tradeCalc = importlib.import_module("Trading Tool")

# TODO  IF YOU CHANGE 'Trader' EVERYTHING NEEDS CHANGING
Trader = trade.TradeSession(magic=916848650, symbol="GBPJPY")
balance = mt5.account_info()._asdict()["balance"]
leverage = mt5.account_info()._asdict()["leverage"]


# Calc = tradeCalc.TradingTool(balance=balance, leverage=leverage)


# TODO If you are doing high frequency trading / scalping, need to deal with re-quotes


class PopupMessages:

    def __init__(self, title, icon, text, fontsize):
        self.font = QFont()
        self.font.setPointSize(fontsize)  # 15 is a good size
        self.title = title
        self.icon = icon
        self.text = text

    def popup(self):
        message = QMessageBox()
        message.setWindowTitle(f"{self.title}")  # dont think fstring is required
        message.setIcon(self.icon)
        message.setText(self.text)
        message.setFont(self.font)

        ex = message.exec_()


class TraderControl:

    def __init__(self, view):
        """Controller initializer."""
        self._view = view
        Trader.Risk.risk = 1.0
        Trader.Deviation.dev = 1
        self._view.riskSpinBox.setValue(1.0)
        self._view.accBalance.setText(f"£{balance:.2f}")
        self._view.symbolDisplay.setText(f"{Trader.symbol}")
        self.get_prices()
        self.get_pending()
        self.get_open()
        self.font = QFont()
        self.font.setPointSize(15)
        # Connect signals and slots
        self.set_order_type()
        self._connectSignals()

    def get_prices(self):
        symbol = Trader.symbol
        bid = mt5.symbol_info_tick(symbol).bid
        ask = mt5.symbol_info_tick(symbol).ask
        spread = round(abs(ask - bid) * 1000)
        threading.Timer(1.0, self.get_prices).start()
        self._view.askPriceDisplay.setText(f"{ask:.3f}")
        self._view.bidPriceDisplay.setText(f"{bid:.3f}")
        self._view.spreadDisplay.setText(f"{spread}")

    def get_pending(self):
        threading.Timer(3.0, self.get_pending).start()
        Trader.no_orders = mt5.orders_total()
        if Trader.no_orders >= 1:
            self._view.pendingOrdersCombo.setEnabled(True)
            new_tickets = Trader.get_pending_tickets()
            current_tickets = [self._view.pendingOrdersCombo.itemText(i) for i in
                               range(self._view.pendingOrdersCombo.count())]
            if new_tickets != current_tickets:
                difference = list(set(new_tickets) - set(current_tickets))
                if len(current_tickets) < len(new_tickets):
                    for item in sorted(difference):
                        # add item
                        self._view.pendingOrdersCombo.addItem(str(item))
                    Trader.no_orders += len(difference)
                elif len(new_tickets) < len(current_tickets):
                    difference = list(set(current_tickets) - set(new_tickets))
                    for item in difference:
                        # find index
                        index = self._view.pendingOrdersCombo.findText(item)
                        # remove item
                        self._view.pendingOrdersCombo.removeItem(index)
                    Trader.no_orders -= len(difference)
        elif Trader.no_orders == 0:
            current_tickets = [self._view.pendingOrdersCombo.itemText(i) for i in
                               range(self._view.pendingOrdersCombo.count())]
            for i in range(len(current_tickets)):
                self._view.pendingOrdersCombo.removeItem(i)
            self._view.pendingOrdersCombo.setEnabled(False)

    def get_open(self):
        threading.Timer(3.0, self.get_open).start()
        Trader.no_positions = mt5.positions_total()

        if Trader.no_positions >= 1:
            self._view.openOrdersCombo.setEnabled(True)
            if self._view.openOrdersCombo.itemText(0) != "":
                self._view.openOrdersCombo.insertItem(0, "")
            new_tickets = Trader.get_open_tickets()
            current_tickets = [self._view.openOrdersCombo.itemText(i) for i in
                               range(self._view.openOrdersCombo.count())]

            if new_tickets != current_tickets:
                difference = list(set(new_tickets) - set(current_tickets))
                if len(current_tickets) < len(new_tickets):
                    for item in sorted(difference):
                        # add item
                        self._view.openOrdersCombo.addItem(str(item))
                    Trader.no_positions += len(difference)
                elif len(new_tickets) < len(current_tickets):
                    difference = list(set(current_tickets) - set(new_tickets))
                    for item in difference:
                        if item == "":
                            continue
                        # find index
                        index = self._view.openOrdersCombo.findText(item)
                        # remove item
                        self._view.openOrdersCombo.removeItem(index)
                    Trader.no_positions -= len(difference)
        elif Trader.no_positions == 0:
            current_tickets = [self._view.openOrdersCombo.itemText(i) for i in
                               range(self._view.openOrdersCombo.count())]
            for i in range(len(current_tickets)):
                self._view.openOrdersCombo.removeItem(i)
                self._view.openOrdersCombo.setEnabled(False)

    def set_sl(self):
        Trader.StopLoss.sl = self._view.priceSpinBox.value()
        self._view.stopLossBox.setText(f"{Trader.StopLoss.sl:.3f}")

    def set_tp(self):
        Trader.TakeProfit.tp = self._view.priceSpinBox.value()
        self._view.takeProfitBox.setText(f"{Trader.TakeProfit.tp:.3f}")

    def set_dev(self):
        Trader.Deviation.dev = self._view.riskSpinBox.value()
        self._view.devBox.setText(f"{Trader.Deviation.dev}")

    def set_risk(self):
        Trader.Risk.risk = self._view.riskSpinBox.value()
        self._view.riskBox.setText(f"{Trader.Risk.risk}")
        self._view.riskCost.setText(f"£{round(balance * (Trader.Risk.risk / 100), 2):.2f}")

    def set_price(self):
        Trader.OpenPrice.price = self._view.priceSpinBox.value()
        self._view.entryPriceBox.setText(f"{Trader.OpenPrice.price:.3f}")

    def enable_date(self):
        # TODO implement the contract type time
        if self._view.contractComboBox.currentText() == "Specified":
            self._view.dateTimeEdit.setEnabled(True)
        else:
            self._view.dateTimeEdit.setEnabled(False)

    def set_order_type(self):
        symbol = Trader.symbol
        if self._view.orderTypeComboBox.currentText() == "Buy":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_BUY
            self._view.priceSpinBox.setValue(mt5.symbol_info_tick(symbol).bid)
        if self._view.orderTypeComboBox.currentText() == "Sell":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_SELL
            self._view.priceSpinBox.setValue(mt5.symbol_info_tick(symbol).ask)
        if self._view.orderTypeComboBox.currentText() == "Buy Limit":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_BUY_LIMIT
            self._view.priceSpinBox.setValue(mt5.symbol_info_tick(symbol).bid)
        if self._view.orderTypeComboBox.currentText() == "Sell Limit":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_SELL_LIMIT
            self._view.priceSpinBox.setValue(mt5.symbol_info_tick(symbol).ask)
        if self._view.orderTypeComboBox.currentText() == "Buy Stop":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_BUY_STOP
            self._view.priceSpinBox.setValue(mt5.symbol_info_tick(symbol).bid)
        if self._view.orderTypeComboBox.currentText() == "Sell Stop":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_SELL_STOP
            self._view.priceSpinBox.setValue(mt5.symbol_info_tick(symbol).ask)

    def check_time(self):
        threading.Timer(3.0, self.check_time).start()
        if QTime.toPyTime(self._view.dateTimeEdit.time()) != Trader.order_tt:
            Trader.order_tt = QTime.toPyTime(self._view.dateTimeEdit.time())

    def order_expiration(self):
        if self._view.contractComboBox.currentText() == "GTC":
            Trader.order_time = mt5.ORDER_TIME_GTC
        elif self._view.contractComboBox.currentText() == "Today":
            Trader.order_time = mt5.ORDER_TIME_DAY
        elif self._view.contractComboBox.currentText() == "Specified":
            Trader.order_time = mt5.ORDER_TIME_SPECIFIED
            Trader.order_tt = QTime.toPyTime(self._view.dateTimeEdit.time())
            self.check_time()

    @staticmethod
    def order_calc():
        Trader.Volume.volume = Trader.position_size(Trader.OpenPrice.price, Trader.StopLoss.sl, Trader.Risk.risk)

        msg = Trader.check_order(Trader.OrderType.order_type, Trader.symbol, Trader.OpenPrice.price,
                                 Trader.Volume.volume)
        message = PopupMessages(title="Order Check", icon=QMessageBox.Information, text=msg, fontsize=15)
        message.popup()

    @staticmethod
    def _get_orders():
        msg = Trader.get_orders()
        message = PopupMessages(title="Pending Orders", icon=QMessageBox.Information, text=msg, fontsize=15)
        message.popup()

    @staticmethod
    def _get_positions():
        if mt5.positions_total() == 0:
            msg = "No Open Positions"
        else:
            msg = Trader.get_positions()
        message = PopupMessages(title="Open Positions", icon=QMessageBox.Information, text=msg, fontsize=15)
        message.popup()

    def exec_trade(self):
        symbol = Trader.symbol
        if Trader.OrderType.order_type == mt5.ORDER_TYPE_BUY:
            price = mt5.symbol_info_tick(symbol).ask
        elif Trader.OrderType.order_type == mt5.ORDER_TYPE_SELL:
            price = mt5.symbol_info_tick(symbol).bid

        lot = Trader.position_size(price, Trader.StopLoss.sl, Trader.Risk.risk)
        if lot == -1:
            self.entry_error_popup(msg="SL, TP and/or deviation")
        result = Trader.open_trade(Trader.OrderType.order_type, symbol, lot)
        if isinstance(result, dict):
            msg = ""
            for field in result.keys():
                if field == "request":
                    traderequest_dict = result[field]._asdict()
                    for item in traderequest_dict:
                        if item in {"action", "symbol", "volume", "price", "sl", "tp", "deviation"}:

                            if item == 'action':
                                msg += f"{item}   -   {Trader.Orders(traderequest_dict[item]).name}\n"
                            else:
                                msg += f"{item}   -   {traderequest_dict[item]}\n"
                        else:
                            pass
            self.order_error_popup(f"{result['comment']}\n\n{msg}")

        elif lot != -1:
            self.order_send_successful(msg="Order_send() Successful")

    def exec_order(self):
        symbol = Trader.symbol
        if Trader.OrderType.order_type in {mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_BUY_LIMIT}:
            lot = Trader.position_size(Trader.OpenPrice.price, Trader.StopLoss.sl, Trader.Risk.risk)
            result = Trader.place_order(Trader.OrderType.order_type, symbol, Trader.OpenPrice.price, lot)
        elif Trader.OrderType.order_type in {mt5.ORDER_TYPE_SELL_STOP, mt5.ORDER_TYPE_SELL_LIMIT}:
            lot = Trader.position_size(Trader.OpenPrice.price, Trader.StopLoss.sl, Trader.Risk.risk)
            result = Trader.place_order(Trader.OrderType.order_type, symbol, Trader.OpenPrice.price, lot)
        elif Trader.OrderType.order_type in {mt5.ORDER_TYPE_SELL, mt5.ORDER_TYPE_BUY}:
            error = PopupMessages(title="Entry Error", icon=QMessageBox.Warning,
                                  text=f"Not a valid pending order", fontsize=15)
            error.popup()
            return 0

        if lot == -1:
            self.entry_error_popup("SL, TP and/or deviation")
        if isinstance(result, dict):
            msg = ""
            for field in result.keys():
                if field == "request":
                    traderequest_dict = result[field]._asdict()
                    for item in traderequest_dict:
                        if item == 'action':
                            msg += f"Trade request: {item}   -   {Trader.Orders(traderequest_dict[item]).name}\n"
                        else:
                            msg += f"Trade request: {item}   -   {traderequest_dict[item]}\n"
            self.order_error_popup(f"{result['comment']}\n\n{msg}")

        elif lot != -1:
            self.order_send_successful(msg="Order_send() Successful")

    def set_tp_ratio(self):
        if Trader.risk_to_xreward(self._view.tpSpinBox.value()):
            self.entry_error_popup("Stop Loss")
        else:
            self._view.takeProfitBox.setText(f"{Trader.TakeProfit.tp}")

    def double_order(self):
        symbol = Trader.symbol
        if Trader.OrderType.order_type == mt5.ORDER_TYPE_BUY:
            price = mt5.symbol_info_tick(symbol).ask
        elif Trader.OrderType.order_type == mt5.ORDER_TYPE_SELL:
            price = mt5.symbol_info_tick(symbol).bid

        lot = Trader.position_size(price, Trader.StopLoss.sl, Trader.Risk.risk)
        if lot == -1:
            self.entry_error_popup(msg="SL, TP and/or deviation")
        result = Trader.open_trade(Trader.OrderType.order_type, symbol, lot)
        if isinstance(result, dict):
            msg = ""
            for field in result.keys():
                if field == "request":
                    traderequest_dict = result[field]._asdict()
                    for item in traderequest_dict:
                        if item in {"action", "symbol", "volume", "price", "sl", "tp", "deviation"}:

                            if item == 'action':
                                msg += f"{item}   -   {Trader.Orders(traderequest_dict[item]).name}\n"
                            else:
                                msg += f"{item}   -   {traderequest_dict[item]}\n"
                        else:
                            pass
            self.order_error_popup(f"{result['comment']}\n\n{msg}")

        elif lot != -1:
            result2 = Trader.open_trade(Trader.OrderType.order_type, symbol, lot)
            self.order_send_successful(msg="Order_send() Successful")

    def close_cstm(self):
        custom_percent = self._view.closeCustomSpinBox.value()
        ticket = self._view.openOrdersCombo.currentText()
        Trader.close_custom_pct(percent_close=custom_percent, ticket=ticket)

    @staticmethod
    def entry_error_popup(msg):
        error = PopupMessages(title="Entry Error", icon=QMessageBox.Warning,
                              text=f"You have not entered a {msg} value", fontsize=15)
        error.popup()

    @staticmethod
    def order_error_popup(msg):
        error = PopupMessages(title="Order Error", icon=QMessageBox.Warning,
                              text=f"{msg}", fontsize=15)
        error.popup()

    @staticmethod
    def order_send_successful(msg):
        message = PopupMessages(title="Order Sent", icon=QMessageBox.Information,
                                text=f"{msg}", fontsize=15)
        message.popup()

    def get_open_ticket(self):
        return self._view.openOrdersCombo.currentText()

    def get_pending_ticket(self):
        return self._view.pendingOrdersCombo.currentText()

    def _cancel_order(self):
        ticket = self.get_pending_ticket()
        Trader.cancel_order(ticket)

    def _close_full(self):
        ticket = self.get_open_ticket()
        Trader.close_full(ticket)

    def _close_half(self):
        ticket = self.get_open_ticket()
        Trader.close_half(ticket=ticket)

    def _half_risk(self):
        ticket = self.get_open_ticket()
        Trader.half_risk(ticket=ticket)

    def _auto_be(self):
        ticket = self.get_open_ticket()
        Trader.auto_be(ticket=ticket)

    def _close_all(self):
        msg = Trader.close_all()
        close = PopupMessages(title="Close All", icon=QMessageBox.Information,
                              text=f"{msg}", fontsize=15)
        close.popup()

    def _cancel_all(self):
        msg = Trader.cancel_all()
        cancel = PopupMessages(title="Cancel All", icon=QMessageBox.Information,
                               text=f"{msg}", fontsize=15)
        cancel.popup()

    def partial_tp(self):
        price = self._view.priceSpinBox.value()
        proc = threading.Timer(1.0, self.partial_tp)
        proc.start()
        ticket = self.get_open_ticket()
        if Trader.OrderType.order_type == mt5.ORDER_TYPE_BUY:
            # bid
            if price == mt5.symbol_info_tick(Trader.symbol).bid:
                Trader.close_custom_pct(percent_close=80, ticket=ticket)
                Trader.auto_be(ticket=ticket)
                proc.cancel()
        if Trader.OrderType.order_type == mt5.ORDER_TYPE_SELL:
            # ask
            if price == mt5.symbol_info_tick(Trader.symbol).ask:
                Trader.close_custom_pct(percent_close=80, ticket=ticket)
                Trader.auto_be(ticket=ticket)
                proc.cancel()

    def candle_sl_set(self, tick):
        high, low = Trader.get_candle_hl(tick=tick)
        if Trader.OrderType.order_type == mt5.ORDER_TYPE_SELL:
            Trader.StopLoss.sl = high
            self._view.stopLossBox.setText(f"{Trader.StopLoss.sl:.3f}")
        if Trader.OrderType.order_type == mt5.ORDER_TYPE_BUY:
            Trader.StopLoss.sl = low
            self._view.stopLossBox.setText(f"{Trader.StopLoss.sl:.3f}")

    def _connectSignals(self):
        self._view.contractComboBox.currentIndexChanged.connect(lambda: self.enable_date())
        self._view.contractComboBox.currentIndexChanged.connect(lambda: self.order_expiration())
        self._view.orderTypeComboBox.currentIndexChanged.connect(lambda: self.set_order_type())
        self._view.setDevButton.clicked.connect(lambda: self.set_dev())
        self._view.setStopButton.clicked.connect(lambda: self.set_sl())
        self._view.setTargetButton.clicked.connect(lambda: self.set_tp())
        self._view.setRiskButton.clicked.connect(lambda: self.set_risk())
        self._view.setPriceButton.clicked.connect(lambda: self.set_price())
        self._view.checkPosButton.clicked.connect(lambda: self.order_calc())
        self._view.halfRiskButton.clicked.connect(lambda: self._half_risk())
        self._view.openTradeButton.clicked.connect(lambda: self.exec_trade())
        self._view.runnerButton.clicked.connect(lambda: Trader.runner())
        self._view.closeAllButton.clicked.connect(lambda: self._close_all())
        self._view.closeHalfButton.clicked.connect(lambda: self._close_half())
        self._view.openOrderButton.clicked.connect(lambda: self.exec_order())
        self._view.getOrdersButton.clicked.connect(lambda: self._get_orders())
        self._view.getPositionsButton.clicked.connect(lambda: self._get_positions())
        self._view.autoBeButton.clicked.connect(lambda: self._auto_be())
        self._view.targetAtRatioButton.clicked.connect(lambda: self.set_tp_ratio())
        self._view.doubleOrderButton.clicked.connect(lambda: self.double_order())
        self._view.cancelAllButton.clicked.connect(lambda: self._cancel_all())
        self._view.closeCustomButton.clicked.connect(lambda: self.close_cstm())
        self._view.cancelOrderButton.clicked.connect(lambda: self._cancel_order())
        self._view.closeFullButton.clicked.connect(lambda: self._close_full())
        self._view.partialTPButton.clicked.connect(lambda: self.partial_tp())
        self._view.oneMinButton.clicked.connect(lambda: self.candle_sl_set(tick="1min"))
        self._view.fiveMinButton.clicked.connect(lambda: self.candle_sl_set(tick="5min"))
        self._view.fifteenMinButton.clicked.connect(lambda: self.candle_sl_set(tick="15min"))
        self._view.thirtyMinButton.clicked.connect(lambda: self.candle_sl_set(tick="30min"))
        self._view.oneHourButton.clicked.connect(lambda: self.candle_sl_set(tick="1hr"))
        self._view.fourHourButton.clicked.connect(lambda: self.candle_sl_set(tick="4hr"))


def main():
    """Main function."""
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = UI.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    TraderControl(view=ui)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
