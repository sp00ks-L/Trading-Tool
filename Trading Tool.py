import pandas as pd
import numpy as np
import importlib
import MetaTrader5 as mt5
# trade = importlib.import_module("mt5test")


class TradingTool:

    def __init__(self, balance, leverage):
        self.balance = balance
        self.leverage = leverage

    def get_pips(self, close_price, vol, risk):
        pip_value = round((0.01 / close_price) * vol, 5)
        pip_sl = ((self.balance * (risk / 100)) / 100) / pip_value
        return pip_value, pip_sl

    @staticmethod
    def risk_reward(profit, loss):
        try:
            rr = round(profit / loss, 1)
        except ZeroDivisionError:
            return "\nThis amount of risk is not suitable with current parameters"
        return f"R : R       :   {1} : {rr}"

    def margin(self, vol):
        return (vol * 100000) / self.leverage

    def buy(self, vol, open_price, close_price, risk):
        vol *= 100000
        entry = open_price * vol
        out = close_price * vol
        pip_val, pip_sl = self.get_pips(close_price, vol, risk)
        profit = round(((out - entry) / close_price), 2)
        actual_sl = round(open_price - (pip_sl / 100), 3)
        potential_loss = round((open_price - actual_sl) * pip_val * 10000, 2)

        print(f"Pip Value   :   {round(pip_val, 5)}")
        print(f"{risk}% SL       :   {actual_sl} -->  £ {potential_loss}")
        print(f"Profit (£)  :   {profit}")
        print(f"Return      :   {round((profit / self.balance) * 100, 2)}%")
        print(self.risk_reward(profit, potential_loss))

    def sell(self, vol, open_price, close_price, risk):
        vol *= 100000
        entry = open_price * vol
        out = close_price * vol
        pip_val, pip_sl = self.get_pips(close_price, vol, risk)
        profit = round(((entry - out) / close_price), 2)
        actual_sl = round(open_price + (pip_sl / 100), 3)
        potential_loss = round((actual_sl - open_price) * pip_val * 10000, 2)

        print(f"Pip Value   :   {round(pip_val, 5)}")
        print(f"{risk}% SL       :   {actual_sl} -->  £ {potential_loss}")
        print(f"Profit (£)  :   {profit}")
        print(f"Return      :   {round((profit / self.balance) * 100, 2)}%")
        print(self.risk_reward(profit, potential_loss))

    def entry(self, order_type, open_price, output=False):
        out = pd.DataFrame()
        vols = [0.06, 0.12, 0.18]
        risks = [1, 2, 5, 10]
        for vol in vols:
            rdata = []
            for risk in risks:
                pip_val, pip_sl = self.get_pips(close_price=open_price, vol=vol * 1000, risk=risk)
                if order_type == 'BUY':
                    exp_profit = round(open_price + (pip_sl / 100), 3)
                    actual_sl = round(open_price - (pip_sl / 100), 3)
                    pip_diff = round((exp_profit - open_price) * 100, 3)
                elif order_type == 'SELL':
                    exp_profit = round(open_price - (pip_sl / 100), 3)
                    actual_sl = round(open_price + (pip_sl / 100), 3)
                    pip_diff = round((open_price - exp_profit) * 100, 3)

                rdata.append((actual_sl, exp_profit, pip_diff))
            data = {'Volume': vol, 'Margin': self.margin(vol), '1pct': [rdata[0]], '2pct': [rdata[1]],
                    '5pct': [rdata[2]], '10pct': [rdata[3]]}
            new_df = pd.DataFrame(data)
            out = out.append(new_df)
        out.set_index('Volume', inplace=True)
        print(out.head())
        if output:
            out.to_csv(f"{order_type} - {open_price}.csv")

    def returnspct(self, profit):
        print(f"{round((profit / self.balance) * 100, 2)}")
        return '-----------------'

    '''
    volume entry calc for given risk
    Example
    If you enter at 137.050 and you want your SL @ 137.191
    Enter your risk at 1%
    return appropriate volume to represent loss 
    '''

    def position_size(self, open_price, sl, risk):
        pip_diff = abs((open_price - sl) * 100)
        max_loss = round(self.balance * (risk / 100), 2)
        pos_size = round((max_loss / pip_diff) / (0.01 / sl), 4)
        print(f"Current Balance     :   {self.balance}")
        print(f"{risk}% Risk           :   {max_loss}")
        print("--------------------------------------")
        print(f"Position Size       :   {pos_size} units")
        print(f"Standard Lot        :   {round(pos_size / 100000, 4)}")
        print(f"Mini Lot            :   {round(pos_size / 10000, 4)}")
        print(f"Micro Lot           :   {round(pos_size / 1000, 4)}")
        print("--------------------------------------")
        return round(pos_size / 100000, 2)


# demo = Tradingtool(balance=653.23, leverage=50)
demo = TradingTool(balance=67255.71, leverage=50)
# demo.buy(0.12, 138.250, 138.374, risk=2)
# demo.sell(0.045, 135.430, 135.000, risk=2)
# demo.entry('SELL', 134.580, output=True)


symbol = 'GBPJPY'
# price, lot, sl = demo.position_size(135.000, 134.900, 1)
# print(lot)

# mt5.initialize()
# Trader = trade.TradeSession(916848650)
# Trader.open_trade('BUY', symbol, lot, sl, 500, 5)
# # Trader.runner(75, 10, 100)
