# 🅿️ Smart Park System - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Dashboard Overview](#dashboard-overview)
4. [Vehicle Management](#vehicle-management)
5. [Reservations](#reservations)
6. [Reports & Analytics](#reports--analytics)
7. [Admin Panel](#admin-panel)
8. [Troubleshooting](#troubleshooting)

---

## Introduction

Welcome to the Smart Park System! This intelligent parking management solution helps you:
- Monitor parking availability in real-time
- Manage vehicle entry and exit efficiently
- Process payments automatically
- Handle reservations seamlessly
- Track revenue and usage analytics

---

## Getting Started

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r reqiuirements.txt
   ```

2. **Start the application:**
   ```bash
   streamlit run smart_park.py
   ```
   
   Or use the quick start script:
   ```bash
   ./start_smart_park.sh
   ```

3. **Access the application:**
   Open your browser and go to: `http://localhost:8501`

### Generate Demo Data (Optional)

To populate the system with sample data for testing:
```bash
python3 generate_demo_data.py
```

---

## Dashboard Overview

The dashboard provides a real-time view of your parking facility:

### Key Metrics
- **Total Spots**: Total number of parking spaces
- **Available**: Number of free parking spots
- **Occupied**: Number of spots currently in use
- **Reserved**: Number of spots reserved for future use
- **Occupancy Rate**: Percentage of occupied spots

### Parking Grid
The visual grid shows all parking spots organized by floor:
- 🟢 **Green spots**: Available for parking
- 🔴 **Red spots**: Currently occupied
- 🟣 **Purple spots**: Reserved for bookings

Each spot displays:
- Spot ID (e.g., A01, B05, C12)
- Hourly rate

---

## Vehicle Management

### Vehicle Entry (Check-in)

**Steps:**
1. Click on **"🚗 Vehicle Entry"** in the sidebar
2. Fill in the required information:
   - **Vehicle Registration Number**: Enter the plate number
   - **Vehicle Type**: Select from car, motorcycle, truck, or van
   - **Driver Name**: Enter the driver's name
   - **Phone Number**: Enter contact number
3. **Select Parking Spot**: Choose from available spots
4. **Set Entry Time**: Current time is pre-filled, adjust if needed
5. Click **"✅ Check In Vehicle"**

**What happens next:**
- Vehicle is registered in the system
- Selected spot status changes to "occupied"
- Entry timestamp is recorded
- Billing timer starts

### Vehicle Exit (Check-out)

**Steps:**
1. Click on **"🚪 Vehicle Exit"** in the sidebar
2. **Select Vehicle**: Choose from the dropdown list showing all parked vehicles
3. Review the **Vehicle Details**:
   - Registration number
   - Driver name
   - Vehicle type
   - Parking spot
   - Entry time
4. **Set Exit Time**: Current time is pre-filled
5. Review **Parking Summary**:
   - Duration (calculated automatically)
   - Hourly rate
   - **Total cost**
6. **Select Payment Method**: Cash, Credit Card, Debit Card, or Mobile Payment
7. Click **"💳 Process Exit & Payment"**

**What happens next:**
- Parking duration and cost are calculated
- Transaction is recorded
- Parking spot becomes available
- Vehicle status changes to "completed"
- Receipt information is displayed

---

## Reservations

### Making a Reservation

**Steps:**
1. Click on **"📅 Reservations"** in the sidebar
2. Fill in customer details:
   - **Vehicle Registration**: Future vehicle plate number
   - **Customer Name**: Name of the person making reservation
   - **Phone Number**: Contact number
   - **Email**: Email address for confirmation
3. Select reservation details:
   - **Select Spot**: Choose from available spots
   - **Reservation Date**: Pick the date
   - **Reservation Time**: Set the arrival time
   - **Duration**: Specify how many hours
4. Review the **Total Cost**
5. Click **"📅 Confirm Reservation"**

**What happens next:**
- Booking is confirmed with a unique Booking ID
- Selected spot is marked as "reserved"
- Booking details are stored
- Confirmation message is displayed

### Managing Bookings
View all active bookings in the **Admin Panel** → **View Bookings** tab

---

## Reports & Analytics

Access comprehensive analytics by clicking **"📊 Reports"** in the sidebar.

### Revenue Metrics
- **Total Revenue**: All-time revenue from parking fees
- **Total Transactions**: Number of completed transactions
- **Average Transaction**: Average parking fee per transaction

### Recent Transactions Table
View the last 10 transactions with:
- Vehicle registration number
- Parking spot used
- Duration of parking
- Amount paid
- Payment method
- Timestamp

### Payment Methods Chart
Visual breakdown of payment methods used by customers

### Use Cases
- **Daily reconciliation**: Check total revenue for the day
- **Trend analysis**: Identify peak usage times
- **Payment preferences**: Understand customer payment habits
- **Audit trail**: Complete transaction history

---

## Admin Panel

Access administrative features by clicking **"⚙️ Admin Panel"** in the sidebar.

### Manage Spots Tab

**View All Spots:**
- See complete list of parking spots
- Check status of each spot
- View rates and configurations

**Add New Parking Spot:**
1. Click on **"➕ Add New Parking Spot"** expander
2. Enter:
   - **Spot ID**: Unique identifier (e.g., D01)
   - **Floor**: Select floor level
   - **Rate/Hour**: Set hourly rate in dollars
3. Click **"Add Spot"**

### View Bookings Tab
- See all active reservations
- Check booking details
- Monitor upcoming arrivals

### System Settings Tab
- Configure system parameters
- Access danger zone for data reset
- **⚠️ Reset All Data**: Completely wipe the database (use with caution)

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: Application won't start
**Solution:**
```bash
# Check Python version (needs 3.8+)
python3 --version

# Reinstall dependencies
pip3 install -r reqiuirements.txt --force-reinstall

# Try alternate port
streamlit run smart_park.py --server.port 8502
```

#### Issue: Database errors
**Solution:**
1. Go to Admin Panel
2. Navigate to System Settings
3. Use "Reset All Data" option
4. Restart the application

#### Issue: Spot not showing as available after checkout
**Solution:**
- Refresh the page (F5 or Ctrl+R)
- Check if transaction was completed properly
- Verify in Admin Panel → Manage Spots

#### Issue: Port 8501 already in use
**Solution:**
```bash
# Find and kill process using port 8501
lsof -ti:8501 | xargs kill -9

# Or use a different port
streamlit run smart_park.py --server.port 8502
```

#### Issue: Missing dependencies
**Solution:**
```bash
# Install individual packages
pip3 install streamlit pandas plotly
```

### Getting Help

1. **Check the logs**: Look for error messages in the terminal
2. **Review the README**: See SMART_PARK_README.md for technical details
3. **Test with demo data**: Use `generate_demo_data.py` to test functionality
4. **Run tests**: Execute `test_smart_park.py` to verify system integrity

---

## Tips & Best Practices

### For Operators
1. **Regular reconciliation**: Check reports daily to track revenue
2. **Monitor occupancy**: Use dashboard to identify peak times
3. **Maintain availability**: Process exits promptly to free up spots
4. **Handle reservations**: Check bookings tab for upcoming arrivals
5. **Backup data**: Periodically backup `parking_data.json`

### For Administrators
1. **Set appropriate rates**: Adjust rates based on demand and location
2. **Add capacity**: Add new spots as needed through Admin Panel
3. **Review analytics**: Use reports to make informed decisions
4. **Data management**: Regular data cleanup for old transactions
5. **System maintenance**: Keep the application updated

### Security Recommendations
1. **Access control**: Implement user authentication for production use
2. **Secure database**: Protect `parking_data.json` with proper permissions
3. **Backup regularly**: Keep multiple backups of the database
4. **Monitor access**: Track who accesses the admin panel
5. **Audit logs**: Review transaction logs regularly

---

## Quick Reference

### Keyboard Shortcuts (Browser)
- **F5** or **Ctrl+R**: Refresh the page
- **Ctrl+Plus**: Zoom in
- **Ctrl+Minus**: Zoom out
- **F11**: Toggle fullscreen

### Status Color Codes
- 🟢 **Green**: Available
- 🔴 **Red**: Occupied
- 🟣 **Purple**: Reserved

### Default Rates
- **Floor A**: $5/hour (Premium)
- **Floor B**: $4/hour (Standard)
- **Floor C**: $3/hour (Economy)

### System Capacity
- **Floors**: 3 (A, B, C)
- **Spots per floor**: 20
- **Total capacity**: 60 vehicles

---

## Feature Highlights

### ✅ What the System Does
- Real-time spot availability tracking
- Automated time and cost calculation
- Multiple payment method support
- Advanced booking system
- Comprehensive reporting
- Multi-floor management
- Visual parking grid
- Transaction history
- Revenue analytics

### 🔄 Automatic Processes
- Duration calculation based on entry/exit times
- Cost calculation using spot rates
- Spot status updates (available/occupied/reserved)
- Transaction logging
- Revenue aggregation
- Occupancy rate calculation

### 📊 Data Tracked
- Vehicle information
- Driver details
- Parking duration
- Payment information
- Booking details
- Revenue metrics
- Usage statistics
- Transaction history

---

## Appendix

### File Locations
- **Application**: `smart_park.py`
- **Database**: `parking_data.json` (auto-generated)
- **Tests**: `test_smart_park.py`
- **Demo data**: `generate_demo_data.py`
- **Documentation**: `SMART_PARK_README.md`, `USER_GUIDE.md`

### Database Structure
```json
{
  "parking_spots": [...],    // All parking spot definitions
  "vehicles": [...],          // Active and completed vehicle records
  "bookings": [...],          // Reservation records
  "transactions": [...]       // Completed payment transactions
}
```

### Support
For technical details and API documentation, refer to:
- `SMART_PARK_README.md` - Technical documentation
- `README.md` - Project overview
- Code comments in `smart_park.py`

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**License**: Educational Use
