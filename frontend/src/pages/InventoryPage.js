import InventoryCard from "../components/InventoryCard";

const inventories = [
  { id: "INV001", name: "Electronics", image: "/images/electronics.png" },
  { id: "INV002", name: "Toys", image: "/images/toys.png" },
  { id: "INV003", name: "Stationary", image: "/images/stationary.png" },
  { id: "INV004", name: "Gadgets", image: "/images/gadgets.png" },
  { id: "INV005", name: "Appliances", image: "/images/appliances.png" },
  { id: "INV006", name: "Accessories", image: "/images/accessories.png" },
  { id: "INV007", name: "Tools", image: "/images/tools.png" },
  { id: "INV008", name: "Office Supplies", image: "/images/office.png" }
];

function InventoryPage() {
  return (
    <div style={{ padding: "30px" }}>
      
      {/* HEADER */}
      <h1 style={{
        textAlign: "center",
        color: "#38bdf8",
        letterSpacing: "2px",
        marginBottom: "30px",
        textShadow: "0 0 10px #38bdf8"
      }}>
        Inventory Categories
      </h1>

      <div style={{
  display: "grid",
  gridTemplateColumns: "repeat(4, 1fr)",   // ✅ FIX: 4 per row
  gap: "40px",
  justifyItems: "center",
  marginTop: "40px"
}}>
        {inventories.map((inv, i) => (
          <InventoryCard key={i} {...inv} />
        ))}
      </div>
    </div>
  );
}

export default InventoryPage;