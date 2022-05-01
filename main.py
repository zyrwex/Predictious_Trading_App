"""Main python file of the predictious trading bot.

"""

import threading
import time
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.execution import *
from ibapi.contract import Contract
import pandas as pd


class TradingApp(EWrapper, EClient):
        def __init__(self):
            EClient.__init__(self,self)
            self.contract_id = 0
            self.pos_df = pd.DataFrame(columns=['Symbol', 'SecType',
                                             'Currency', 'Position', 'Avg cost'])
            self.acc_summary_df = pd.DataFrame(columns=['Tag', 'Value'])
            self.order_df = pd.DataFrame(columns=['Symbol', 'SecType',
                                              'Action', 'OrderType', "PermId",
                                              'TotalQty', 'LmtPrice'])
            self.execution_df = pd.DataFrame(columns=['Symbol', 'SecType', 'Currency',  "ExecId",
                                                      'Time',
                                                      'Side', 'Shares',
                                                      'AvPrice'])
            self.pnl_single_df = pd.DataFrame(columns=['UnrealizedPnL', 'dailyPnL', 'Value' ])


        def nextValidId(self, orderId):
            super().nextValidId(orderId)
            self.nextValidOrderId = orderId

        def accountSummary(self, reqId, account, tag, value, currency):
            super().accountSummary(reqId, account, tag, value, currency)
            dictionary = {"Tag": tag, "Value": value}
            self.acc_summary_df = self.acc_summary_df.append(dictionary, ignore_index=True)

        def position(self, account, contract, position, avgCost):
            super().position(account, contract, position, avgCost)
            dictionary = {"Symbol": contract.symbol, "SecType": contract.secType,
                          "Currency": contract.currency, "Position": position, "Avg cost": avgCost}
            if self.pos_df["Symbol"].str.contains(contract.symbol).any():
                self.pos_df.loc[self.pos_df["Symbol"]==contract.symbol,"Position"] = position
                self.pos_df.loc[self.pos_df["Symbol"]==contract.symbol,"Avg cost"] = avgCost
            else:
                self.pos_df = self.pos_df.append(dictionary, ignore_index=True)

        def openOrder(self, orderId, contract, order, orderState):
            super().openOrder(orderId, contract, order, orderState)
            dictionary = {"Symbol": contract.symbol, "SecType": contract.secType,
                        "Action": order.action, "OrderType": order.orderType,
                          "TotalQty": order.totalQuantity, "PermId":order.permId,
                          "LmtPrice": order.lmtPrice, "AuxPrice": order.auxPrice, "Status": orderState.status}
            if self.order_df["PermId"].astype(str).str.contains(str(order.permId)).any():
                self.order_df.loc[self.order_df["PermId"]==order.permId,"Status"] = orderState.status
                self.order_df.loc[self.order_df["PermId"]==order.permId,"AuxPrice"] = order.auxPrice
            else:
                self.order_df = self.order_df.append(dictionary, ignore_index=True)

        def execDetails(self, reqId, contract, execution):
            super().execDetails(reqId, contract, execution)
            dictionary = {"Symbol":contract.symbol, "SecType":contract.secType, "Currency":contract.currency,
                        "Time":execution.time,  "ExecId":execution.execId,
                          "Side":execution.side, "Shares":execution.shares,
                          "AvPrice":execution.avgPrice}
            if self.execution_df['ExecId'].str.contains(execution.execId).any():
                pass
            else:
                self.execution_df = self.execution_df.append(dictionary, ignore_index=True)

        def pnlSingle(self, reqId, pos, dailyPnL, unrealizedPnL, realizedPnL, value):
            super().pnlSingle(reqId, pos, dailyPnL, unrealizedPnL, realizedPnL, value)
            dictionary = {"UnrealizedPnL": unrealizedPnL, "dailyPnL": dailyPnL, "Value": value}
            self.pnl_single_df = self.pnl_single_df.append(dictionary, ignore_index=True)


        def contractDetails(self, reqId, contractDetails):
            self.contract_id = int(str(contractDetails.contract).split(",")[0])


app = TradingApp()  # Initialize the Trading Object

class ConnectionWindow:
    """This is the log window where the user will enter their connection information."""
    def __init__(self, master):
        self.master = master
        self.input1 = ""
        self.input2 = ""
        self.input3 = ""
        self.input4 = ""

        # Define the window
        master.title('Trading Platform')
        master.geometry('490x350')
        master.resizable(0, 0)
        # To make sure the window comes to the front when app is opened
        master.attributes('-topmost', True)
        master.update()
        # To make sure the window doesn't stay permanently in the front
        master.attributes('-topmost', False)

        # Configure the rows
        master.rowconfigure(0, weight=1, minsize=70)
        master.rowconfigure(1, weight=1)
        master.rowconfigure(2, weight=1)
        master.rowconfigure(3, weight=1)
        master.rowconfigure(4, weight=1)
        master.rowconfigure(5, weight=1)
        master.rowconfigure(6, weight=1, minsize=70)

        # Configure the columns
        master.columnconfigure(0, weight=1, minsize=70)
        master.columnconfigure(1, weight=1, minsize=70)
        master.columnconfigure(2, weight=1)
        master.columnconfigure(3, weight=1, minsize=70)
        master.columnconfigure(4, weight=1, minsize=70)

        # Label of the input boxes
        self.label1 = Label(master, text="Account Number")
        self.label2 = Label(master, text="IP Adress")
        self.label3 = Label(master, text="Socket Port")
        self.label4 = Label(master, text="Client ID")
        self.label1.grid(row=1, column=1)
        self.label2.grid(row=2, column=1)
        self.label3.grid(row=3, column=1)
        self.label4.grid(row=4, column=1)

        # Input boxes
        self.entry1 = Entry(master, width=15)
        self.entry2 = Entry(master, width=15)
        self.entry3 = Entry(master, width=15)
        self.entry4 = Entry(master, width=15)

        # Read the connection information file
        lst = self.read_file()

        # Insert the default connection information
        self.account_number = lst[0]
        self.ip = lst[1]
        self.port = lst[2]
        self.client_id = lst[3]
        self.entry1.insert(0, self.account_number)
        self.entry2.insert(0, self.ip)
        self.entry3.insert(0, self.port)
        self.entry4.insert(0, self.client_id)

        self.entry1.grid(row=1, column=2)
        self.entry2.grid(row=2, column=2)
        self.entry3.grid(row=3, column=2)
        self.entry4.grid(row=4, column=2)

        # connection-button
        self.button = Button(master, text='Connect to TWS', command=lambda: [self.tws_connect(), self.new_window()])
        self.button.grid(row=5, column=2)

    def new_window(self):
        # Check connection; open main window and hide connection window if connection is established
        if app.isConnected() is True:
            time.sleep(1)
            self.master.withdraw()
            self.new_window = Toplevel(self.master)
            self.gui2 = MainWindow(self.new_window)
        else:  # Error message box will appear and connection da will be set to default if not
            f = open("connection_data.txt", "w")
            f.write("DU3635578,127.0.0.1,7497,0")
            f.close()

            self.entry1.delete(0, END)
            self.entry2.delete(0, END)
            self.entry3.delete(0, END)
            self.entry4.delete(0, END)
            self.entry1.insert(0, self.account_number)
            self.entry2.insert(0, self.ip)
            self.entry3.insert(0, self.port)
            self.entry4.insert(0, self.client_id)
            messagebox.showerror("Error", """Connection failed, try again. Account number, IP Adress, Socket Port and Client ID have been reset to default.
                                  Make sure you are logged into your TWS.""")

    def create_file(self, account_number, ip, port, client_id):
        """Save the user inputs connection data

        :param account_number: Users account number
        :param ip: IP number
        :param port: Port number (Paper Trading Account port of TWS is 7497)
        :param client_id: Client ID (TWS session can handle 32 different clients simultaneously)
        """
        f = open("connection_data.txt", "w")
        f.write(""+str(account_number)+","+str(ip)+","+str(port)+","+str(client_id)+"")
        f.close()

    def read_file(self):
        """This function is used to set default values in the entry boxes in the GUI

        :return: connection information as a list
        """

        try:
            f = open("connection_data.txt", "r")
            lst = f.read().split(',')
            if len(lst)!=4:
                f = open("connection_data.txt", "w")
                f.write("DU3635578,127.0.0.1,7497,0")
                f.seek(0)
                lst = f.read().split(',')
                return lst
            f.close()
            return lst
        except IOError:  # If file doesn't exist, create a new one
            f = open("connection_data.txt", "w+")
            f.write("DU3635578,127.0.0.1,7497,0")
            f.seek(0)
            lst = f.read().split(',')
            f.close()
            return lst

    def tws_connect(self):
        """Establish a connection to TWS"""

        self.input1 = self.entry1.get()
        self.input2 = self.entry2.get()
        self.input3 = self.entry3.get()
        self.input4 = self.entry4.get()
        self.create_file(self.input1, self.input2, self.input3, self.input4)
        # Open the file with the connection information
        f = open("connection_data.txt", "r")
        lst = f.read().split(',')


        # Connect to local machine
        app.connect(lst[1], int(lst[2]), int(lst[3]))
        f.close()
        # Put websocket connection into another thread
        con_thread = threading.Thread(target=self.websocket_con, daemon=True)
        con_thread.start()


    def websocket_con(self):
        """Start TCP connection. This is where the message queue is processed in an
        infinite loop and the EWrapper call-back functions are automatically triggered
        """

        app.run()

class MainWindow:
    """This is the main window where charts, trades, positions etc. will be shown."""
    def __init__(self, master):

        self.master = master
        # Define the window
        master.geometry("1440x800")
        master.resizable(False, False)
        # To make sure the window comes to the front when app is opened
        master.attributes('-topmost', True)
        master.update()
        # To make sure the window doesn't stay permanently in the front
        master.attributes('-topmost', False)
        root.after(100, self.display_tables)



    def display_tables(self):
        app.reqAccountSummary(99, "All", "$LEDGER:ALL")
        app.reqExecutions(21, ExecutionFilter())
        app.reqPositions()
        app.reqAllOpenOrders()
        time.sleep(1)

        acc_summ_usd_df = app.acc_summary_df
        acc_summ_usd_df.loc[32, 'Value'] = round(float(acc_summ_usd_df.loc[32, 'Value']), 2)
        acc_summ_usd_df.loc[33, 'Value'] = round(float(acc_summ_usd_df.loc[33, 'Value']), 2)
        acc_summ_usd_df.loc[34, 'Value'] = round(float(acc_summ_usd_df.loc[34, 'Value']), 2)
        acc_summ_usd_df.loc[26, 'Value'] = round(float(acc_summ_usd_df.loc[26, 'Value']), 2)
        acc_summ_usd_df['Value'] = acc_summ_usd_df['Value'].astype(str)+'$'
        acc_summ_usd_df = app.acc_summary_df.iloc[[32, 33, 34, 26],:]   # 56, 57, 58, 50
        acc_summ_usd_df = acc_summ_usd_df.transpose()


        # USD account summary labelframe
        acc_summ_usd_labelframe = LabelFrame(self.master,text="Account Summary in USD", labelanchor="n")
        acc_summ_usd_labelframe.place(x= 0, y=0)

        # USD account summary treeview
        self.acc_summ_usd_tree = ttk.Treeview(acc_summ_usd_labelframe, show="tree", height=2)
        self.acc_summ_usd_tree.grid()
        self.acc_summ_usd_tree['columns'] = acc_summ_usd_df.columns.values.tolist()

        # Add USD summary data to treeview
        for i in acc_summ_usd_df.columns.values.tolist():
                self.acc_summ_usd_tree.column(i, width=179)
                self.acc_summ_usd_tree.heading(i, text=i)
        for index, row in acc_summ_usd_df.iterrows():
                self.acc_summ_usd_tree.insert("", 'end', text=index, values=list(row))
        self.acc_summ_usd_tree.column("#0", width = 0, stretch = "no") # to get rid of the index column

        # Manipulate EURO summary data
        acc_summ_euro_df = app.acc_summary_df
        acc_summ_euro_df['Value'] = acc_summ_euro_df['Value'].str.rstrip('$')
        acc_summ_euro_df.loc[56, 'Value'] = round(float(acc_summ_euro_df.loc[56, 'Value']), 2)
        acc_summ_euro_df.loc[57, 'Value'] = round(float(acc_summ_euro_df.loc[57, 'Value']), 2)
        acc_summ_euro_df.loc[58, 'Value'] = round(float(acc_summ_euro_df.loc[58, 'Value']), 2)
        acc_summ_euro_df.loc[50, 'Value'] = round(float(acc_summ_euro_df.loc[50, 'Value']), 2)
        acc_summ_euro_df['Value'] = acc_summ_euro_df['Value'].astype(str)+'€'
        acc_summ_euro_df = acc_summ_euro_df.iloc[[56, 57, 58, 50],:]   # 56, 57, 58, 50
        acc_summ_euro_df = acc_summ_euro_df.transpose()

        # EURO account summary labelframe
        acc_summ_euro_labelframe = LabelFrame(self.master,text="Account Summary in EURO", labelanchor="n")
        acc_summ_euro_labelframe.place(x= 720, y=0)

        # EURO account summary treeview
        self.acc_summ_euro_tree = ttk.Treeview(acc_summ_euro_labelframe, show="tree", height=2)
        self.acc_summ_euro_tree.grid()
        self.acc_summ_euro_tree['columns'] = acc_summ_euro_df.columns.values.tolist()

        # Add EURO summary data to treeview
        for i in acc_summ_euro_df.columns.values.tolist():
                self.acc_summ_euro_tree.column(i, width=180)
                self.acc_summ_euro_tree.heading(i, text=i)
        for index, row in acc_summ_euro_df.iterrows():
                self.acc_summ_euro_tree.insert("", 'end', text=index, values=list(row))
        self.acc_summ_euro_tree.column("#0", width = 0, stretch = "no") # to get rid of the index column


        exec_df = app.execution_df

        # Execution labelframe
        exec_labelframe = LabelFrame(self.master, text="Trades", labelanchor="n")
        exec_labelframe.place(x=365 , y=570)

        # Exectution treeview
        self.exec_tree = ttk.Treeview(exec_labelframe)
        self.exec_tree.grid()
        self.exec_tree['columns'] = exec_df.columns.values.tolist()

        # Add execution data to treeview
        for i in exec_df.columns.values.tolist():
                self.exec_tree.column(i, width=60)
                self.exec_tree.heading(i, text=i)
        self.exec_tree.column(3, width=140)
        for index, row in exec_df.iterrows():
                self.exec_tree.insert("", 'end', text=index, values=list(row))
        self.exec_tree.column("#0", width = 0, stretch = "no") # to get rid of the index column

        order_df = app.order_df

        # order labelframe
        order_labelframe = LabelFrame(self.master, text="Open Orders", labelanchor="n")
        order_labelframe.place(x=0 , y=570)

        # order treeview
        self.order_tree = ttk.Treeview(order_labelframe)
        self.order_tree.grid()
        self.order_tree['columns'] = order_df.columns.values.tolist()

        # Add order data to treeview
        for i in order_df.columns.values.tolist():
                self.order_tree.column(i, width=60)
                self.order_tree.heading(i, text=i)
        for index, row in order_df.iterrows():
                self.order_tree.insert("", 'end', text=index, values=list(row))
        self.order_tree.column("#0", width = 0, stretch = "no") # to get rid of the index column


        pos_df = app.pos_df
        symbol_lst = []
        secType_lst = []
        symbol_lst = pos_df['Symbol'].values.tolist()
        secType_lst = pos_df['SecType'].values.tolist()
        contract = Contract()
        for i in range(len(symbol_lst)):
            contract.symbol = symbol_lst[i]
            contract.secType = secType_lst[i]
            contract.currency = "USD"
            app.reqContractDetails(100+i, contract)
            time.sleep(1)
            app.reqPnLSingle(i+1000, "DU3635578", "", app.contract_id) #update the account ID
            time.sleep(1)
        daily_pnl_variable = app.pnl_single_df
        pos_df['Avg cost'] = pos_df['Avg cost'].round(decimals=2)

        # Positions labelframe
        positions_labelframe = LabelFrame(self.master, text="Positions", labelanchor="n")
        positions_labelframe.place(x=870 , y=570)

        # Create positions treeview
        self.positions_tree = ttk.Treeview(positions_labelframe, height=4)
        self.positions_tree.grid()

        # Manipulate positions data
        tree_columns = pos_df.columns.values.tolist()
        tree_columns.extend(['UnrealizedPnL', 'dailyPnL', 'MktValue'])
        self.positions_tree['columns'] = tree_columns
        tree1_content =  pos_df.join(daily_pnl_variable)
        tree1_content['UnrealizedPnL'] = tree1_content['UnrealizedPnL'].round(decimals=2)
        tree1_content['dailyPnL'] = tree1_content['dailyPnL'].round(decimals=2)
        tree1_content['Value'] = tree1_content['Value'].round(decimals=2)

        # Add positions data to treeview
        for i in tree_columns:
                self.positions_tree.column(i, width=60)
                self.positions_tree.heading(i, text=i)
        self.positions_tree.column(5, width=90)
        self.positions_tree.column(6, width=90)
        self.positions_tree.column(7, width=90)

        for index, row in tree1_content.iterrows():
                self.positions_tree.insert("", 'end', text=index, values=list(row))
        self.positions_tree.column("#0", width = 0, stretch = "no") # to get rid of the index column

        # Cash positions labelframe
        cash_positions_labelframe = LabelFrame(self.master, text="Cash Positions", labelanchor="n")
        cash_positions_labelframe.place(x=870 , y=695)

        # Cash positions treeview
        self.cash_position_tree = ttk.Treeview(cash_positions_labelframe, height=3)
        self.cash_position_tree.grid()

        # Manipulate cash positions data
        cash_positions_df = app.acc_summary_df
        cash_positions_df['Value'] = cash_positions_df['Value'].str.rstrip('€')
        cash_positions_df.loc[32, 'Value'] = round(float(cash_positions_df.loc[32, 'Value']), 2)
        cash_positions_df.loc[8, 'Value'] = round(float(cash_positions_df.loc[8, 'Value']), 2)
        cash_positions_df = app.acc_summary_df.loc[[32, 8]]
        cash_positions_df['Value'] = cash_positions_df['Value'].astype(str)+'$'
        self.cash_position_tree['columns'] = cash_positions_df.columns.values.tolist()

        # Add cash positions data to treeview
        for i in cash_positions_df.columns.values.tolist():
                self.cash_position_tree.column(i, width=285)
                self.cash_position_tree.heading(i, text=i)
        for index, row in cash_positions_df.iterrows():
                self.cash_position_tree.insert("", 'end', text=index, values=list(row))
        self.cash_position_tree.column("#0", width = 0, stretch = "no") # to get rid of the index column

        root.after(100, self.display_tables)




if __name__ == '__main__':
    root = Tk()
    gui = ConnectionWindow(root)
    root.mainloop()
