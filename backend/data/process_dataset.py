import pandas as pd
import random

# Load dataset
df = pd.read_csv("inventory.csv")

# 🔥 Inventory mapping (based on Category column)
inventory_map = {
    "Electronics": "INV001",
    "Toys": "INV002",
    "Stationery": "INV003",
    "Gadgets": "INV004",
    "Clothing": "INV005",
    "Furniture": "INV006",
    "Sports": "INV007",
    "Accessories": "INV008"
}

# If dataset category names differ → adjust here
def map_inventory(category):
    category = str(category).lower()

    if "electronic" in category:
        return "INV001"
    elif "toy" in category:
        return "INV002"
    elif "station" in category:
        return "INV003"
    elif "gadget" in category:
        return "INV004"
    else:
        return "INV008"

df["inventory_id"] = df["Category"].apply(map_inventory)

# 🔥 Generate product names
electronics_names = ["Samsung TV", "Sony Headphones", "LG Monitor"]
toy_names = ["Lego Set", "Toy Car", "Doll"]
stationery_names = ["Notebook", "Pen", "Marker"]
gadgets_names = ["Power Bank", "Smart Watch", "Bluetooth Speaker"]

def generate_name(inv):
    if inv == "INV001":
        return random.choice(electronics_names)
    elif inv == "INV002":
        return random.choice(toy_names)
    elif inv == "INV003":
        return random.choice(stationery_names)
    elif inv == "INV004":
        return random.choice(gadgets_names)
    else:
        return "Generic Product"

df["product_name"] = df["inventory_id"].apply(generate_name)

# Save new dataset
df.to_csv("inventory_updated.csv", index=False)

print("✅ Dataset updated successfully")