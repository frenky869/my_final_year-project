#!/usr/bin/env python3
"""
Generate demo data for Smart Park System
"""

import sys
from pathlib import Path
import datetime
import random

# Add the project directory to path (use relative path)
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from smart_park import DB_PATH, init_database, load_database, save_database

def generate_demo_data():
    """Generate comprehensive demo data"""
    print("🎬 Generating demo data for Smart Park System...")
    
    # Initialize fresh database
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_database()
    
    data = load_database()
    
    # Sample vehicle data
    sample_vehicles = [
        ("ABC-1234", "John Smith", "+1-555-0101", "car"),
        ("XYZ-5678", "Sarah Johnson", "+1-555-0102", "motorcycle"),
        ("DEF-9012", "Mike Brown", "+1-555-0103", "car"),
        ("GHI-3456", "Emily Davis", "+1-555-0104", "van"),
        ("JKL-7890", "David Wilson", "+1-555-0105", "car"),
    ]
    
    # Add some parked vehicles
    print("  Adding parked vehicles...")
    occupied_spots = ["A01", "A05", "B03", "B07", "C02"]
    
    for i, (plate, name, phone, vtype) in enumerate(sample_vehicles):
        spot = occupied_spots[i]
        entry_time = datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 5))
        
        vehicle = {
            "id": i + 1,
            "vehicle_number": plate,
            "vehicle_type": vtype,
            "driver_name": name,
            "driver_phone": phone,
            "spot_id": spot,
            "entry_time": str(entry_time),
            "exit_time": None,
            "status": "parked"
        }
        
        data["vehicles"].append(vehicle)
        
        # Update spot status
        for s in data["parking_spots"]:
            if s["id"] == spot:
                s["status"] = "occupied"
                break
    
    print(f"  ✅ Added {len(sample_vehicles)} parked vehicles")
    
    # Add some bookings
    print("  Adding reservations...")
    reserved_spots = ["A10", "B12", "C15"]
    booking_customers = [
        ("RSV-001", "Alice Cooper", "+1-555-0201", "alice@example.com"),
        ("RSV-002", "Bob Martin", "+1-555-0202", "bob@example.com"),
        ("RSV-003", "Carol White", "+1-555-0203", "carol@example.com"),
    ]
    
    for i, (plate, name, phone, email) in enumerate(booking_customers):
        spot = reserved_spots[i]
        booking_time = datetime.time(14 + i, 0)
        
        booking = {
            "id": i + 1,
            "vehicle_number": plate,
            "customer_name": name,
            "customer_phone": phone,
            "customer_email": email,
            "spot_id": spot,
            "booking_date": str(datetime.date.today()),
            "booking_time": str(booking_time),
            "duration_hours": random.randint(2, 4),
            "total_cost": round(random.uniform(8, 20), 2),
            "status": "confirmed",
            "created_at": str(datetime.datetime.now())
        }
        
        data["bookings"].append(booking)
        
        # Update spot status
        for s in data["parking_spots"]:
            if s["id"] == spot:
                s["status"] = "reserved"
                break
    
    print(f"  ✅ Added {len(booking_customers)} reservations")
    
    # Add some completed transactions
    print("  Adding transaction history...")
    past_vehicles = [
        ("OLD-1111", "A02", 3.5, 5.0),
        ("OLD-2222", "B04", 2.0, 4.0),
        ("OLD-3333", "C05", 5.5, 3.0),
        ("OLD-4444", "A08", 1.5, 5.0),
        ("OLD-5555", "B09", 4.0, 4.0),
        ("OLD-6666", "C10", 2.5, 3.0),
        ("OLD-7777", "A15", 6.0, 5.0),
        ("OLD-8888", "B18", 3.0, 4.0),
    ]
    
    payment_methods = ["Cash", "Credit Card", "Debit Card", "Mobile Payment"]
    
    for i, (plate, spot, hours, rate) in enumerate(past_vehicles):
        exit_time = datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 24))
        entry_time = exit_time - datetime.timedelta(hours=hours)
        
        transaction = {
            "id": i + 1,
            "vehicle_id": 100 + i,
            "vehicle_number": plate,
            "spot_id": spot,
            "entry_time": str(entry_time),
            "exit_time": str(exit_time),
            "duration_hours": round(hours, 2),
            "rate_per_hour": rate,
            "total_amount": round(hours * rate, 2),
            "payment_method": random.choice(payment_methods),
            "timestamp": str(exit_time)
        }
        
        data["transactions"].append(transaction)
    
    print(f"  ✅ Added {len(past_vehicles)} completed transactions")
    
    # Save all data
    save_database(data)
    
    # Print summary
    print("\n" + "="*50)
    print("📊 Demo Data Summary")
    print("="*50)
    print(f"Total Parking Spots: {len(data['parking_spots'])}")
    print(f"Occupied: {sum(1 for s in data['parking_spots'] if s['status'] == 'occupied')}")
    print(f"Reserved: {sum(1 for s in data['parking_spots'] if s['status'] == 'reserved')}")
    print(f"Available: {sum(1 for s in data['parking_spots'] if s['status'] == 'available')}")
    print(f"Active Vehicles: {len([v for v in data['vehicles'] if v['status'] == 'parked'])}")
    print(f"Active Bookings: {len(data['bookings'])}")
    print(f"Completed Transactions: {len(data['transactions'])}")
    
    total_revenue = sum(t['total_amount'] for t in data['transactions'])
    print(f"Total Revenue: ${total_revenue:.2f}")
    print("="*50)
    print("✅ Demo data generated successfully!")
    print(f"📁 Database location: {DB_PATH}")
    
    return True

if __name__ == "__main__":
    try:
        generate_demo_data()
    except Exception as e:
        print(f"❌ Error generating demo data: {e}")
        sys.exit(1)
