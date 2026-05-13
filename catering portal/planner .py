unit_price = 12.75

print("--- Airline Catering Planner ---")

# 1. Ask user for count
passengers_input = input("Enter total passenger count: ")
passengers = int(passengers_input)

# 2. Calculation
total_meals = passengers * 1.05
total_cost = total_meals * unit_price

# 3. Output
print(f"Total meals needed (with 5% buffer): {total_meals}")
print(f"Total Purchase Order amount: ${total_cost:.2f}")