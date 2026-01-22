"""
Main Dashboard module for Hotel Room Billing System
Displays room status and handles room selection
"""

import tkinter as tk
from tkinter import ttk
from billing_window import BillingWindow
from database import Database


class Dashboard:
    def __init__(self, root):
        """
        Initialize main dashboard
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.db = Database()
        
        # Configure root window
        self.root.title("Hotel Room Billing System")
        # Open covering the entire screen (cross-platform) without changing widget/layout logic
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_w}x{screen_h}+0+0")
        self.root.resizable(False, True)
        
        # Create UI
        self.create_widgets()
        
        # Note: keep existing widgets/layout unchanged; window is already sized to screen
        
        # Initial room status update
        self.update_room_status()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        if width > 0 and height > 0:  # Ensure window has been rendered
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create all UI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Hotel Room Billing System",
                               font=('Helvetica', 24, 'bold'))
        title_label.pack(pady=(0, 30))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, text="Select a room to manage billing",
                                  font=('Helvetica', 12))
        subtitle_label.pack(pady=(0, 30))
        
        # Rooms frame
        rooms_frame = ttk.Frame(main_frame)
        rooms_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create room buttons
        self.room_buttons = {}
        room_numbers = ['101', '102', '103', '104', '105', '106']
        
        # Configure grid
        for i in range(3):
            rooms_frame.columnconfigure(i, weight=1, uniform='room_col')
        for i in range(2):
            rooms_frame.rowconfigure(i, weight=1, uniform='room_row')
        
        # Create buttons in 3x2 grid
        for idx, room_num in enumerate(room_numbers):
            row = idx // 3
            col = idx % 3
            
            # Create button with custom styling
            btn = tk.Button(rooms_frame, 
                          text=f"Room {room_num}",
                          font=('Helvetica', 16, 'bold'),
                          command=lambda rn=room_num: self.open_billing_window(rn),
                          relief=tk.RAISED,
                          borderwidth=3,
                          cursor='hand1',
                          padx=20,
                          pady=20)
            
            btn.grid(row=row, column=col, sticky=tk.NSEW, padx=10, pady=10)
            
            # Store button reference
            self.room_buttons[room_num] = btn
        
        # Status legend
        legend_frame = ttk.Frame(main_frame)
        legend_frame.pack(pady=20)
        
        # Available indicator
        available_indicator = tk.Label(legend_frame, text="●", 
                                      font=('Helvetica', 20),
                                      foreground='#27ae60')
        available_indicator.pack(side=tk.LEFT, padx=5)
        ttk.Label(legend_frame, text="Available", 
                 font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        
        # Occupied indicator
        occupied_indicator = tk.Label(legend_frame, text="●", 
                                     font=('Helvetica', 20),
                                     foreground='#e74c3c')
        occupied_indicator.pack(side=tk.LEFT, padx=20)
        ttk.Label(legend_frame, text="Occupied", 
                 font=('Helvetica', 10)).pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        refresh_btn = ttk.Button(main_frame, text="Refresh Status",
                                command=self.update_room_status)
        refresh_btn.pack(pady=10)
    
    def update_room_status(self):
        """Update room status display - always fetches fresh data from database"""
        # Force refresh from database (do not use cached state)
        rooms_status = self.db.get_all_rooms_status()
        
        # Update each room button color based on current database status
        for room_num, button in self.room_buttons.items():
            status = rooms_status.get(room_num, 'available')
            
            if status == 'available':
                button.config(bg='#d5f4e6', activebackground='#a8e6cf',
                            foreground='#27ae60')
            else:  # occupied
                button.config(bg='#fadbd8', activebackground='#f1948a',
                            foreground='#e74c3c')
        
        # Force UI update to ensure colors are repainted
        self.root.update_idletasks()
    
    def open_billing_window(self, room_number):
        """Open billing window for selected room"""
        # Check if room is occupied
        status = self.db.get_room_status(room_number)
        
        if status == 'available':
            # Mark room as occupied when opening billing
            self.db.set_room_status(room_number, 'occupied')
            self.update_room_status()
        
        # Open billing window
        BillingWindow(self.root, room_number, self.db, 
                     refresh_callback=self.update_room_status)
    
    def refresh_dashboard(self):
        """Public method to refresh dashboard (called from billing window)"""
        self.update_room_status()

