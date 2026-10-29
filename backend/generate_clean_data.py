import pandas as pd
import random

df = pd.read_csv("data/inventory_updated.csv")

# INVENTORY STRUCTURE
inventory_map = {
    "INV001": ("Electronics", ["Samsung TV", "Dell Laptop", "iPhone", "LG Monitor"]),
    "INV002": ("Toys", ["Lego Set", "Barbie Doll", "Teddy Bear", "Hot Wheels"]),
    "INV003": ("Stationery", ["Pen", "Pencil", "Eraser", "Scale"]),
    "INV004": ("Gadgets", ["Smart Watch", "Headphones", "Power Bank", "Pendrive"]),
    "INV005": ("Clothing", ["T-Shirt", "Jeans", "Jacket", "Hoodie"]),
    "INV006": ("Furniture", ["Sofa", "Chair", "Table", "Bed"]),
    "INV007": ("Sports", ["Football", "Cricket Bat", "Dumbbell", "Tennis Racket"]),
    "INV008": ("Accessories", ["Watch", "Ring", "Handbag", "Chain"])
}

inventory_ids = list(inventory_map.keys())
products = sorted(df["Product ID"].unique())

# FIXED mapping
product_to_inventory = {
    product: inventory_ids[i % len(inventory_ids)]
    for i, product in enumerate(products)
}

# APPLY
df["inventory_id"] = df["Product ID"].map(product_to_inventory)

# ASSIGN CATEGORY + NAME
product_name_map = {}
category_map = {}

for product, inv in product_to_inventory.items():
    category, names = inventory_map[inv]
    product_name_map[product] = random.choice(names)
    category_map[product] = category

df["Product Name"] = df["Product ID"].map(product_name_map)
df["Category"] = df["Product ID"].map(category_map)

# SAVE NEW DATASET
df.to_csv("data/inventory_final.csv", index=False)

print("✅ Clean dataset created: inventory_final.csv")