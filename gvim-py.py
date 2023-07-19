#!/usr/bin/env python3

from tkinter import *
from tkinter.ttk import *

root = Tk()
root.geometry("800x600")

frame = Frame(root)
frame.pack()

mainbar = Menu(frame, bd=2, relief=RAISED)

filemenu = Menu(mainbar)
filemenu.add_command(label="Exit", command=root.destroy)
mainbar.add_cascade(label="File", menu=filemenu)

editmenu = Menu(mainbar)
mainbar.add_cascade(label="Edit", menu=editmenu)

helpmenu = Menu(mainbar)
mainbar.add_cascade(label="Help", menu=helpmenu)

root.config(menu=mainbar)

windows = Notebook(frame)
windows.pack()

def add_window(windows):
    sub_frame = Frame(windows)
    textpad = Text(sub_frame, bd=2, width=100, height=32, relief=SUNKEN)
    textpad.pack()
    entry = Entry(sub_frame, width=100)
    entry.pack()
    windows.add(sub_frame)
    return

add_window(windows)

root.mainloop()
