# Hotel Room Billing System

A professional desktop application for managing hotel room billing and generating receipts. Built with Python and Tkinter.

## Features

- **Room Management Dashboard**: Visual display of 6 rooms (101-106) with color-coded status
  - Green: Available rooms
  - Red: Occupied rooms
  
- **Billing Window**: Comprehensive billing form with:
  - Guest information entry
  - Check-in date selection
  - Days stayed calculation
  - Room charge per day
  - Automatic tax calculations (CGST 9%, SGST 9%)
  - Real-time total calculation

- **Professional PDF Receipts**: 
  - Hotel branding and details
  - Auto-generated receipt numbers
  - Complete billing breakdown
  - Tax calculations
  - Professional formatting

- **Database Persistence**: 
  - SQLite database for room status and bills
  - Data persists across application restarts
  - Complete billing history

- **Print Functionality**: 
  - Generate and print receipts directly
  - System print integration

## Requirements

- Python 3.6 or higher
- Tkinter (usually included with Python)
- reportlab library

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install reportlab
   ```

## Running the Application

1. **Start the application**:
   ```bash
   python main.py
   ```

2. **Using the application**:
   - The main dashboard shows all 6 rooms
   - Click on any room to open the billing window
   - Fill in guest details and billing information
   - Use "Generate Bill" to create and view the PDF receipt
   - Use "Print Receipt" to send the receipt directly to printer
   - Use "Checkout Room" to complete checkout and mark room as available

## Project Structure

```
.
├── main.py              # Application entry point
├── dashboard.py         # Main dashboard UI
├── billing_window.py    # Billing form window
├── receipt.py           # PDF receipt generator
├── database.py          # Database operations
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── hotel_billing.db    # SQLite database (created automatically)
└── receipts/           # Generated PDF receipts (created automatically)
```

## Database Schema

### Rooms Table
- `room_number` (TEXT, PRIMARY KEY)
- `status` (TEXT) - 'available' or 'occupied'

### Bills Table
- `bill_no` (TEXT, PRIMARY KEY)
- `guest_name` (TEXT)
- `room_number` (TEXT)
- `days` (INTEGER)
- `rate` (REAL)
- `subtotal` (REAL)
- `cgst` (REAL)
- `sgst` (REAL)
- `total` (REAL)
- `date` (TEXT)

## Features in Detail

### Room Status Management
- Rooms are automatically marked as "occupied" when billing window is opened
- Rooms are marked as "available" when checkout is completed
- Status persists across application restarts

### Bill Generation
- Auto-generated bill numbers (format: BILLYYYYMMDD####)
- Automatic tax calculations (CGST and SGST at 9% each)
- All bills are saved to database for record keeping

### Receipt Design
- Professional hotel branding
- Complete guest and billing information
- Itemized charges
- Tax breakdown
- Total amount highlighted

## Extending the Application

The code is modular and easy to extend. You can add:

- **Food Billing**: Add food items to the billing window
- **Extra Charges**: Add laundry, room service, etc.
- **Discounts**: Add discount calculation logic
- **Reports**: Generate daily/monthly reports from database
- **Search**: Search bills by guest name or date
- **Multiple Hotels**: Extend database schema for multiple properties

## Troubleshooting

### PDF not opening automatically
- On macOS/Linux, ensure you have a PDF viewer installed
- On Windows, ensure default PDF viewer is set

### Print not working
- Ensure you have a printer configured on your system
- Check printer permissions

### Database errors
- Ensure you have write permissions in the application directory
- Delete `hotel_billing.db` to reset the database (will lose all data)

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions, please check the code comments for detailed explanations of each module's functionality.

