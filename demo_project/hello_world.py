#!/usr/bin/env python3
"""
Hello World Demo Project
A simple demonstration of the App Program Writer capabilities
"""

import tkinter as tk
from tkinter import messagebox
import datetime

class HelloWorldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hello World - App Program Writer Demo")
        self.root.geometry("400x300")
        self.root.configure(bg='#2b2b2b')
        
        # Create main frame
        main_frame = tk.Frame(root, bg='#2b2b2b')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Title label
        title_label = tk.Label(main_frame, 
                              text="Hello World!", 
                              font=('Arial', 24, 'bold'),
                              fg='#ffffff',
                              bg='#2b2b2b')
        title_label.pack(pady=20)
        
        # Welcome message
        welcome_label = tk.Label(main_frame,
                                text="Welcome to App Program Writer!",
                                font=('Arial', 12),
                                fg='#cccccc',
                                bg='#2b2b2b')
        welcome_label.pack(pady=10)
        
        # Current time button
        time_button = tk.Button(main_frame,
                               text="Show Current Time",
                               command=self.show_time,
                               bg='#4c5052',
                               fg='#ffffff',
                               font=('Arial', 10),
                               relief='flat',
                               padx=20,
                               pady=10)
        time_button.pack(pady=20)
        
        # Features list
        features_frame = tk.Frame(main_frame, bg='#2b2b2b')
        features_frame.pack(pady=20)
        
        features = [
            "✓ Multi-language support",
            "✓ Project management",
            "✓ Code execution",
            "✓ Auto-save functionality",
            "✓ Search and replace",
            "✓ Modern dark theme UI"
        ]
        
        for feature in features:
            feature_label = tk.Label(features_frame,
                                   text=feature,
                                   font=('Arial', 10),
                                   fg='#00ff00',
                                   bg='#2b2b2b')
            feature_label.pack(anchor='w')
        
        # Exit button
        exit_button = tk.Button(main_frame,
                               text="Exit",
                               command=root.quit,
                               bg='#cc3333',
                               fg='#ffffff',
                               font=('Arial', 10),
                               relief='flat',
                               padx=20,
                               pady=5)
        exit_button.pack(side='bottom', pady=20)
    
    def show_time(self):
        """Display current time in a message box"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messagebox.showinfo("Current Time", f"The current time is:\n{current_time}")

def main():
    """Main function to run the demo app"""
    root = tk.Tk()
    app = HelloWorldApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
