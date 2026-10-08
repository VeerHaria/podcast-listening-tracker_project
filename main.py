"""Run this file to start the application:  python main.py"""
import tkinter as tk
from tkinter import messagebox

import storage
from gui import App

try:
    podcasts, episodes = storage.load_all()
except ValueError as error:
    tk.Tk().withdraw()
    messagebox.showerror("Cannot load data", str(error))
else:
    App(podcasts, episodes).mainloop()
