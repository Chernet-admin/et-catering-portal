import csv
from datetime import datetime

# 1. Setup Data
unit_price = 12.75
log_file = "catering_portal_history.csv"

print("--- Welcome to the Catering Portal ---")

# 2. Collect Inputs
flight_no = input("Enter Flight Number: ")
passengers = int(input("Enter Passenger Count: "))

# 3. Calculations
total_meals = passengers * 1.05
total_cost = total_meals * unit_price

# 4. Show results on screen
print(f"\n--- Order Summary for {flight_no} ---")
print(f"Meals needed: {total_meals}")
print(f"Total Cost: ${total_cost:.2f}")

# 5. Save to the "Portal Database" (CSV)
file_exists = False
try:
    with open(log_file, 'r') as f:
        file_exists = True
except FileNotFoundError:
    file_exists = False

with open(log_file, 'a', newline='') as f:
    writer = csv.writer(f)
    # If the file is new, add the headers (the top row)
    if not file_exists:
        writer.writerow(["Date", "Flight Number", "Passengers", "Total Meals", "Total Cost"])
    
    # Save the current order
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    writer.writerow([current_date, flight_no, passengers, total_meals, total_cost])

print(f"\n[Success] Data saved to {log_file}")