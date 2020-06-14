import sys
import importlib
import MetaTrader5 as mt5

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget

UI = importlib.import_module('traderUI5')
trade = importlib.import_module('spooksFX')
tradeCalc = importlib.import_module('Trading Tool')

# TODO  IF YOU CHANGE 'Trader' EVERYTHING NEEDS CHANGING
Trader = trade.TradeSession(916848650)
balance = mt5.account_info()._asdict()['balance']
leverage = mt5.account_info()._asdict()['leverage']

Calc = tradeCalc.TradingTool(balance=balance, leverage=leverage)


# price, lot, sl = demo.position_size(134.000, 134.150, 1.0)


class TraderControl:

    def __init__(self, view):
        """Controller initializer."""
        self._view = view
        # Connect signals and slots
        self.set_order_type()
        self._connectSignals()

    def set_sl(self):
        Trader.StopLoss.sl = self._view.priceSpinBox.value()
        self._view.stopLossBox.setText(f"{Trader.StopLoss.sl}")

    def set_tp(self):
        Trader.TakeProfit.tp = self._view.priceSpinBox.value()
        self._view.takeProfitBox.setText(f"{Trader.TakeProfit.tp}")

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
        if self._view.orderTypeComboBox.currentText() == "Sell":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_SELL
        if self._view.orderTypeComboBox.currentText() == "Buy Limit":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_BUY_LIMIT
        if self._view.orderTypeComboBox.currentText() == "Sell Limit":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_SELL_LIMIT
        if self._view.orderTypeComboBox.currentText() == "Buy Stop":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_BUY_STOP
        if self._view.orderTypeComboBox.currentText() == "Sell Stop":
            Trader.OrderType.order_type = mt5.ORDER_TYPE_SELL_STOP

    def order_calc(self):
        # TODO if no price given, use current price
        # open_price, sl, risk
        Trader.Volume.volume = Calc.position_size(Trader.OpenPrice.price, Trader.TakeProfit.tp, Trader.Risk.risk)
        Trader.check_order(Trader.OrderType.order_type, "GBPJPY", Trader.OpenPrice.price, Trader.Volume.volume)

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
