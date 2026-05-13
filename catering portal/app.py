import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. INITIAL SYSTEM CONFIGURATION ---
# Setting up page layout and identifying global constants
st.set_page_config(page_title="ET. Catering Portal", page_icon="🇪🇹", layout="wide")

# Database definitions for persistent storage
USER_DB = "users_db.csv"
HISTORY_DB = "catering_history.csv"
INVENTORY_DB = "master_inventory.csv"
FLIGHT_LIST_FILE = "saved_flights.csv"
SERVICE_TEMPLATES_FILE = "service_templates.csv"
MEAL_TEMPLATES_FILE = "meal_templates.csv"

# Comprehensive list of catering items for system tracking
EQUIPMENT_ITEMS = ["Trays", "Bowls", "Plates", "Spoons", "Forks"]
FOOD_ITEMS = ["Oranges", "Apples", "Kiwis", "Grapes"]
ALL_ITEMS = EQUIPMENT_ITEMS + FOOD_ITEMS

# --- 2. ADVANCED DATA UTILITIES & REPAIR ---

def load_users():
    """Retrieves user credentials and handles database initialization."""
    if os.path.exists(USER_DB):
        return pd.read_csv(USER_DB, dtype={'password': str})
    # Default Admin account for first-time setup
    return pd.DataFrame([{"username": "user32020", "password": "12345", "role": "admin"}])

def save_users(df):
    """Commits user data changes to the local storage."""
    df.to_csv(USER_DB, index=False)

def load_data(file, default_cols):
    """Loads CSV data with specific error handling for column mismatch issues."""
    if os.path.exists(file) and os.path.getsize(file) > 0:
        try:
            # We use on_bad_lines to skip corrupted rows seen in your screenshot
            return pd.read_csv(file, on_bad_lines='skip')
        except Exception:
            return pd.DataFrame(columns=default_cols)
    return pd.DataFrame(columns=default_cols)

def load_inventory():
    """Synchronizes the current stock balance on hand (BoH)."""
    if os.path.exists(INVENTORY_DB):
        return pd.read_csv(INVENTORY_DB).set_index("Item")
    # Initialize with large stock if file is missing
    return pd.DataFrame({"Stock_Qty": [1100000] * len(ALL_ITEMS)}, index=ALL_ITEMS)

def save_inventory(df):
    """Writes updated stock levels back to the inventory database."""
    df.reset_index().rename(columns={'index': 'Item'}).to_csv(INVENTORY_DB, index=False)

# --- 3. AUTHENTICATION & WELCOME HEADER ---

if "auth_status" not in st.session_state:
    st.session_state.update({"auth_status": False, "role": None, "user": None})

if not st.session_state["auth_status"]:
    # AMENDMENT: Welcome Header with a dedicated Ethiopian Flag Image for visibility
    st.markdown("""
        <div style='text-align: center;'>
            <h1>
                <img src='https://upload.wikimedia.org/wikipedia/commons/7/71/Flag_of_Ethiopia.svg' width='50'> 
                Welcome
            </h1>
            <h3 style='color: #2E7D32;'>ET. Catering Portal</h3>
        </div>
    """, unsafe_allow_html=True)
    
    col_l, col_m, col_r = st.columns([1,1,1])
    with col_m:
        with st.form("portal_access"):
            u_name = st.text_input("Username")
            u_pass = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In", use_container_width=True):
                u_db = load_users()
                valid = u_db[(u_db['username'] == u_name) & (u_db['password'] == str(u_pass))]
                if not valid.empty:
                    st.session_state.update({
                        "auth_status": True, 
                        "role": valid.iloc[0]['role'], 
                        "user": u_name
                    })
                    st.rerun()
                else:
                    st.error("Invalid Username or Password. Please try again.")
else:
    # --- 4. NAVIGATION INTERFACE ---
    st.sidebar.markdown(f"## 👤 {st.session_state['user']}")
    st.sidebar.markdown(f"**Current Role:** {st.session_state['role'].capitalize()}")
    
    # Core system pages
    nav_options = ["Home / Calculator", "Inventory & Variance", "History Log"]
    
    # Privileged administrator pages
    if st.session_state["role"] == "admin":
        nav_options += ["Flight & Service Manager", "Meal Service Editor", "Admin Control"]
    
    current_page = st.sidebar.radio("Navigation Menu Selection", nav_options)
    
    if st.sidebar.button("Logout System Account"):
        st.session_state.update({"auth_status": False, "user": None, "role": None})
        st.rerun()

    # --- 5. PAGE: HOME / CALCULATOR ---
    if current_page == "Home / Calculator":
        st.markdown("<h2 style='text-align: center;'>ET. Catering Portal</h2>", unsafe_allow_html=True)
        
        # Ethiopian Plane Image Implementation - Ensures visual asset is loaded
        st.image("https://www.ethiopianairlines.com/images/default-source/fleet/b787-9.png", 
                 use_container_width=True, caption="Ethiopian Airlines Catering Division")
        
        f_data = load_data(FLIGHT_LIST_FILE, ["Flight_No"])
        s_data = load_data(SERVICE_TEMPLATES_FILE, ["Service_Name", "Trays", "Bowls", "Plates"])
        m_data = load_data(MEAL_TEMPLATES_FILE, ["Meal_Name", "Oranges", "Apples", "Kiwis"])

        if f_data.empty or s_data.empty or m_data.empty:
            st.error("⚠️ System database is empty. Please configure Flights, Services, and Meals in Manager tabs.")
        else:
            c1, c2, c3 = st.columns(3)
            sel_f = c1.selectbox("Flight Number", f_data['Flight_No'])
            sel_move = c2.selectbox("Movement", ["Outgoing (Departure)", "Incoming (Arrival)"])
            pax_val = c3.number_input("Pax Count", min_value=1, value=100)

            c4, c5 = st.columns(2)
            sel_serv = c4.selectbox("Equipment Service", s_data['Service_Name'])
            sel_meal = c5.selectbox("Meal Service", m_data['Meal_Name'])

            if st.button("Confirm and Update Stock", use_container_width=True):
                # Fetching template values for calculation
                s_ref = s_data[s_data['Service_Name'] == sel_serv].iloc[0]
                m_ref = m_data[m_data['Meal_Name'] == sel_meal].iloc[0]
                
                # Math Logic for Inventory Changes
                calc_eq = {"Trays": pax_val*s_ref['Trays'], "Bowls": pax_val*s_ref['Bowls'], 
                           "Plates": pax_val*s_ref['Plates'], "Spoons": 0, "Forks": 0}
                calc_fd = {"Oranges": pax_val*m_ref['Oranges'], "Apples": pax_val*m_ref['Apples'], 
                           "Kiwis": pax_val*m_ref['Kiwis'], "Grapes": 0}
                
                inv_state = load_inventory()
                
                # Processing stock subtraction/addition based on movement type
                if sel_move == "Outgoing (Departure)":
                    for item, qty in {**calc_eq, **calc_fd}.items():
                        if item in inv_state.index: inv_state.at[item, "Stock_Qty"] -= qty
                else:
                    for item, qty in calc_eq.items():
                        if item in inv_state.index: inv_state.at[item, "Stock_Qty"] += qty

                # Writing Transaction to History with Timestamp
                history_entry = {"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                                "Flight": sel_f, "Type": sel_move, "Pax": pax_val}
                history_entry.update(calc_eq)
                history_entry.update(calc_fd)
                
                pd.DataFrame([history_entry]).to_csv(HISTORY_DB, mode='a', 
                                                  header=not os.path.exists(HISTORY_DB), index=False)
                
                save_inventory(inv_state)
                st.success(f"Successfully processed flight {sel_f}. Stock balance adjusted.")

    # --- 6. PAGE: INVENTORY & VARIANCE ---
    elif current_page == "Inventory & Variance":
        st.header("📦 Inventory Stock & Movement Analysis")
        
        main_inv = load_inventory()
        # Loading history while strictly enforcing columns to avoid KeyError
        hist_df = load_data(HISTORY_DB, ["Type"] + ALL_ITEMS)
        
        # Building the report dataframe structure
        report_table = pd.DataFrame(index=ALL_ITEMS)
        
        # Fixing the data recording error to ensure non-zero values appear
        if not hist_df.empty and 'Type' in hist_df.columns:
            out_subset = hist_df[hist_df['Type'] == "Outgoing (Departure)"]
            in_subset = hist_df[hist_df['Type'] == "Incoming (Arrival)"]
            
            for item in ALL_ITEMS:
                # Summing quantities from history if the column exists in the dataset
                report_table.loc[item, "Total Outgoing Qty"] = out_subset[item].sum() if item in out_subset.columns else 0
                report_table.loc[item, "Total Incoming Qty"] = in_subset[item].sum() if item in in_subset.columns else 0
        else:
            report_table["Total Outgoing Qty"] = 0
            report_table["Total Incoming Qty"] = 0

        report_table["Balance On Hand"] = main_inv["Stock_Qty"]
        
        st.subheader("Current Inventory Status Overview")
        # Ordering columns to match your requested layout: BoH, Outgoing, Incoming
        st.dataframe(report_table[["Balance On Hand", "Total Outgoing Qty", "Total Incoming Qty"]], 
                     use_container_width=True)

        st.markdown("---")
        st.subheader("📊 Net Variance & System Status")
        var_calc = pd.DataFrame(index=ALL_ITEMS)
        var_calc["Net Performance"] = report_table["Total Incoming Qty"] - report_table["Total Outgoing Qty"]
        var_calc["Stock Status"] = var_calc["Net Performance"].apply(lambda x: "🔻 Loss Reported" if x < 0 else "✅ Stable")
        st.dataframe(var_calc, use_container_width=True)

    # --- 7. PAGE: FLIGHT & SERVICE MANAGER ---
    elif current_page == "Flight & Service Manager":
        st.header("✈️ Flight & Equipment Setup")
        fl_c1, srv_c1 = st.columns(2)
        
        with fl_c1:
            st.subheader("Flight Registry")
            curr_fl = load_data(FLIGHT_LIST_FILE, ["Flight_No"])
            new_fl_no = st.text_input("New Flight No (e.g. 500)")
            if st.button("Register New Flight"):
                if new_fl_no:
                    new_f_df = pd.DataFrame([{"Flight_No": new_fl_no}])
                    curr_fl = pd.concat([curr_fl, new_f_df], ignore_index=True)
                    curr_fl.to_csv(FLIGHT_LIST_FILE, index=False)
                    st.rerun()
            
            st.write("Manage List:")
            st.dataframe(curr_fl, use_container_width=True)
            
            if not curr_fl.empty:
                f_idx = st.selectbox("Select Flight Entry to Delete", curr_fl.index, 
                                     format_func=lambda x: f"Row {x}: {curr_fl.loc[x, 'Flight_No']}")
                if st.button("Confirm Delete Flight"):
                    curr_fl = curr_fl.drop(f_idx)
                    curr_fl.to_csv(FLIGHT_LIST_FILE, index=False)
                    st.rerun()

        with srv_c1:
            st.subheader("Equipment Service Templates")
            curr_srv = load_data(SERVICE_TEMPLATES_FILE, ["Service_Name", "Trays", "Bowls", "Plates"])
            with st.form("add_srv_form"):
                n_srv = st.text_input("Service Template Name")
                q_tr = st.number_input("Trays per Passenger", 0.0)
                q_bw = st.number_input("Bowls per Passenger", 0.0)
                q_pl = st.number_input("Plates per Passenger", 0.0)
                if st.form_submit_button("Save Service Template"):
                    new_s = pd.DataFrame([{"Service_Name": n_srv, "Trays": q_tr, "Bowls": q_bw, "Plates": q_pl}])
                    pd.concat([curr_srv, new_s], ignore_index=True).to_csv(SERVICE_TEMPLATES_FILE, index=False)
                    st.rerun()
            
            st.write("Manage Equipment Services:")
            st.dataframe(curr_srv, use_container_width=True)
            if not curr_srv.empty:
                s_idx = st.selectbox("Select Service to Manage", curr_srv.index, 
                                     format_func=lambda x: f"Row {x}: {curr_srv.loc[x, 'Service_Name']}")
                if st.button("Remove Selected Service"):
                    curr_srv = curr_srv.drop(s_idx)
                    curr_srv.to_csv(SERVICE_TEMPLATES_FILE, index=False)
                    st.rerun()

    # --- 8. PAGE: MEAL SERVICE EDITOR ---
    elif current_page == "Meal Service Editor":
        st.header("🍎 Meal Configuration Manager")
        curr_ml = load_data(MEAL_TEMPLATES_FILE, ["Meal_Name", "Oranges", "Apples", "Kiwis"])
        
        with st.form("add_meal_form"):
            n_ml = st.text_input("Meal Plan Designation")
            o_ml = st.number_input("Oranges Per Pax", 0.0)
            a_ml = st.number_input("Apples Per Pax", 0.0)
            k_ml = st.number_input("Kiwis Per Pax", 0.0)
            if st.form_submit_button("Confirm Meal Definition"):
                new_m = pd.DataFrame([{"Meal_Name": n_ml, "Oranges": o_ml, "Apples": a_ml, "Kiwis": k_ml}])
                pd.concat([curr_ml, new_m], ignore_index=True).to_csv(MEAL_TEMPLATES_FILE, index=False)
                st.rerun()
        
        st.write("Current Global Meal Menu:")
        st.dataframe(curr_ml, use_container_width=True)
        
        if not curr_ml.empty:
            m_idx = st.selectbox("Select Meal Row to Delete", curr_ml.index, 
                                 format_func=lambda x: f"Row {x}: {curr_ml.loc[x, 'Meal_Name']}")
            if st.button("Delete Selected Meal Plan"):
                curr_ml = curr_ml.drop(m_idx)
                curr_ml.to_csv(MEAL_TEMPLATES_FILE, index=False)
                st.rerun()

    # --- 9. PAGE: HISTORY LOG ---
    elif current_page == "History Log":
        st.header("📑 Transaction History Logs")
        # Comprehensive historical data loading to track all past user actions
        full_hist = load_data(HISTORY_DB, [])
        if not full_hist.empty:
            st.dataframe(full_hist, use_container_width=True)
            if st.button("Purge History Records (Admin Only)"):
                if st.session_state["role"] == "admin":
                    pd.DataFrame(columns=["Date", "Flight", "Type", "Pax"] + ALL_ITEMS).to_csv(HISTORY_DB, index=False)
                    st.rerun()
        else:
            st.info("No transaction records currently available in the database.")

    # --- 10. PAGE: ADMIN CONTROL ---
    elif current_page == "Admin Control":
        st.header("⚙️ System Administration")
        users = load_users()
        
        t1, t2 = st.tabs(["Create Staff User", "Security Credentials Reset"])
        
        with t1:
            with st.form("create_staff_user"):
                un_in = st.text_input("Assign New Username")
                pw_in = st.text_input("Assign New Password")
                rl_in = st.selectbox("Assign System Access Role", ["user", "admin"])
                if st.form_submit_button("Finalize User Registration"):
                    if un_in and pw_in:
                        new_u_df = pd.DataFrame([{"username": un_in, "password": pw_in, "role": rl_in}])
                        save_users(pd.concat([users, new_u_df], ignore_index=True))
                        st.success(f"Access granted successfully to {un_in}")
                        st.rerun()
        
        with t2:
            target_staff = st.selectbox("Select Staff Account", users['username'])
            reset_key = st.text_input("Enter New Secure Password", type="password")
            if st.button("Execute Security Key Update"):
                users.loc[users['username'] == target_staff, 'password'] = reset_key
                save_users(users)
                st.success(f"User security credentials for {target_staff} updated.")
        
        st.divider()
        st.subheader("Authorized Personnel Directory")
        st.dataframe(users[['username', 'role']], use_container_width=True)
