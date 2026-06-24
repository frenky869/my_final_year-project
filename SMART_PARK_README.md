# 🅿️ Smart Park System

## Overview
Smart Park System is an intelligent parking management solution that provides real-time monitoring, automated billing, and comprehensive parking spot management. Built with Python and Streamlit, it offers a modern, user-friendly interface for managing parking operations efficiently.

## Features

### 🚗 Core Functionality
- **Real-time Parking Monitoring**: Track parking spot availability in real-time
- **Vehicle Entry/Exit Management**: Seamless check-in and check-out process
- **Automated Billing**: Calculate parking fees automatically based on duration
- **Reservation System**: Allow customers to reserve parking spots in advance
- **Multi-floor Support**: Manage parking across multiple floors (A, B, C)

### 📊 Analytics & Reporting
- **Revenue Tracking**: Monitor total revenue and transaction history
- **Occupancy Statistics**: Real-time occupancy rates and utilization metrics
- **Payment Analytics**: Breakdown of payment methods and transaction volumes
- **Historical Reports**: Access historical parking data and trends

### ⚙️ Admin Features
- **Spot Management**: Add, edit, and manage parking spots
- **Booking Management**: View and manage reservations
- **Rate Configuration**: Set different rates for different floors/zones
- **System Configuration**: Customize system settings

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone or download the repository**
```bash
cd /path/to/my_final_year-project
```

2. **Install dependencies**
```bash
pip install -r reqiuirements.txt
```

3. **Run the application**
```bash
streamlit run smart_park.py
```

4. **Access the application**
Open your browser and navigate to:
```
http://localhost:8501
```

## Usage Guide

### 1. Dashboard
- View real-time statistics (total spots, available, occupied, reserved)
- Monitor occupancy rates
- See visual parking grid with color-coded status:
  - **Green**: Available spots
  - **Red**: Occupied spots
  - **Purple**: Reserved spots

### 2. Vehicle Entry
To register a new vehicle:
1. Navigate to "Vehicle Entry" from the sidebar
2. Enter vehicle registration number
3. Select vehicle type (car, motorcycle, truck, van)
4. Provide driver details (name and phone)
5. Select an available parking spot
6. Set entry time
7. Click "Check In Vehicle"

### 3. Vehicle Exit
To process vehicle exit:
1. Navigate to "Vehicle Exit"
2. Select the vehicle from the dropdown
3. Review vehicle details and parking information
4. Set exit time
5. Review calculated charges:
   - Duration in hours
   - Rate per hour
   - Total amount
6. Select payment method
7. Click "Process Exit & Payment"

### 4. Reservations
To make a reservation:
1. Navigate to "Reservations"
2. Enter customer and vehicle details
3. Select desired parking spot
4. Choose reservation date and time
5. Specify duration
6. Review total cost
7. Click "Confirm Reservation"

### 5. Reports
View comprehensive analytics:
- Total revenue generated
- Number of transactions
- Average transaction value
- Recent transaction history
- Payment method breakdown

### 6. Admin Panel
Administrative features:
- **Manage Spots**: View all spots, add new spots, configure rates
- **View Bookings**: Monitor all active reservations
- **System Settings**: Configure system parameters
- **Reset Data**: Clear all data (use with caution)

## System Architecture

### Data Storage
The system uses a JSON-based database (`parking_data.json`) with four main collections:

1. **parking_spots**: Stores parking spot information
   - Spot ID, floor, status, vehicle type, rate per hour

2. **vehicles**: Records vehicle entries and exits
   - Vehicle details, driver info, entry/exit times, status

3. **bookings**: Manages reservations
   - Customer details, spot allocation, booking time, duration

4. **transactions**: Tracks all financial transactions
   - Payment details, duration, amounts, timestamps

### Parking Spot Status
- **available**: Spot is free and ready for use
- **occupied**: Spot is currently in use
- **reserved**: Spot is booked for future use

## Default Configuration

### Parking Structure
- **3 Floors**: A, B, C
- **20 Spots per floor**: Total 60 spots
- **Rate Structure**:
  - Floor A: $5/hour (premium)
  - Floor B: $4/hour (standard)
  - Floor C: $3/hour (economy)

### Payment Methods
- Cash
- Credit Card
- Debit Card
- Mobile Payment

## Technical Details

### Technology Stack
- **Framework**: Streamlit 1.28.2
- **Data Processing**: Pandas 2.1.3
- **Visualization**: Plotly 5.18.0
- **Language**: Python 3.x

### File Structure
```
my_final_year-project/
├── smart_park.py           # Main application file
├── parking_data.json       # Database file (auto-generated)
├── reqiuirements.txt       # Python dependencies
├── SMART_PARK_README.md    # This file
└── README.md              # Original project README
```

## Features Breakdown

### Real-time Dashboard
- Live parking spot visualization
- Color-coded status indicators
- Floor-wise organization
- Occupancy metrics
- Revenue tracking

### Vehicle Management
- Quick check-in process
- Automated time tracking
- Multiple vehicle type support
- Driver information storage
- Historical records

### Billing System
- Automatic duration calculation
- Variable rate support
- Multiple payment methods
- Transaction receipts
- Revenue reporting

### Reservation System
- Advance booking capability
- Customer information management
- Confirmation system
- Booking history
- Spot allocation

## Customization

### Adding More Floors
Edit the `init_database()` function in `smart_park.py`:
```python
for floor in ['A', 'B', 'C', 'D', 'E']:  # Add more floors
    for spot_num in range(1, 21):
        # ... spot creation code
```

### Changing Rates
Modify the rate structure in the spot creation code:
```python
"rate_per_hour": 5.0 if floor == 'A' else 4.0 if floor == 'B' else 3.0
```

### Adding Vehicle Types
Update the vehicle type options in the entry form:
```python
vehicle_type = st.selectbox("Vehicle Type", ["car", "motorcycle", "truck", "van", "bus", "bicycle"])
```

## Troubleshooting

### Database Issues
If you encounter database errors:
1. Navigate to Admin Panel
2. Use the "Reset All Data" option
3. Restart the application

### Port Already in Use
If port 8501 is busy:
```bash
streamlit run smart_park.py --server.port 8502
```

### Missing Dependencies
Reinstall all packages:
```bash
pip install -r reqiuirements.txt --force-reinstall
```

## Future Enhancements

Potential features for future versions:
- Mobile app integration
- License plate recognition (LPR)
- IoT sensor integration
- Email/SMS notifications
- Multi-tenant support
- Advanced analytics dashboard
- QR code-based entry/exit
- Integration with payment gateways
- Camera surveillance integration
- Automated barrier control

## Support

For issues or questions:
1. Check this README for common solutions
2. Review the code comments in `smart_park.py`
3. Test with sample data first
4. Use the Admin Panel to reset if needed

## License

This project is part of a final year project for educational purposes.

## Acknowledgments

Built with:
- Streamlit for the web framework
- Pandas for data management
- Plotly for visualizations
- Python for backend logic

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Author**: Final Year Project Team
