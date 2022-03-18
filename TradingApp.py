from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import pandas as pd

class TradingApp(EWrapper, EClient):
        def __init__(self):
            EClient.__init__(self,self)
            self.pos_df = pd.DataFrame(columns=['Account', 'Symbol', 'SecType',
                                             'Currency', 'Position', 'Avg cost'])
            self.acc_summary_df = pd.DataFrame(columns=['ReqId', 'Account', 'Tag', 'Value', 'Currency'])
            self.pnl_summary_df = pd.DataFrame(columns=['ReqId', 'DailyPnL', 'UnrealizedPnL', 'RealizedPnL'])
            self.order_df = pd.DataFrame(columns=['PermId', 'ClientId', 'OrderId',
                                              'Account', 'Symbol', 'SecType',
                                              'Exchange', 'Action', 'OrderType',
                                              'TotalQty', 'CashQty', 'LmtPrice',
                                              'AuxPrice', 'Status'])
            self.execution_df = pd.DataFrame(columns=['ReqId', 'PermId', 'Symbol',
                                                  'SecType', 'Currency', 'ExecId',
                                                  'Time', 'Account', 'Exchange',
                                                  'Side', 'Shares', 'Price',
                                                  'AvPrice', 'cumQty', 'OrderRef'])

        def nextValidId(self, orderId):
            super().nextValidId(orderId)
            self.nextValidOrderId = orderId

        def accountSummary(self, reqId, account, tag, value, currency):
            super().accountSummary(reqId, account, tag, value, currency)
            dictionary = {"ReqId":reqId, "Account": account, "Tag": tag, "Value": value, "Currency": currency}
            self.acc_summary = self.acc_summary.append(dictionary, ignore_index=True)

        def pnl(self, reqId, dailyPnL, unrealizedPnL, realizedPnL):
            super().pnl(reqId, dailyPnL, unrealizedPnL, realizedPnL)
            dictionary = {"ReqId":reqId, "DailyPnL": dailyPnL, "UnrealizedPnL": unrealizedPnL, "RealizedPnL": realizedPnL}
            self.pnl_summary = self.pnl_summary.append(dictionary, ignore_index=True)

        def position(self, account, contract, position, avgCost):
            super().position(account, contract, position, avgCost)
            dictionary = {"Account":account, "Symbol": contract.symbol, "SecType": contract.secType,
                          "Currency": contract.currency, "Position": position, "Avg cost": avgCost}
            if self.pos_df["Symbol"].str.contains(contract.symbol).any():
                self.pos_df.loc[self.pos_df["Symbol"]==contract.symbol,"Position"] = position
                self.pos_df.loc[self.pos_df["Symbol"]==contract.symbol,"Avg cost"] = avgCost
            else:
                self.pos_df = self.pos_df.append(dictionary, ignore_index=True)

        def openOrder(self, orderId, contract, order, orderState):
            super().openOrder(orderId, contract, order, orderState)
            dictionary = {"PermId":order.permId, "ClientId": order.clientId, "OrderId": orderId,
                          "Account": order.account, "Symbol": contract.symbol, "SecType": contract.secType,
                          "Exchange": contract.exchange, "Action": order.action, "OrderType": order.orderType,
                          "TotalQty": order.totalQuantity, "CashQty": order.cashQty,
                          "LmtPrice": order.lmtPrice, "AuxPrice": order.auxPrice, "Status": orderState.status}
            self.order_df = self.order_df.append(dictionary, ignore_index=True)

        def execDetails(self, reqId, contract, execution):
            super().execDetails(reqId, contract, execution)
            dictionary = {"ReqId":reqId, "PermId":execution.permId, "Symbol":contract.symbol, "SecType":contract.secType, "Currency":contract.currency,
                          "ExecId":execution.execId, "Time":execution.time, "Account":execution.acctNumber, "Exchange":execution.exchange,
                          "Side":execution.side, "Shares":execution.shares, "Price":execution.price,
                          "AvPrice":execution.avgPrice, "cumQty":execution.cumQty, "OrderRef":execution.orderRef}
            self.execution_df = self.execution_df.append(dictionary, ignore_index=True)
