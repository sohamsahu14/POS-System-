"""
Room Billing Window module for Hotel Room Billing System
Handles the billing form and calculations
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database import Database
from receipt import ReceiptGenerator


class BillingWindow:
    def __init__(self, parent, room_number, db, refresh_callback=None):
        """
        Initialize billing window
        
        Args:
            parent: Parent window
            room_number: Room number for billing
            db: Database instance
            refresh_callback: Callback to refresh dashboard
        """
        self.parent = parent
        self.room_number = room_number
        self.db = db
        self.refresh_callback = refresh_callback
        self.receipt_gen = ReceiptGenerator()
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Room {room_number} - Billing")
        self.window.geometry("500x650")  # Increased height for new checkout date field
        self.window.resizable(False, False)
        
        # Create UI
        self.create_widgets()
        
        # Center window (after widgets are created)
        self.center_window()
        
        # Focus on guest name field (after window is shown)
        self.window.after(100, lambda: self.guest_name_entry.focus())
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        if width > 0 and height > 0:  # Ensure window has been rendered
            x = (self.window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.window.winfo_screenheight() // 2) - (height // 2)
            self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create all UI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=f"Room {self.room_number} Billing",
                               font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Form fields frame
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Room Number (non-editable)
        ttk.Label(form_frame, text="Room Number:", font=('Helvetica', 10)).grid(
            row=0, column=0, sticky=tk.W, pady=10, padx=5)
        room_entry = ttk.Entry(form_frame, font=('Helvetica', 10), state='readonly')
        room_entry.insert(0, self.room_number)
        room_entry.grid(row=0, column=1, sticky=tk.EW, pady=10, padx=5)
        
        # Guest Name
        ttk.Label(form_frame, text="Guest Name:", font=('Helvetica', 10)).grid(
            row=1, column=0, sticky=tk.W, pady=10, padx=5)
        self.guest_name_entry = ttk.Entry(form_frame, font=('Helvetica', 10), width=30)
        self.guest_name_entry.grid(row=1, column=1, sticky=tk.EW, pady=10, padx=5)
        
        # Check-in Date
        ttk.Label(form_frame, text="Check-in Date:", font=('Helvetica', 10)).grid(
            row=2, column=0, sticky=tk.W, pady=10, padx=5)
        self.checkin_date_entry = ttk.Entry(form_frame, font=('Helvetica', 10), width=30)
        today = datetime.now().strftime('%d-%m-%Y')
        self.checkin_date_entry.insert(0, today)
        self.checkin_date_entry.grid(row=2, column=1, sticky=tk.EW, pady=10, padx=5)
        self.checkin_date_entry.bind('<KeyRelease>', self.on_date_change)
        self.checkin_date_entry.bind('<FocusOut>', self.on_date_change)
        
        # Check-out Date
        ttk.Label(form_frame, text="Check-out Date:", font=('Helvetica', 10)).grid(
            row=3, column=0, sticky=tk.W, pady=10, padx=5)
        self.checkout_date_entry = ttk.Entry(form_frame, font=('Helvetica', 10), width=30)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d-%m-%Y')
        self.checkout_date_entry.insert(0, tomorrow)
        self.checkout_date_entry.grid(row=3, column=1, sticky=tk.EW, pady=10, padx=5)
        self.checkout_date_entry.bind('<KeyRelease>', self.on_date_change)
        self.checkout_date_entry.bind('<FocusOut>', self.on_date_change)
        
        # Number of Nights (auto-calculated, read-only)
        ttk.Label(form_frame, text="Number of Nights:", font=('Helvetica', 10)).grid(
            row=4, column=0, sticky=tk.W, pady=10, padx=5)
        self.nights_entry = ttk.Entry(form_frame, font=('Helvetica', 10), width=30, state='readonly')
        self.nights_entry.insert(0, "1")
        self.nights_entry.grid(row=4, column=1, sticky=tk.EW, pady=10, padx=5)
        
        # Room Charge per Day
        ttk.Label(form_frame, text="Room Charge/Day (₹):", font=('Helvetica', 10)).grid(
            row=5, column=0, sticky=tk.W, pady=10, padx=5)
        self.rate_entry = ttk.Entry(form_frame, font=('Helvetica', 10), width=30)
        self.rate_entry.insert(0, "2000")
        self.rate_entry.grid(row=5, column=1, sticky=tk.EW, pady=10, padx=5)
        self.rate_entry.bind('<KeyRelease>', self.calculate_total)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        # Calculation frame
        calc_frame = ttk.Frame(main_frame)
        calc_frame.pack(fill=tk.BOTH, expand=True)
        
        # Subtotal
        ttk.Label(calc_frame, text="Subtotal:", font=('Helvetica', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.subtotal_label = ttk.Label(calc_frame, text="₹0.00", 
                                        font=('Helvetica', 10))
        self.subtotal_label.grid(row=0, column=1, sticky=tk.E, pady=5, padx=5)
        
        # CGST
        ttk.Label(calc_frame, text="CGST (9%):", font=('Helvetica', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.cgst_label = ttk.Label(calc_frame, text="₹0.00", 
                                   font=('Helvetica', 10))
        self.cgst_label.grid(row=1, column=1, sticky=tk.E, pady=5, padx=5)
        
        # SGST
        ttk.Label(calc_frame, text="SGST (9%):", font=('Helvetica', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.sgst_label = ttk.Label(calc_frame, text="₹0.00", 
                                   font=('Helvetica', 10))
        self.sgst_label.grid(row=2, column=1, sticky=tk.E, pady=5, padx=5)
        
        # Total
        ttk.Label(calc_frame, text="Total Amount:", 
                 font=('Helvetica', 12, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=10, padx=5)
        self.total_label = ttk.Label(calc_frame, text="₹0.00", 
                                     font=('Helvetica', 12, 'bold'),
                                     foreground='#c0392b')
        self.total_label.grid(row=3, column=1, sticky=tk.E, pady=10, padx=5)
        
        calc_frame.columnconfigure(1, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # Generate Bill button
        generate_btn = ttk.Button(button_frame, text="Generate Bill",
                                 command=self.generate_bill, width=18)
        generate_btn.pack(side=tk.LEFT, padx=3, expand=True)
        
        # Print Receipt button
        print_btn = ttk.Button(button_frame, text="Print Receipt",
                              command=self.print_receipt, width=18)
        print_btn.pack(side=tk.LEFT, padx=3, expand=True)
        
        # Checkout Room button
        checkout_btn = ttk.Button(button_frame, text="Checkout Room",
                                 command=self.checkout_room, width=18)
        checkout_btn.pack(side=tk.LEFT, padx=3, expand=True)
        
        # Initial calculation
        self.on_date_change()
    
    def parse_date(self, date_str):
        """Parse date string in DD-MM-YYYY format to datetime object"""
        try:
            return datetime.strptime(date_str.strip(), '%d-%m-%Y')
        except ValueError:
            return None
    
    def calculate_nights(self):
        """Calculate number of nights from check-in and check-out dates"""
        checkin_str = self.checkin_date_entry.get().strip()
        checkout_str = self.checkout_date_entry.get().strip()
        
        checkin_date = self.parse_date(checkin_str)
        checkout_date = self.parse_date(checkout_str)
        
        if checkin_date and checkout_date:
            nights = (checkout_date - checkin_date).days
            return max(1, nights) if nights >= 1 else None
        return None
    
    def on_date_change(self, event=None):
        """Handle date changes - recalculate nights and totals"""
        nights = self.calculate_nights()
        
        if nights is not None:
            # Update nights field (read-only)
            self.nights_entry.config(state='normal')
            self.nights_entry.delete(0, tk.END)
            self.nights_entry.insert(0, str(nights))
            self.nights_entry.config(state='readonly')
            
            # Recalculate totals
            self.calculate_total()
        else:
            # Invalid dates, clear nights
            self.nights_entry.config(state='normal')
            self.nights_entry.delete(0, tk.END)
            self.nights_entry.insert(0, "0")
            self.nights_entry.config(state='readonly')
            
            # Set totals to zero
            self.subtotal_label.config(text="₹0.00")
            self.cgst_label.config(text="₹0.00")
            self.sgst_label.config(text="₹0.00")
            self.total_label.config(text="₹0.00")
    
    def calculate_total(self, event=None):
        """Calculate subtotal, taxes, and total"""
        try:
            # Get nights from auto-calculation
            nights = self.calculate_nights()
            if nights is None or nights < 1:
                nights = 0
            
            rate = float(self.rate_entry.get() or 0)
            
            subtotal = nights * rate
            cgst = subtotal * 0.09
            sgst = subtotal * 0.09
            total = subtotal + cgst + sgst
            
            # Update labels
            self.subtotal_label.config(text=f"₹{subtotal:.2f}")
            self.cgst_label.config(text=f"₹{cgst:.2f}")
            self.sgst_label.config(text=f"₹{sgst:.2f}")
            self.total_label.config(text=f"₹{total:.2f}")
        except ValueError:
            # Invalid input, set to zero
            self.subtotal_label.config(text="₹0.00")
            self.cgst_label.config(text="₹0.00")
            self.sgst_label.config(text="₹0.00")
            self.total_label.config(text="₹0.00")
    
    def validate_inputs(self):
        """Validate all input fields"""
        if not self.guest_name_entry.get().strip():
            messagebox.showerror("Error", "Please enter guest name")
            return False
        
        # Validate dates
        checkin_str = self.checkin_date_entry.get().strip()
        checkout_str = self.checkout_date_entry.get().strip()
        
        checkin_date = self.parse_date(checkin_str)
        checkout_date = self.parse_date(checkout_str)
        
        if not checkin_date:
            messagebox.showerror("Error", "Please enter a valid check-in date (DD-MM-YYYY)")
            return False
        
        if not checkout_date:
            messagebox.showerror("Error", "Please enter a valid check-out date (DD-MM-YYYY)")
            return False
        
        # Validate checkout date > check-in date
        if checkout_date <= checkin_date:
            messagebox.showerror("Error", "Check-out date must be after check-in date")
            return False
        
        # Validate nights
        nights = self.calculate_nights()
        if nights is None or nights < 1:
            messagebox.showerror("Error", "Number of nights must be at least 1")
            return False
        
        try:
            rate = float(self.rate_entry.get())
            if rate <= 0:
                messagebox.showerror("Error", "Room charge must be greater than 0")
                return False
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid room charge")
            return False
        
        return True
    
    def get_bill_data(self):
        """Get bill data from form"""
        nights = self.calculate_nights()
        rate = float(self.rate_entry.get())
        subtotal = nights * rate
        cgst = subtotal * 0.09
        sgst = subtotal * 0.09
        total = subtotal + cgst + sgst
        
        bill_no = self.db.generate_bill_number()
        
        return {
            'bill_no': bill_no,
            'guest_name': self.guest_name_entry.get().strip(),
            'room_number': self.room_number,
            'check_in_date': self.checkin_date_entry.get().strip(),
            'checkout_date': self.checkout_date_entry.get().strip(),
            'nights': nights,
            'rate': rate,
            'subtotal': subtotal,
            'cgst': cgst,
            'sgst': sgst,
            'total': total,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def generate_bill(self):
        """Generate bill and save to database"""
        if not self.validate_inputs():
            return
        
        bill_data = self.get_bill_data()
        
        # Save to database
        try:
            self.db.save_bill(bill_data)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving bill: {str(e)}")
            return
        
        # Mark room as occupied after generating bill
        self.db.set_room_status(self.room_number, 'occupied')
        
        # Refresh dashboard to update room colors (force UI update)
        if self.refresh_callback:
            self.refresh_callback()
            # Ensure parent window updates
            self.parent.update_idletasks()
        
        # Generate PDF receipt
        try:
            filepath = self.receipt_gen.generate_receipt(bill_data)
            self.receipt_gen.open_pdf(filepath)
            messagebox.showinfo("Success", 
                              f"Bill generated successfully!\nBill No: {bill_data['bill_no']}\nReceipt saved to: {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating receipt: {str(e)}")
    
    def print_receipt(self):
        """Print the last generated receipt"""
        if not self.validate_inputs():
            return
        
        bill_data = self.get_bill_data()
        
        # Generate PDF receipt
        try:
            filepath = self.receipt_gen.generate_receipt(bill_data)
            self.receipt_gen.print_pdf(filepath)
            messagebox.showinfo("Success", "Receipt sent to printer!")
        except Exception as e:
            messagebox.showerror("Error", f"Error printing receipt: {str(e)}")
    
    def checkout_room(self):
        """Checkout room and mark as available"""
        if not self.validate_inputs():
            return
        
        # Generate bill first
        bill_data = self.get_bill_data()
        
        # Save to database
        try:
            self.db.save_bill(bill_data)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving bill: {str(e)}")
            return
        
        # Generate receipt
        try:
            filepath = self.receipt_gen.generate_receipt(bill_data)
            self.receipt_gen.open_pdf(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Error generating receipt: {str(e)}")
        
        # Mark room as available after checkout
        self.db.set_room_status(self.room_number, 'available')
        
        # Refresh dashboard to update room colors (force UI update)
        if self.refresh_callback:
            self.refresh_callback()
            # Ensure parent window updates before closing
            self.parent.update_idletasks()
        
        messagebox.showinfo("Success", 
                          f"Room {self.room_number} checked out successfully!\nBill No: {bill_data['bill_no']}")
        
        # Close window
        self.window.destroy()

