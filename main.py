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
import pandas as pd


class TradingApp(EWrapper, EClient):
        def __init__(self):
            EClient.__init__(self,self)
            self.pos_df = pd.DataFrame(columns=['Symbol', 'SecType',
                                             'Currency', 'Position', 'Avg cost'])
            self.acc_summary_df = pd.DataFrame(columns=['Account', 'Value', 'Currency'])
            self.pnl_summary_df = pd.DataFrame(columns=['DailyPnL', 'UnrealizedPnL', 'RealizedPnL'])
            self.order_df = pd.DataFrame(columns=['Account', 'Symbol', 'SecType',
                                              'Exchange', 'Action', 'OrderType',
                                              'TotalQty', 'CashQty', 'LmtPrice',
                                              'AuxPrice', 'Status'])
            self.execution_df = pd.DataFrame(columns=['Symbol', 'SecType', 'Currency',
                                                      'Time', 'Exchange',
                                                      'Side', 'Shares', 'Price',
                                                      'AvPrice'])

        def nextValidId(self, orderId):
            super().nextValidId(orderId)
            self.nextValidOrderId = orderId

        def accountSummary(self, reqId, account, tag, value, currency):
            super().accountSummary(reqId, account, tag, value, currency)
            dictionary = {"Account": account, "Value": value, "Currency": currency}
            self.acc_summary_df = self.acc_summary_df.append(dictionary, ignore_index=True)

        def pnl(self, reqId, dailyPnL, unrealizedPnL, realizedPnL):
            super().pnl(reqId, dailyPnL, unrealizedPnL, realizedPnL)
            dictionary = {"DailyPnL": dailyPnL, "UnrealizedPnL": unrealizedPnL, "RealizedPnL": realizedPnL}
            self.pnl_summary_df = self.pnl_summary_df.append(dictionary, ignore_index=True)

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
            dictionary = {"Account": order.account, "Symbol": contract.symbol, "SecType": contract.secType,
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

        # Request PnL
        app.reqPnL(5, "DU3635578", "")
        time.sleep(0.5)
        pnl_summary_df = app.pnl_summary_df
        pnl_summary_df["DailyPnL"] = pnl_summary_df["DailyPnL"].round(decimals = 2)
        pnl_summary_df["UnrealizedPnL"] = pnl_summary_df["UnrealizedPnL"].round(decimals = 2)
        pnl_summary_df["RealizedPnL"] = pnl_summary_df["RealizedPnL"].round(decimals = 2)

        # Profit & loss labelframe
        lf = LabelFrame(master,text="Account Summary", labelanchor="n")
        lf.place(x= 0, y=0)

        # Insert Profit & loss data in labelframe
        self.acc_sum = Text(lf, height = 2, width=130, font=("Helvetica", 18))
        self.acc_sum.insert(INSERT, pnl_summary_df.to_string(index=False))
        self.acc_sum.config(state = 'disabled')
        self.acc_sum.grid()


        # Request positions
        app.reqPositions()
        time.sleep(0.5)
        pos_df = app.pos_df
        pos_df['Avg cost'] = pos_df['Avg cost'].round(decimals=2)

        lz = LabelFrame(master, text="Positions", labelanchor="n")
        lz.place(x=820 , y=570)

        # Create treeview
        self.tree1 = ttk.Treeview(lz)
        self.tree1.grid()
        self.tree1['columns'] = pos_df.columns.values.tolist()

        # Add data to treeview
        for i in pos_df.columns.values.tolist():
                self.tree1.column(i, width=90)
                self.tree1.heading(i, text=i)

        for index, row in pos_df.iterrows():
                self.tree1.insert("", 'end', text=index, values=list(row))
        self.tree1.column("#0", width = 0, stretch = "no") # to get rid of the index column

        app.reqExecutions(21, ExecutionFilter())
        execution_df = app.execution_df
        time.sleep(1)

        exec_labelframe = LabelFrame(master, text="Trades", labelanchor="n")
        exec_labelframe.place(x=0 , y=570)

        self.tree2 = ttk.Treeview(exec_labelframe)
        self.tree2.grid()
        self.tree2['columns'] = execution_df.columns.values.tolist()

        # Add data to treeview
        for i in execution_df.columns.values.tolist():
                self.tree2.column(i, width=90)
                self.tree2.heading(i, text=i)
        for index, row in execution_df.iterrows():
                self.tree2.insert("", 'end', text=index, values=list(row))
        self.tree2.column("#0", width = 0, stretch = "no") # to get rid of the index column

        app.reqOpenOrders()
        app.reqAllOpenOrders() # returns all open orders irrespective of client ID
        time.sleep(1)
        order_df = app.order_df

        order_labelframe = LabelFrame(master, text="Orders", labelanchor="n")
        order_labelframe.place(x=0 , y=340)

        self.tree3 = ttk.Treeview(order_labelframe)
        self.tree3.grid()
        self.tree3['columns'] = order_df.columns.values.tolist()

        # Add data to treeview
        for i in order_df.columns.values.tolist():
                self.tree3.column(i, width=90)
                self.tree3.heading(i, text=i)
        for index, row in execution_df.iterrows():
                self.tree3.insert("", 'end', text=index, values=list(row))
        self.tree3.column("#0", width = 0, stretch = "no") # to get rid of the index column




root = Tk()
gui = ConnectionWindow(root)
root.mainloop()
