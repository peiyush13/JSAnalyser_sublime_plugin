import os
import sys
import tkinter as tk

try:
    # for Python2
    from Tkinter import *  ## notice capitalized T in Tkinter
except ImportError:
    # for Python3
    from tkinter import *  ## notice lowercase 't' in tkinter here

from tkinter import filedialog

path = os.path.realpath(__file__).split("\\")
path[len(path) - 1] = "";
FOLDER = "\\".join(path)
root = tk.Tk()
root.withdraw()

if len(sys.argv) == 2:
    arg = os.path.join(FOLDER, sys.argv[1])
    root.file_name = filedialog.askopenfilename(initialdir=arg, title="Select file",filetypes=[("JSON Files", "*.json")])
elif len(sys.argv) > 2:
    arg = os.path.join(FOLDER, sys.argv[1])
    root.file_name = filedialog.askopenfilename(initialdir=arg, title="Select file",filetypes=[("JS Files", "*.js")])
else:
    arg=FOLDER
    root.file_name = filedialog.askopenfilename(initialdir=arg, title="Select file",filetypes=[("JSON Files", "*.json")])


print(root.file_name)
