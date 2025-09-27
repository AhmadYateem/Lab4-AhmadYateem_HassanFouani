# Run the Tkinter UI (uses the App class defined in submission/part4_database.py)
import tkinter as tk
from submission.part4_database import App, init_db

if __name__ == "__main__":
    init_db()  # ensure DB exists
    root = tk.Tk()
    App(root)
    root.mainloop()
