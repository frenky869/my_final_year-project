import streamlit as st
import pandas as pd
import datetime
import json
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Smart Park System",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Main background styling */
    .main {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }
    
    /* Header styling */
    .main-header {
        font-size: 4rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 800;
    }
    
    .sub-header {
        font-size: 1.8rem;
        color: #a8d8ea;
        margin-bottom: 2rem;
        text-align: center;
        font-weight: 600;
    }
    
    /* Card styling */
    .parking-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 15px 0;
        transition: transform 0.3s ease;
        color: #ffffff;
    }
    
    .parking-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.15);
    }
    
    .available-spot {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    
    .occupied-spot {
        background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    
    .reserved-spot {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        color: #ffffff;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Make text readable */
    h1, h2, h3, h4, h5, h6 {
        color: #a8d8ea !important;
    }
    
    p, div, span, label {
        color: #e6e6e6 !important;
    }
    
    .stTextInput input, .stNumberInput input, .stSelectbox div {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: #ffffff;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Database file path
DB_PATH = Path(__file__).parent / "parking_data.json"

# Initialize database structure
def init_database():
    """Initialize the parking database if it doesn't exist"""
    if not DB_PATH.exists():
        default_data = {
            "parking_spots": [],
            "vehicles": [],
            "bookings": [],
            "transactions": []
        }
        save_database(default_data)
        
        # Create default parking spots
        spots = []
        for floor in ['A', 'B', 'C']:
            for spot_num in range(1, 21):
                spots.append({
                    "id": f"{floor}{spot_num:02d}",
                    "floor": floor,
                    "status": "available",
                    "vehicle_type": "car",
                    "rate_per_hour": 5.0 if floor == 'A' else 4.0 if floor == 'B' else 3.0
                })
        
        data = load_database()
        data["parking_spots"] = spots
        save_database(data)

def load_database():
    """Load data from JSON database"""
    if DB_PATH.exists():
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    return {"parking_spots": [], "vehicles": [], "bookings": [], "transactions": []}

def save_database(data):
    """Save data to JSON database"""
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def get_parking_statistics():
    """Calculate parking statistics"""
    data = load_database()
    spots = data.get("parking_spots", [])
    
    total_spots = len(spots)
    available = sum(1 for s in spots if s["status"] == "available")
    occupied = sum(1 for s in spots if s["status"] == "occupied")
    reserved = sum(1 for s in spots if s["status"] == "reserved")
    
    return {
        "total": total_spots,
        "available": available,
        "occupied": occupied,
        "reserved": reserved,
        "occupancy_rate": (occupied / total_spots * 100) if total_spots > 0 else 0
    }

def display_dashboard():
    """Display the main dashboard"""
    st.markdown('<div class="main-header">🅿️ Smart Park System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Intelligent Parking Management Solution</div>', unsafe_allow_html=True)
    
    # Statistics
    stats = get_parking_statistics()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <h3>🅿️</h3>
            <h2 style="margin: 10px 0; color: #667eea !important;">{stats["total"]}</h2>
            <p>Total Spots</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <h3>✅</h3>
            <h2 style="margin: 10px 0; color: #38ef7d !important;">{stats["available"]}</h2>
            <p>Available</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <h3>🚗</h3>
            <h2 style="margin: 10px 0; color: #ff6a00 !important;">{stats["occupied"]}</h2>
            <p>Occupied</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="metric-card">
            <h3>📅</h3>
            <h2 style="margin: 10px 0; color: #f5576c !important;">{stats["reserved"]}</h2>
            <p>Reserved</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col5:
        st.markdown(f'''
        <div class="metric-card">
            <h3>📊</h3>
            <h2 style="margin: 10px 0; color: #a8d8ea !important;">{stats["occupancy_rate"]:.1f}%</h2>
            <p>Occupancy</p>
        </div>
        ''', unsafe_allow_html=True)

def display_parking_grid():
    """Display parking spots in a grid layout"""
    st.markdown("### 🅿️ Parking Spot Status")
    
    data = load_database()
    spots = data.get("parking_spots", [])
    
    # Group by floor
    floors = {}
    for spot in spots:
        floor = spot["floor"]
        if floor not in floors:
            floors[floor] = []
        floors[floor].append(spot)
    
    # Display each floor
    for floor_name in sorted(floors.keys()):
        st.markdown(f"#### Floor {floor_name}")
        floor_spots = floors[floor_name]
        
        # Display in rows of 5
        for i in range(0, len(floor_spots), 5):
            cols = st.columns(5)
            for j, col in enumerate(cols):
                if i + j < len(floor_spots):
                    spot = floor_spots[i + j]
                    with col:
                        status_class = f"{spot['status']}-spot"
                        emoji = "✅" if spot['status'] == 'available' else "🚗" if spot['status'] == 'occupied' else "📅"
                        st.markdown(f'''
                        <div class="{status_class}">
                            {emoji}<br>
                            <strong>{spot['id']}</strong><br>
                            ${spot['rate_per_hour']}/hr
                        </div>
                        ''', unsafe_allow_html=True)

def vehicle_entry():
    """Handle vehicle entry"""
    st.markdown("### 🚗 Vehicle Entry")
    
    data = load_database()
    available_spots = [s for s in data["parking_spots"] if s["status"] == "available"]
    
    if not available_spots:
        st.error("⚠️ No parking spots available!")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        vehicle_number = st.text_input("Vehicle Registration Number", placeholder="e.g., ABC-1234")
        vehicle_type = st.selectbox("Vehicle Type", ["car", "motorcycle", "truck", "van"])
        driver_name = st.text_input("Driver Name", placeholder="e.g., John Doe")
        driver_phone = st.text_input("Phone Number", placeholder="e.g., +1234567890")
    
    with col2:
        spot_options = [s["id"] for s in available_spots]
        selected_spot = st.selectbox("Select Parking Spot", spot_options)
        entry_time = st.time_input("Entry Time", datetime.datetime.now().time())
        
        spot_details = next(s for s in available_spots if s["id"] == selected_spot)
        st.info(f"Rate: ${spot_details['rate_per_hour']}/hour")
    
    if st.button("✅ Check In Vehicle"):
        if not vehicle_number or not driver_name:
            st.error("Please fill in all required fields!")
            return
        
        # Create vehicle entry
        vehicle_entry = {
            "id": len(data["vehicles"]) + 1,
            "vehicle_number": vehicle_number.upper(),
            "vehicle_type": vehicle_type,
            "driver_name": driver_name,
            "driver_phone": driver_phone,
            "spot_id": selected_spot,
            "entry_time": str(datetime.datetime.combine(datetime.date.today(), entry_time)),
            "exit_time": None,
            "status": "parked"
        }
        
        # Update spot status
        for spot in data["parking_spots"]:
            if spot["id"] == selected_spot:
                spot["status"] = "occupied"
                break
        
        # Save to database
        data["vehicles"].append(vehicle_entry)
        save_database(data)
        
        st.success(f"✅ Vehicle {vehicle_number} checked in to spot {selected_spot}!")
        st.rerun()

def vehicle_exit():
    """Handle vehicle exit"""
    st.markdown("### 🚗 Vehicle Exit")
    
    data = load_database()
    parked_vehicles = [v for v in data["vehicles"] if v["status"] == "parked"]
    
    if not parked_vehicles:
        st.info("No vehicles currently parked.")
        return
    
    # Create a searchable list
    vehicle_options = {f"{v['vehicle_number']} - Spot {v['spot_id']}": v for v in parked_vehicles}
    selected_vehicle_key = st.selectbox("Select Vehicle", list(vehicle_options.keys()))
    
    if selected_vehicle_key:
        vehicle = vehicle_options[selected_vehicle_key]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Vehicle Details:**")
            st.write(f"- Registration: {vehicle['vehicle_number']}")
            st.write(f"- Driver: {vehicle['driver_name']}")
            st.write(f"- Type: {vehicle['vehicle_type']}")
            st.write(f"- Spot: {vehicle['spot_id']}")
            st.write(f"- Entry Time: {vehicle['entry_time']}")
        
        with col2:
            exit_time = st.time_input("Exit Time", datetime.datetime.now().time())
            
            # Calculate parking duration and cost
            entry_dt = datetime.datetime.fromisoformat(vehicle['entry_time'])
            exit_dt = datetime.datetime.combine(datetime.date.today(), exit_time)
            
            if exit_dt < entry_dt:
                exit_dt += datetime.timedelta(days=1)
            
            duration = exit_dt - entry_dt
            hours = duration.total_seconds() / 3600
            
            # Get spot rate
            spot = next((s for s in data["parking_spots"] if s["id"] == vehicle['spot_id']), None)
            rate = spot['rate_per_hour'] if spot else 5.0
            
            total_cost = hours * rate
            
            st.write("**Parking Summary:**")
            st.write(f"- Duration: {hours:.2f} hours")
            st.write(f"- Rate: ${rate}/hour")
            st.write(f"- **Total Cost: ${total_cost:.2f}**")
        
        payment_method = st.selectbox("Payment Method", ["Cash", "Credit Card", "Debit Card", "Mobile Payment"])
        
        if st.button("💳 Process Exit & Payment"):
            # Update vehicle status
            for v in data["vehicles"]:
                if v["id"] == vehicle["id"]:
                    v["exit_time"] = str(exit_dt)
                    v["status"] = "completed"
                    break
            
            # Free up the spot
            for s in data["parking_spots"]:
                if s["id"] == vehicle['spot_id']:
                    s["status"] = "available"
                    break
            
            # Create transaction record
            transaction = {
                "id": len(data["transactions"]) + 1,
                "vehicle_id": vehicle["id"],
                "vehicle_number": vehicle["vehicle_number"],
                "spot_id": vehicle["spot_id"],
                "entry_time": vehicle["entry_time"],
                "exit_time": str(exit_dt),
                "duration_hours": round(hours, 2),
                "rate_per_hour": rate,
                "total_amount": round(total_cost, 2),
                "payment_method": payment_method,
                "timestamp": str(datetime.datetime.now())
            }
            
            data["transactions"].append(transaction)
            save_database(data)
            
            st.success(f"✅ Vehicle {vehicle['vehicle_number']} checked out! Total: ${total_cost:.2f}")
            st.rerun()

def booking_system():
    """Handle parking spot reservations"""
    st.markdown("### 📅 Reserve Parking Spot")
    
    data = load_database()
    available_spots = [s for s in data["parking_spots"] if s["status"] == "available"]
    
    if not available_spots:
        st.warning("⚠️ No spots available for reservation.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        vehicle_number = st.text_input("Vehicle Registration", placeholder="ABC-1234")
        customer_name = st.text_input("Customer Name", placeholder="John Doe")
        customer_phone = st.text_input("Phone Number", placeholder="+1234567890")
        customer_email = st.text_input("Email", placeholder="john@example.com")
    
    with col2:
        spot_options = [s["id"] for s in available_spots]
        selected_spot = st.selectbox("Select Spot", spot_options)
        
        booking_date = st.date_input("Reservation Date", datetime.date.today())
        booking_time = st.time_input("Reservation Time")
        duration_hours = st.number_input("Duration (hours)", min_value=1, max_value=24, value=2)
        
        spot_details = next(s for s in available_spots if s["id"] == selected_spot)
        total_cost = spot_details['rate_per_hour'] * duration_hours
        st.info(f"Total Cost: ${total_cost:.2f}")
    
    if st.button("📅 Confirm Reservation"):
        if not vehicle_number or not customer_name:
            st.error("Please fill in all required fields!")
            return
        
        booking = {
            "id": len(data["bookings"]) + 1,
            "vehicle_number": vehicle_number.upper(),
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "customer_email": customer_email,
            "spot_id": selected_spot,
            "booking_date": str(booking_date),
            "booking_time": str(booking_time),
            "duration_hours": duration_hours,
            "total_cost": round(total_cost, 2),
            "status": "confirmed",
            "created_at": str(datetime.datetime.now())
        }
        
        # Update spot status
        for spot in data["parking_spots"]:
            if spot["id"] == selected_spot:
                spot["status"] = "reserved"
                break
        
        data["bookings"].append(booking)
        save_database(data)
        
        st.success(f"✅ Reservation confirmed! Booking ID: {booking['id']}")
        st.info(f"Spot {selected_spot} reserved for {customer_name} on {booking_date} at {booking_time}")
        st.rerun()

def reports_analytics():
    """Display reports and analytics"""
    st.markdown("### 📊 Reports & Analytics")
    
    data = load_database()
    transactions = data.get("transactions", [])
    vehicles = data.get("vehicles", [])
    
    if not transactions:
        st.info("No transaction data available yet.")
        return
    
    # Convert to DataFrame
    df_transactions = pd.DataFrame(transactions)
    
    # Revenue metrics
    total_revenue = df_transactions['total_amount'].sum()
    avg_transaction = df_transactions['total_amount'].mean()
    total_transactions = len(transactions)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <h3>💰</h3>
            <h2 style="margin: 10px 0; color: #38ef7d !important;">${total_revenue:.2f}</h2>
            <p>Total Revenue</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card">
            <h3>💳</h3>
            <h2 style="margin: 10px 0; color: #667eea !important;">{total_transactions}</h2>
            <p>Transactions</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card">
            <h3>📊</h3>
            <h2 style="margin: 10px 0; color: #f5576c !important;">${avg_transaction:.2f}</h2>
            <p>Avg Transaction</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # Recent transactions
    st.markdown("#### 📋 Recent Transactions")
    display_df = df_transactions[['vehicle_number', 'spot_id', 'duration_hours', 'total_amount', 'payment_method', 'timestamp']].tail(10)
    st.dataframe(display_df, use_container_width=True)
    
    # Payment methods breakdown
    if 'payment_method' in df_transactions.columns:
        st.markdown("#### 💳 Payment Methods")
        payment_counts = df_transactions['payment_method'].value_counts()
        st.bar_chart(payment_counts)

def admin_panel():
    """Admin panel for managing the system"""
    st.markdown("### ⚙️ Admin Panel")
    
    tab1, tab2, tab3 = st.tabs(["Manage Spots", "View Bookings", "System Settings"])
    
    with tab1:
        st.markdown("#### Parking Spot Management")
        data = load_database()
        
        # Display all spots in a table
        df_spots = pd.DataFrame(data["parking_spots"])
        st.dataframe(df_spots, use_container_width=True)
        
        # Add new spot
        with st.expander("➕ Add New Parking Spot"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_spot_id = st.text_input("Spot ID", placeholder="A21")
            with col2:
                new_floor = st.selectbox("Floor", ["A", "B", "C", "D"])
            with col3:
                new_rate = st.number_input("Rate/Hour ($)", min_value=1.0, value=5.0)
            
            if st.button("Add Spot"):
                if new_spot_id:
                    new_spot = {
                        "id": new_spot_id,
                        "floor": new_floor,
                        "status": "available",
                        "vehicle_type": "car",
                        "rate_per_hour": new_rate
                    }
                    data["parking_spots"].append(new_spot)
                    save_database(data)
                    st.success(f"Spot {new_spot_id} added!")
                    st.rerun()
    
    with tab2:
        st.markdown("#### Active Bookings")
        data = load_database()
        bookings = data.get("bookings", [])
        
        if bookings:
            df_bookings = pd.DataFrame(bookings)
            st.dataframe(df_bookings, use_container_width=True)
        else:
            st.info("No active bookings.")
    
    with tab3:
        st.markdown("#### System Configuration")
        st.info("System settings and configuration options coming soon...")
        
        # Reset database option
        st.markdown("##### ⚠️ Danger Zone")
        if st.button("🗑️ Reset All Data", type="secondary"):
            if st.checkbox("I understand this will delete all data"):
                DB_PATH.unlink(missing_ok=True)
                init_database()
                st.success("Database reset successfully!")
                st.rerun()

def main():
    """Main application"""
    # Initialize database
    init_database()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🚀 Navigation")
        page = st.radio(
            "Select Page",
            ["🏠 Dashboard", "🚗 Vehicle Entry", "🚪 Vehicle Exit", "📅 Reservations", "📊 Reports", "⚙️ Admin Panel"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 📍 Quick Stats")
        stats = get_parking_statistics()
        st.metric("Available Spots", stats["available"])
        st.metric("Occupancy Rate", f"{stats['occupancy_rate']:.1f}%")
        
        st.markdown("---")
        st.markdown("### ℹ️ System Info")
        st.info("""
        **Smart Park System v1.0**
        
        Intelligent parking management 
        with real-time monitoring and 
        automated billing.
        """)
    
    # Main content based on selected page
    if page == "🏠 Dashboard":
        display_dashboard()
        display_parking_grid()
    
    elif page == "🚗 Vehicle Entry":
        display_dashboard()
        vehicle_entry()
    
    elif page == "🚪 Vehicle Exit":
        display_dashboard()
        vehicle_exit()
    
    elif page == "📅 Reservations":
        display_dashboard()
        booking_system()
    
    elif page == "📊 Reports":
        display_dashboard()
        reports_analytics()
    
    elif page == "⚙️ Admin Panel":
        admin_panel()

if __name__ == "__main__":
    main()
