import sys
import importlib
import MetaTrader5 as mt5
import threading

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QFont

UI = importlib.import_module("traderUI10")
trade = importlib.import_module("spooksFX")
tradeCalc = importlib.import_module("Trading Tool")

# TODO  IF YOU CHANGE 'Trader' EVERYTHING NEEDS CHANGING
Trader = trade.TradeSession(magic=916848650, symbol="GBPJPY")
balance = mt5.account_info()._asdict()["balance"]
leverage = mt5.account_info()._asdict()["leverage"]

Calc = tradeCalc.TradingTool(balance=balance, leverage=leverage)


# TODO If you are doing high frequency trading / scalping, need to deal with re-quotes


class TraderControl:

    def __init__(self, view):
        """Controller initializer."""
        self._view = view
        Trader.Risk.risk = 1.0
        Trader.Deviation.dev = 1
        self.font = QFont()
        self.font.setPointSize(15)
        self._view.riskSpinBox.setValue(1.0)
        self._view.accBalance.setText(f"£{balance:.2f}")
        self._view.symbolDisplay.setText(f"{Trader.symbol}")
        self.get_prices()
        self.get_pending()
        self.order_screener()
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
        if Trader.no_orders >= 1:
            self._view.pendingOrdersCombo.setEnabled(True)
            tickets = Trader.get_pending_tickets()
            self._view.pendingOrdersCombo.addItems(tickets)

    def order_screener(self):
        # checks every x seconds to see if no of order is different
        threading.Timer(10.0, self.order_screener).start()
        if mt5.orders_total() != Trader.no_orders:
            index = self._view.pendingOrdersCombo.findText()
            pass

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

    def order_expiration(self):
        if self._view.contractComboBox.currentText() == "GTC":
            dtime = None
        elif self._view.contractComboBox.currentText() == "Today":
            dtime = self._view.dateTimeEdit.datetime()
        elif self._view.contractComboBox.currentText() == "Specified":
            dtime = self._view.dateTimeEdit.datetime()

    def order_calc(self):
        Trader.Volume.volume = Calc.position_size(Trader.OpenPrice.price, Trader.StopLoss.sl, Trader.Risk.risk,
                                                  verbose=True)
        Trader.check_order(Trader.OrderType.order_type, Trader.symbol, Trader.OpenPrice.price, Trader.Volume.volume)

    def exec_trade(self):
        symbol = Trader.symbol
        if Trader.OrderType.order_type == mt5.ORDER_TYPE_BUY:
            price = mt5.symbol_info_tick(symbol).ask
        elif Trader.OrderType.order_type == mt5.ORDER_TYPE_SELL:
            price = mt5.symbol_info_tick(symbol).bid

        lot = Calc.position_size(price, Trader.StopLoss.sl, Trader.Risk.risk, verbose=True)
        if lot == -1:
            self.entry_error_popup("SL, TP and/or deviation")
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

        else:
            self.order_send_successful(msg="Order_send() Successful")

    def exec_order(self):
        symbol = Trader.symbol
        if Trader.OrderType.order_type in {mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_BUY_LIMIT}:
            lot = Calc.position_size(Trader.OpenPrice.price, Trader.StopLoss.sl, Trader.Risk.risk, verbose=True)
            result = Trader.place_order(Trader.OrderType.order_type, symbol, Trader.OpenPrice.price, lot)
        elif Trader.OrderType.order_type in {mt5.ORDER_TYPE_SELL_STOP, mt5.ORDER_TYPE_SELL_LIMIT}:
            lot = Calc.position_size(Trader.OpenPrice.price, Trader.StopLoss.sl, Trader.Risk.risk, verbose=True)
            result = Trader.place_order(Trader.OrderType.order_type, symbol, Trader.OpenPrice.price, lot)

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

        else:
            self.order_send_successful(msg="Order_send() Successful")

    def set_tp_ratio(self):
        if Trader.risk_to_xreward(self._view.tpSpinBox.value()):
            self.entry_error_popup("Stop Loss")
        else:
            self._view.takeProfitBox.setText(f"{Trader.TakeProfit.tp}")

    def double_order(self):
        self.exec_trade()
        self.exec_trade()

    def close_cstm(self):
        custom_percent = self._view.closeCustomSpinBox.value()
        Trader.close_custom_pct(percent_close=custom_percent)

    def entry_error_popup(self, msg):
        error = QMessageBox()
        error.setWindowTitle("Entry Error")
        error.setIcon(QMessageBox.Warning)
        error.setText(f"You have not entered a {msg} value")
        error.setFont(self.font)

        x = error.exec_()

    def order_error_popup(self, msg):
        error = QMessageBox()
        error.setWindowTitle("Order Error")
        error.setIcon(QMessageBox.Warning)
        error.setText(f"{msg}")
        error.setFont(self.font)

        x = error.exec_()

    def order_send_successful(self, msg):
        message = QMessageBox()
        message.setWindowTitle("Order Sent")
        message.setIcon(QMessageBox.Information)
        message.setText(f"{msg}")
        message.setFont(self.font)

        x = message.exec_()

    def _connectSignals(self):
        self._view.contractComboBox.currentIndexChanged.connect(lambda: self.enable_date())
        self._view.orderTypeComboBox.currentIndexChanged.connect(lambda: self.set_order_type())
        self._view.setDevButton.clicked.connect(lambda: self.set_dev())
        self._view.setStopButton.clicked.connect(lambda: self.set_sl())
        self._view.setTargetButton.clicked.connect(lambda: self.set_tp())
        self._view.setRiskButton.clicked.connect(lambda: self.set_risk())
        self._view.setPriceButton.clicked.connect(lambda: self.set_price())
        self._view.checkPosButton.clicked.connect(lambda: self.order_calc())
        self._view.halfRiskButton.clicked.connect(lambda: Trader.half_risk())
        self._view.openTradeButton.clicked.connect(lambda: self.exec_trade())
        self._view.runnerButton.clicked.connect(lambda: Trader.runner())
        self._view.closeAllButton.clicked.connect(lambda: Trader.close_all())
        self._view.closeHalfButton.clicked.connect(lambda: Trader.close_half())
        self._view.openOrderButton.clicked.connect(lambda: self.exec_order())
        self._view.getOrdersButton.clicked.connect(lambda: Trader.get_orders())
        self._view.getPositionsButton.clicked.connect(lambda: Trader.get_positions())
        self._view.autoBeButton.clicked.connect(lambda: Trader.auto_be())
        self._view.targetAtRatioButton.clicked.connect(lambda: self.set_tp_ratio())
        self._view.doubleOrderButton.clicked.connect(lambda: self.double_order())
        self._view.cancelAllButton.clicked.connect(lambda: Trader.cancel_all())
        self._view.closeCustomButton.clicked.connect(lambda: self.close_cstm())


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
