import sys
import importlib
import MetaTrader5 as mt5

from PyQt5 import QtCore, QtGui, QtWidgets

UI = importlib.import_module('traderUI6')
trade = importlib.import_module('spooksFX')
tradeCalc = importlib.import_module('Trading Tool')

# TODO  IF YOU CHANGE 'Trader' EVERYTHING NEEDS CHANGING
Trader = trade.TradeSession(916848650)
balance = mt5.account_info()._asdict()['balance']
leverage = mt5.account_info()._asdict()['leverage']

Calc = tradeCalc.TradingTool(balance=balance, leverage=leverage)

# TODO If you are doing high frequency trading / scalping, need to deal with re-quotes


class TraderControl:

    def __init__(self, view):
        """Controller initializer."""
        self._view = view
        self._view.riskSpinBox.setValue(1.0)
        # Connect signals and slots
        self.set_order_type()
        self._connectSignals()

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

    def set_price(self):
        Trader.OpenPrice.price = self._view.priceSpinBox.value()
        self._view.entryPriceBox.setText(f"{Trader.OpenPrice.price:.3f}")

    def enable_date(self):
        if self._view.contractComboBox.currentText() == "Specified":
            self._view.dateTimeEdit.setEnabled(True)
        else:
            self._view.dateTimeEdit.setEnabled(False)

    def set_order_type(self):
        if self._view.orderTypeComboBox.currentText() == "Buy":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_BUY
            self._view.priceSpinBox.setValue(mt5.symbol_info_tick('GBPJPY').bid)
        if self._view.orderTypeComboBox.currentText() == "Sell":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_SELL
            self._view.priceSpinBox.setValue(mt5.symbol_info_tick('GBPJPY').ask)
        if self._view.orderTypeComboBox.currentText() == "Buy Limit":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_BUY_LIMIT
            self._view.priceSpinBox.setValue(mt5.symbol_info_tick('GBPJPY').bid)
        if self._view.orderTypeComboBox.currentText() == "Sell Limit":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_SELL_LIMIT
            self._view.priceSpinBox.setValue(mt5.symbol_info_tick('GBPJPY').ask)
        if self._view.orderTypeComboBox.currentText() == "Buy Stop":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_BUY_STOP
            self._view.priceSpinBox.setValue(mt5.symbol_info_tick('GBPJPY').bid)
        if self._view.orderTypeComboBox.currentText() == "Sell Stop":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_SELL_STOP
            self._view.priceSpinBox.setValue(mt5.symbol_info_tick('GBPJPY').ask)

    def order_calc(self):
        # TODO if no price given, use current price
        Trader.Volume.volume = Calc.position_size(Trader.OpenPrice.price, Trader.TakeProfit.tp, Trader.Risk.risk,
                                                  verbose=True)
        Trader.check_order(Trader.OrderType.order_type, "GBPJPY", Trader.OpenPrice.price, Trader.Volume.volume)

    def exec_trade(self):
        if Trader.OrderType.order_type == mt5.ORDER_TYPE_SELL:
            sell = mt5.symbol_info_tick("GBPJPY").bid
            lot = Calc.position_size(sell, Trader.TakeProfit.tp, Trader.Risk.risk, verbose=True)
            Trader.open_trade(Trader.OrderType.order_type, "GBPJPY", lot)
        elif Trader.OrderType.order_type == mt5.ORDER_TYPE_BUY:
            buy = mt5.symbol_info_tick("GBPJPY").ask
            lot = Calc.position_size(buy, Trader.TakeProfit.tp, Trader.Risk.risk, verbose=True)
            Trader.open_trade(Trader.OrderType.order_type, "GBPJPY", lot)

    def exec_order(self):
        # action, symbol, open_price, lot
        if Trader.OrderType.order_type == mt5.ORDER_TYPE_BUY_STOP:
            lot = Calc.position_size(Trader.OpenPrice.price, Trader.TakeProfit.tp, Trader.Risk.risk, verbose=True)
            Trader.place_order(Trader.OrderType.order_type, "GBPJPY", Trader.OpenPrice.price, lot)
        if Trader.OrderType.order_type == mt5.ORDER_TYPE_SELL_STOP:
            lot = Calc.position_size(Trader.OpenPrice.price, Trader.TakeProfit.tp, Trader.Risk.risk, verbose=True)
            Trader.place_order(Trader.OrderType.order_type, "GBPJPY", Trader.OpenPrice.price, lot)

    def set_tp_ratio(self):
        Trader.risk_to_xreward(self._view.tpSpinBox.value())
        self._view.takeProfitBox.setText(f"{Trader.TakeProfit.tp}")

    def double_order(self):
        self.exec_trade()
        self.exec_trade()

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
