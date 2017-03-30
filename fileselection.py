import tkinter as tk

try:
    # for Python2
    from Tkinter import *   ## notice capitalized T in Tkinter
except ImportError:
    # for Python3
    from tkinter import *   ## notice lowercase 't' in tkinter here


from tkinter import filedialog

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()
print(file_path)