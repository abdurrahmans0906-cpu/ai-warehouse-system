import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { FaArrowLeft, FaBrain } from "react-icons/fa";
import { API_BASE } from "../api";

function InventoryDashboard() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState({
    top_products: [],
    products: []
  });

  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/inventory/${id}`)
      .then(res => res.json())
      .then(data => setData(data))
      .catch(err => console.error(err));
  }, [id]);

  if (!data) return <h2 style={{ padding: "20px", color: "#38bdf8" }}>Loading...</h2>;

  return (
    <div style={{
      padding: "30px",
      maxWidth: "1200px",
      margin: "0 auto",
      color: "#f8fafc"
    }}>

      {/* 🔙 HEADER */}
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "15px"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
          <button onClick={() => navigate(-1)} style={backBtn}>
            <FaArrowLeft />
          </button>

          <h1 style={titleStyle}>
            Category: {data.inventory_id || id}
          </h1>
        </div>

        <button
          onClick={() => navigate("/models")}
          style={{
            background: "rgba(56, 189, 248, 0.12)",
            border: "1px solid #38bdf8",
            color: "#38bdf8",
            padding: "8px 16px",
            borderRadius: "10px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            fontSize: "13px",
            fontWeight: "600"
          }}
        >
          <FaBrain /> AI Model Benchmark
        </button>
      </div>

      {/* 🔥 KPI BOXES */}
      <div style={{
        display: "flex",
        gap: "30px",
        marginTop: "30px"
      }}>
        <KPI title="Total Products" value={data.total_products} color="#38bdf8" />
        <KPI title="Sales % of Total" value={`${data.sales_percentage || 0}%`} color="#22c55e" />
      </div>

      {/* 🔍 SEARCH */}
      <div style={{
        display: "flex",
        justifyContent: "center",
        marginTop: "40px",
        gap: "10px"
      }}>
        <input
          placeholder="Search Product ID (e.g. P0001)..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={searchInput}
        />

        <button
          style={searchBtn}
          onClick={() => {
            if (search) navigate(`/product/${search.trim()}`);
          }}
        >
          Search & Forecast
        </button>
      </div>

      {/* 🔥 TABLE */}
      <div style={tableBox}>
        <h3 style={{ color: "#38bdf8", marginBottom: "15px" }}>Top Demand Products in Category</h3>

        <table style={table}>
          <thead>
            <tr>
              <th style={thStyle}>Product ID</th>
              <th style={thStyle}>Product Name</th>
              <th style={thStyle}>Units Sold</th>
              <th style={thStyle}>AI Forecasting Action</th>
            </tr>
          </thead>

          <tbody>
            {data.top_products && data.top_products.length > 0 ? (
              data.top_products.map((p, i) => (
                <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                  <td style={{ ...tdStyle, color: "#38bdf8", fontWeight: "600" }}>{p["Product ID"]}</td>
                  <td style={tdStyle}>{p["Product Name"] || `Product ${p["Product ID"]}`}</td>
                  <td style={{ ...tdStyle, color: "#22c55e", fontWeight: "bold" }}>
                    {p["Units Sold"]}
                  </td>
                  <td style={tdStyle}>
                    <button
                      onClick={() => navigate(`/product/${p["Product ID"]}`)}
                      style={{
                        background: "#020617",
                        border: "1px solid #38bdf8",
                        color: "#38bdf8",
                        padding: "6px 14px",
                        borderRadius: "8px",
                        cursor: "pointer",
                        fontSize: "12px",
                        fontWeight: "600"
                      }}
                    >
                      Forecast & Accuracy
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4" style={tdStyle}>No products found</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
}

/* 🔥 KPI COMPONENT */
function KPI({ title, value, color }) {
  return (
    <div style={{
      flex: 1,
      padding: "25px",
      borderRadius: "18px",
      background: "rgba(255,255,255,0.03)",
      border: `1px solid ${color}`,
      backdropFilter: "blur(10px)",
      textAlign: "center",
      transition: "0.3s"
    }}>
      <h3 style={{ color, margin: "0 0 10px 0", fontSize: "16px" }}>{title}</h3>
      <p style={{ fontSize: "28px", color, margin: 0, fontWeight: "700" }}>{value}</p>
    </div>
  );
}

/* STYLES */
const titleStyle = {
  color: "#38bdf8",
  letterSpacing: "1px",
  margin: 0,
  fontSize: "26px"
};

const backBtn = {
  background: "#020617",
  border: "1px solid #38bdf8",
  color: "#38bdf8",
  padding: "8px 14px",
  borderRadius: "10px",
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  justifyContent: "center"
};

const searchInput = {
  padding: "12px 16px",
  borderRadius: "12px",
  border: "1px solid #38bdf8",
  background: "#020617",
  color: "white",
  width: "300px",
  outline: "none",
  fontSize: "14px"
};

const searchBtn = {
  padding: "12px 20px",
  borderRadius: "12px",
  border: "none",
  background: "#38bdf8",
  color: "#020617",
  cursor: "pointer",
  fontWeight: "600",
  fontSize: "14px"
};

const tableBox = {
  marginTop: "40px",
  padding: "24px",
  borderRadius: "16px",
  background: "rgba(255,255,255,0.03)",
  border: "1px solid rgba(56,189,248,0.2)"
};

const table = {
  width: "100%",
  marginTop: "10px",
  borderCollapse: "collapse",
  color: "white"
};

const thStyle = {
  padding: "14px",
  textAlign: "left",
  color: "#64748b",
  fontWeight: "600",
  fontSize: "12px",
  textTransform: "uppercase",
  borderBottom: "1px solid #1e293b"
};

const tdStyle = {
  padding: "12px 14px",
  textAlign: "left",
  color: "#e2e8f0",
  fontSize: "14px"
};

export default InventoryDashboard;
