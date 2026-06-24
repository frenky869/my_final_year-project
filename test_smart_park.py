#!/usr/bin/env python3
"""
Test script for Smart Park System
Verifies core functionality
"""

import sys
from pathlib import Path
import datetime

# Add the project directory to path (use relative path)
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def test_database_initialization():
    """Test database initialization"""
    print("🧪 Testing database initialization...")
    
    # Import the functions
    from smart_park import init_database, load_database, save_database, DB_PATH
    
    # Remove existing database if any
    if DB_PATH.exists():
        DB_PATH.unlink()
    
    # Initialize
    init_database()
    
    # Check if file was created
    assert DB_PATH.exists(), "Database file not created"
    print("  ✅ Database file created")
    
    # Load and verify structure
    data = load_database()
    assert "parking_spots" in data, "Missing parking_spots"
    assert "vehicles" in data, "Missing vehicles"
    assert "bookings" in data, "Missing bookings"
    assert "transactions" in data, "Missing transactions"
    print("  ✅ Database structure valid")
    
    # Check parking spots
    spots = data["parking_spots"]
    assert len(spots) == 60, f"Expected 60 spots, got {len(spots)}"
    print("  ✅ 60 parking spots created")
    
    # Verify spot structure
    spot = spots[0]
    assert "id" in spot, "Spot missing id"
    assert "floor" in spot, "Spot missing floor"
    assert "status" in spot, "Spot missing status"
    assert "rate_per_hour" in spot, "Spot missing rate"
    print("  ✅ Spot structure valid")
    
    print("✅ Database initialization test PASSED\n")
    return True

def test_parking_statistics():
    """Test statistics calculation"""
    print("🧪 Testing parking statistics...")
    
    from smart_park import get_parking_statistics, load_database
    
    stats = get_parking_statistics()
    
    assert "total" in stats, "Missing total"
    assert "available" in stats, "Missing available"
    assert "occupied" in stats, "Missing occupied"
    assert "reserved" in stats, "Missing reserved"
    assert "occupancy_rate" in stats, "Missing occupancy_rate"
    print("  ✅ Statistics structure valid")
    
    assert stats["total"] == 60, f"Expected 60 total spots, got {stats['total']}"
    assert stats["available"] == 60, f"Expected 60 available spots, got {stats['available']}"
    assert stats["occupied"] == 0, f"Expected 0 occupied spots, got {stats['occupied']}"
    assert stats["occupancy_rate"] == 0, f"Expected 0% occupancy, got {stats['occupancy_rate']}"
    print("  ✅ Initial statistics correct")
    
    print("✅ Statistics test PASSED\n")
    return True

def test_vehicle_entry():
    """Test vehicle entry simulation"""
    print("🧪 Testing vehicle entry...")
    
    from smart_park import load_database, save_database
    
    data = load_database()
    
    # Simulate vehicle entry
    vehicle_entry = {
        "id": 1,
        "vehicle_number": "TEST-123",
        "vehicle_type": "car",
        "driver_name": "Test Driver",
        "driver_phone": "+1234567890",
        "spot_id": "A01",
        "entry_time": str(datetime.datetime.now()),
        "exit_time": None,
        "status": "parked"
    }
    
    data["vehicles"].append(vehicle_entry)
    
    # Update spot status
    for spot in data["parking_spots"]:
        if spot["id"] == "A01":
            spot["status"] = "occupied"
            break
    
    save_database(data)
    print("  ✅ Vehicle entry saved")
    
    # Verify
    data = load_database()
    assert len(data["vehicles"]) == 1, "Vehicle not saved"
    assert data["vehicles"][0]["vehicle_number"] == "TEST-123", "Wrong vehicle number"
    
    # Check spot status
    spot_a01 = next(s for s in data["parking_spots"] if s["id"] == "A01")
    assert spot_a01["status"] == "occupied", "Spot status not updated"
    print("  ✅ Spot status updated correctly")
    
    print("✅ Vehicle entry test PASSED\n")
    return True

def test_transaction():
    """Test transaction creation"""
    print("🧪 Testing transaction creation...")
    
    from smart_park import load_database, save_database
    
    data = load_database()
    
    transaction = {
        "id": 1,
        "vehicle_id": 1,
        "vehicle_number": "TEST-123",
        "spot_id": "A01",
        "entry_time": str(datetime.datetime.now() - datetime.timedelta(hours=2)),
        "exit_time": str(datetime.datetime.now()),
        "duration_hours": 2.0,
        "rate_per_hour": 5.0,
        "total_amount": 10.0,
        "payment_method": "Cash",
        "timestamp": str(datetime.datetime.now())
    }
    
    data["transactions"].append(transaction)
    save_database(data)
    print("  ✅ Transaction saved")
    
    # Verify
    data = load_database()
    assert len(data["transactions"]) == 1, "Transaction not saved"
    assert data["transactions"][0]["total_amount"] == 10.0, "Wrong amount"
    print("  ✅ Transaction details correct")
    
    print("✅ Transaction test PASSED\n")
    return True

def test_booking():
    """Test reservation/booking"""
    print("🧪 Testing booking system...")
    
    from smart_park import load_database, save_database
    
    data = load_database()
    
    booking = {
        "id": 1,
        "vehicle_number": "BOOK-456",
        "customer_name": "Test Customer",
        "customer_phone": "+9876543210",
        "customer_email": "test@example.com",
        "spot_id": "B05",
        "booking_date": str(datetime.date.today()),
        "booking_time": "14:00:00",
        "duration_hours": 3,
        "total_cost": 12.0,
        "status": "confirmed",
        "created_at": str(datetime.datetime.now())
    }
    
    data["bookings"].append(booking)
    
    # Update spot to reserved
    for spot in data["parking_spots"]:
        if spot["id"] == "B05":
            spot["status"] = "reserved"
            break
    
    save_database(data)
    print("  ✅ Booking saved")
    
    # Verify
    data = load_database()
    assert len(data["bookings"]) == 1, "Booking not saved"
    spot_b05 = next(s for s in data["parking_spots"] if s["id"] == "B05")
    assert spot_b05["status"] == "reserved", "Spot not reserved"
    print("  ✅ Spot marked as reserved")
    
    print("✅ Booking test PASSED\n")
    return True

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("🧪 Smart Park System - Test Suite")
    print("=" * 50)
    print()
    
    tests = [
        test_database_initialization,
        test_parking_statistics,
        test_vehicle_entry,
        test_transaction,
        test_booking
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test FAILED: {e}\n")
            failed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("✅ All tests PASSED!")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
