#!/usr/bin/env python3

from tkinter import *

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

windowsmenu = Menu(mainbar)
mainbar.add_cascade(label="Windows", menu=windowsmenu)

helpmenu = Menu(mainbar)
mainbar.add_cascade(label="Help", menu=helpmenu)

root.config(menu=mainbar)

textpad = Text(frame, bd=2, width=100, height=34, relief=SUNKEN)
textpad.pack()

root.mainloop()
