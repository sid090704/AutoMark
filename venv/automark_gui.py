import tkinter as tk
from tkinter import scrolledtext


class AutoMarkGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AutoMark System")
        self.root.geometry("800x600")

        # Title Label
        self.title_label = tk.Label(self.root, text="AutoMark Attendance System", font=("Helvetica", 20))
        self.title_label.pack(pady=10)

        # Log Display (ScrolledText Widget)
        self.log_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Helvetica", 12))
        self.log_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Footer Section
        self.footer_frame = tk.Frame(self.root)
        self.footer_frame.pack(pady=10, side=tk.BOTTOM)

        # Quit Button
        self.quit_button = tk.Button(self.footer_frame, text="Quit", font=("Helvetica", 14), command=self.quit_app)
        self.quit_button.pack(side=tk.RIGHT, padx=10)

    def log_message(self, message):
        """Logs a message to the GUI."""
        self.log_display.insert(tk.END, f"{message}\n")
        self.log_display.see(tk.END)

    def update_display(self):
        """Keeps the GUI responsive while the main system runs."""
        self.root.update_idletasks()
        self.root.update()

    def quit_app(self):
        """Exits the application."""
        self.root.destroy()


# Create a single instance of the GUI
gui = AutoMarkGUI()
