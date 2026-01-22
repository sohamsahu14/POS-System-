"""
Main entry point for Hotel Room Billing System
"""

import tkinter as tk
from dashboard import Dashboard


def main():
    """Main function to start the application"""
    # Create root window
    root = tk.Tk()
    
    # Initialize dashboard
    app = Dashboard(root)
    
    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    main()

