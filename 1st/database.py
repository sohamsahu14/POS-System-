"""
Database module for Hotel Room Billing System
Handles all SQLite database operations
"""

import sqlite3
import os
from datetime import datetime


class Database:
    def __init__(self, db_name='hotel_billing.db'):
        """Initialize database connection and create tables if they don't exist"""
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create rooms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                room_number TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'available'
            )
        ''')
        
        # Check if bills table exists and what schema it has
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bills'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # Get current schema
            cursor.execute("PRAGMA table_info(bills)")
            columns = {column[1]: column for column in cursor.fetchall()}
            
            # Check if old schema exists (has 'days' but not 'nights')
            has_days = 'days' in columns
            has_nights = 'nights' in columns
            has_checkin = 'check_in_date' in columns
            has_checkout = 'checkout_date' in columns
            
            if has_days and not has_nights:
                # Old schema detected - need to migrate
                # SQLite doesn't support DROP COLUMN, so we recreate the table
                # Step 1: Create new table with correct schema
                cursor.execute('''
                    CREATE TABLE bills_new (
                        bill_no TEXT PRIMARY KEY,
                        guest_name TEXT NOT NULL,
                        room_number TEXT NOT NULL,
                        check_in_date TEXT NOT NULL,
                        checkout_date TEXT NOT NULL,
                        nights INTEGER NOT NULL,
                        rate REAL NOT NULL,
                        subtotal REAL NOT NULL,
                        cgst REAL NOT NULL,
                        sgst REAL NOT NULL,
                        total REAL NOT NULL,
                        date TEXT NOT NULL,
                        FOREIGN KEY (room_number) REFERENCES rooms(room_number)
                    )
                ''')
                
                # Step 2: Migrate existing data using column names (safer than indices)
                # Old schema: bill_no, guest_name, room_number, days, rate, subtotal, cgst, sgst, total, date
                cursor.execute('''
                    INSERT INTO bills_new 
                    (bill_no, guest_name, room_number, check_in_date, checkout_date, 
                     nights, rate, subtotal, cgst, sgst, total, date)
                    SELECT 
                        bill_no,
                        guest_name,
                        room_number,
                        COALESCE(date, datetime('now')) as check_in_date,
                        COALESCE(date, datetime('now')) as checkout_date,
                        days as nights,
                        rate,
                        subtotal,
                        cgst,
                        sgst,
                        total,
                        COALESCE(date, datetime('now')) as date
                    FROM bills
                ''')
                
                # Step 3: Drop old table and rename new one
                cursor.execute('DROP TABLE bills')
                cursor.execute('ALTER TABLE bills_new RENAME TO bills')
            elif not has_nights:
                # Table exists but missing nights column - add it
                cursor.execute('ALTER TABLE bills ADD COLUMN check_in_date TEXT')
                cursor.execute('ALTER TABLE bills ADD COLUMN checkout_date TEXT')
                cursor.execute('ALTER TABLE bills ADD COLUMN nights INTEGER')
                
                # Set default values for existing records
                cursor.execute('''
                    UPDATE bills 
                    SET nights = COALESCE((SELECT days FROM bills WHERE bills.bill_no = bills.bill_no), 1),
                        check_in_date = COALESCE(date, datetime('now')),
                        checkout_date = COALESCE(date, datetime('now'))
                    WHERE nights IS NULL
                ''')
        else:
            # Table doesn't exist - create with new schema
            cursor.execute('''
                CREATE TABLE bills (
                    bill_no TEXT PRIMARY KEY,
                    guest_name TEXT NOT NULL,
                    room_number TEXT NOT NULL,
                    check_in_date TEXT NOT NULL,
                    checkout_date TEXT NOT NULL,
                    nights INTEGER NOT NULL,
                    rate REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    cgst REAL NOT NULL,
                    sgst REAL NOT NULL,
                    total REAL NOT NULL,
                    date TEXT NOT NULL,
                    FOREIGN KEY (room_number) REFERENCES rooms(room_number)
                )
            ''')
        
        # Initialize rooms if they don't exist
        for room_num in ['101', '102', '103', '104', '105', '106']:
            cursor.execute('''
                INSERT OR IGNORE INTO rooms (room_number, status)
                VALUES (?, 'available')
            ''', (room_num,))
        
        conn.commit()
        conn.close()
    
    def get_room_status(self, room_number):
        """Get status of a specific room"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT status FROM rooms WHERE room_number = ?', (room_number,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 'available'
    
    def get_all_rooms_status(self):
        """Get status of all rooms"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT room_number, status FROM rooms ORDER BY room_number')
        rooms = cursor.fetchall()
        conn.close()
        return {room[0]: room[1] for room in rooms}
    
    def set_room_status(self, room_number, status):
        """Update room status (available/occupied)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE rooms SET status = ? WHERE room_number = ?
        ''', (status, room_number))
        conn.commit()
        conn.close()
    
    def generate_bill_number(self):
        """Generate unique bill number"""
        conn = self.get_connection()
        cursor = conn.cursor()
        date_str = datetime.now().strftime('%Y%m%d')
        cursor.execute('''
            SELECT COUNT(*) FROM bills WHERE bill_no LIKE ?
        ''', (f'BILL{date_str}%',))
        count = cursor.fetchone()[0]
        conn.close()
        bill_no = f'BILL{date_str}{str(count + 1).zfill(4)}'
        return bill_no
    
    def save_bill(self, bill_data):
        """Save bill to database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bills (bill_no, guest_name, room_number, check_in_date, checkout_date, 
                                 nights, rate, subtotal, cgst, sgst, total, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                bill_data['bill_no'],
                bill_data['guest_name'],
                bill_data['room_number'],
                bill_data['check_in_date'],
                bill_data['checkout_date'],
                bill_data['nights'],
                bill_data['rate'],
                bill_data['subtotal'],
                bill_data['cgst'],
                bill_data['sgst'],
                bill_data['total'],
                bill_data['date']
            ))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            conn.close()
            raise Exception(f"Database error: {str(e)}")
    
    def get_bill(self, bill_no):
        """Retrieve bill from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bills WHERE bill_no = ?', (bill_no,))
        bill = cursor.fetchone()
        conn.close()
        return bill

