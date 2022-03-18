"""Main python file of the predictious trading bot.

Contains mainly the the code of the GUI.
"""

from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from connection import tws_connect
from connection import read_file
from connection import create_file


class ConnectionWindow:
    """This is the log window where the user will enter their connection information."""
    def __init__(self, master):
        self.master = master
        self.input1 = ""
        self.input2 = ""
        self.input3 = ""

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
        master.rowconfigure(1, weight=1, minsize=70)
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
        self.label1 = Label(master, text="IP Adress")
        self.label2 = Label(master, text="Socket Port")
        self.label3 = Label(master, text="Client ID")
        self.label1.grid(row=2, column=1)
        self.label2.grid(row=3, column=1)
        self.label3.grid(row=4, column=1)

        # Input boxes
        self.entry1 = Entry(master, width=15)
        self.entry2 = Entry(master, width=15)
        self.entry3 = Entry(master, width=15)

        # Read the connection information file
        lst = read_file()

        # Insert the default connection information
        self.ip = lst[0]
        self.port = lst[1]
        self.client_id = lst[2]
        self.entry1.insert(0, self.ip)
        self.entry2.insert(0, self.port)
        self.entry3.insert(0, self.client_id)

        self.entry1.grid(row=2, column=2)
        self.entry2.grid(row=3, column=2)
        self.entry3.grid(row=4, column=2)

        # connection-button
        self.button = Button(master, text='Connect to TWS', command=self.clicked)
        self.button.grid(row=5, column=2)

    def clicked(self):
        self.input1 = self.entry1.get()
        self.input2 = self.entry2.get()
        self.input3 = self.entry3.get()
        create_file(self.input1, self.input2, self.input3)
        tws_connect()
        # Check connection; open main window and hide connection window if connection is established
        if tws_connect() is True:
            self.master.withdraw()
            self.new_window = Toplevel(self.master)
            self.gui2 = MainWindow(self.new_window)
        else:  # Error message box will appear if not
            self.entry1.delete(0, END)
            self.entry2.delete(0, END)
            self.entry3.delete(0, END)
            self.entry1.insert(0, self.x)
            self.entry2.insert(0, self.y)
            self.entry3.insert(0, self.z)
            messagebox.showerror("Error", """Connection failed, try again. IP Adress, Socket Port and Client ID have been reset to default.
                                  Make sure you are logged into your TWS.""")


class MainWindow:
    """This is the main window where charts, trades, positions etc. will be shown."""
    def __init__(self, master):
        # Define the window
        master.geometry("1440x800")
        # To make sure the window comes to the front when app is opened
        master.attributes('-topmost', True)
        master.update()
        # To make sure the window doesn't stay permanently in the front
        master.attributes('-topmost', False)


root = Tk()
gui = ConnectionWindow(root)
root.mainloop()
