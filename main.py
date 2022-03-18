"""Trading Bot

Contains
"""

from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from connection import tws_connect
from connection import read_file
from connection import create_file

class ConnectionWindow:
    def __init__(self, master):
      self.master = master
      self.input1 = ""
      self.input2 = ""
      self.input3 = ""

      # Define the window
      master.title('Trading Platform')
      master.geometry('490x350')
      master.resizable(0,0)
      master.attributes('-topmost', True)  # To make sure the window comes to the front when app is opened
      master.update()
      master.attributes('-topmost', False)  # To make sure the window doesn't stay permanently in the front

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

      # Read the
      lst = read_file()


      self.x = lst[0]
      self.y = lst[1]
      self.z = lst[2]
      self.entry1.insert(0, self.x)
      self.entry2.insert(0, self.y)
      self.entry3.insert(0, self.z)

      self.entry1.grid(row=2, column=2)
      self.entry2.grid(row=3, column=2)
      self.entry3.grid(row=4, column=2)

      # connection-button
      self.button = Button(master, text = 'Connect to TWS', command = self.clicked)
      self.button.grid(row=5, column=2)

    def clicked(self):
      self.input1 = self.entry1.get()
      self.input2 = self.entry2.get()
      self.input3 = self.entry3.get()
      create_file(self.input1, self.input2, self.input3)
      tws_connect()
      if tws_connect() == True:
        self.master.withdraw()
        self.new_window = Toplevel(self.master)
        self.gui2 = MainWindow(self.new_window)
      else:
        self.entry1.delete(0, END)
        self.entry2.delete(0, END)
        self.entry3.delete(0, END)
        self.entry1.insert(0, self.x)
        self.entry2.insert(0, self.y)
        self.entry3.insert(0, self.z)
        messagebox.showerror("Error", "Connection failed, try again. IP Adress, Socket Port and Client ID have been reset to default. Make sure you are logged into your TWS.")

class MainWindow:
  def __init__(self, master):
    # Define the window
    master.geometry("1440x800")
    master.attributes('-topmost', True)  # To make sure the window comes to the front when app is opened
    master.update()
    master.attributes('-topmost', False)  # To make sure the window doesn't stay permanently in the front

root = Tk()
gui = ConnectionWindow(root)
root.mainloop()
