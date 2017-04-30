
import tkinter as tk
import os
import sys
try:
    # for Python2
    from Tkinter import *   ## notice capitalized T in Tkinter
except ImportError:
    # for Python3
    from tkinter import *   ## notice lowercase 't' in tkinter here


from tkinter import filedialog


path = os.path.realpath(__file__).split("\\")
path[len(path) - 1] = "";
FOLDER = "\\".join(path)

if sys.argv[0] is not "":
    arg=os.path.join(sys.argv[0])
else:
    arg=FOLDER

root = tk.Tk()
root.withdraw()
root.file_name = filedialog.askopenfilename(initialdir=FOLDER, title="Select file")
print(root.file_name)