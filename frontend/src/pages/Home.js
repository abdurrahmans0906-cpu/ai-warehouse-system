import { useEffect, useState } from "react";
import "../styles/home.css";
import { useNavigate } from "react-router-dom";
import { FaBrain, FaRedo } from "react-icons/fa";
import { API_BASE } from "../api";

function Home() {
  const [data, setData] = useState({
    low_stock: [],
    high_demand: []
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const loadData = () => {
    setLoading(true);
    setError(null);
    fetch(`${API_BASE}/home`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        return res.json();
      })
      .then(data => {
        if (data.error) {
          setError(data.error);
        } else {
          setData(data);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load /home data:", err);
        setError(err.message || "Connection failed");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <h3 style={{ padding: "30px", color: "#38bdf8" }}>Loading Warehouse Command Center...</h3>;

  return (
    <div style={{ padding: "30px", maxWidth: "1300px", margin: "0 auto" }}>
      
      {/* 🔥 TITLE & BENCHMARK BANNER */}
      <div style={{ textAlign: "center", marginBottom: "30px" }}>
        <h1 style={{
          fontSize: "32px",
          color: "#38bdf8",
          letterSpacing: "2px",
          marginBottom: "10px",
          textShadow: "0 0 10px #38bdf8"
        }}>
          AI Warehouse Command Center
        </h1>
        <p style={{ color: "#94a3b8", fontSize: "14px", margin: 0 }}>
          Real-time Inventory Monitoring Powered by 6 Machine Learning & Time-Series Forecasting Models
        </p>

        {/* Quick link button to 6-model benchmark */}
        <div style={{ marginTop: "15px", display: "flex", justifyContent: "center", gap: "10px", flexWrap: "wrap" }}>
          <button
            onClick={() => navigate("/models")}
            style={{
              background: "rgba(56, 189, 248, 0.12)",
              border: "1px solid #38bdf8",
              color: "#38bdf8",
              padding: "10px 22px",
              borderRadius: "10px",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "600",
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              transition: "0.2s"
            }}
          >
            <FaBrain /> Open 6-Model AI Accuracy Benchmark
          </button>

          {error && (
            <button
              onClick={() => loadData()}
              style={{
                background: "rgba(239, 68, 68, 0.12)",
                border: "1px solid #ef4444",
                color: "#ef4444",
                padding: "10px 20px",
                borderRadius: "10px",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: "600",
                display: "inline-flex",
                alignItems: "center",
                gap: "8px"
              }}
            >
              <FaRedo /> Retry Connection
            </button>
          )}
        </div>

        {error && (
          <div style={{
            marginTop: "15px",
            padding: "12px",
            background: "rgba(239, 68, 68, 0.1)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            borderRadius: "10px",
            color: "#f87171",
            fontSize: "14px"
          }}>
            Failed to connect to backend at <code>{API_BASE}</code>: {error}. Ensure FastAPI is running.
          </div>
        )}
      </div>

      {/* 🔴 LOW STOCK TABLE */}
      <div className="table-box">
        <h2 className="red">Critical Low Stock (ROP Breach)</h2>

        <table className="table">
          <thead>
            <tr>
              <th>Product ID</th>
              <th>Product Name</th>
              <th>Stock</th>
              <th>ROP</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            {data.low_stock.length > 0 ? (
              data.low_stock.map((p, i) => (
                <tr key={i}>
                  <td className="blue">{p["Product ID"]}</td>
                  <td>{p["Product Name"]}</td>
                  <td style={{ color: "#ef4444", fontWeight: "bold" }}>
                    {Math.round(p["Inventory Level"])}
                  </td>
                  <td style={{ color: "#38bdf8" }}>
                    {Math.round(p["rop"])}
                  </td>
                  <td>
                    <button
                      className="btn"
                      onClick={() => navigate(`/product/${p["Product ID"]}`)}
                    >
                      Forecast & Accuracy
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5">No low stock products</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* 📈 HIGH DEMAND TABLE */}
      <div className="table-box">
        <h2 className="green">High Demand Products</h2>

        <table className="table">
          <thead>
            <tr>
              <th>Product ID</th>
              <th>Product Name</th>
              <th>Units Sold</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            {data.high_demand.length > 0 ? (
              data.high_demand.map((p, i) => (
                <tr key={i}>
                  <td className="blue">{p["Product ID"]}</td>
                  <td>{p["Product Name"]}</td>
                  <td>{Math.round(p["Units Sold"])}</td>
                  <td>
                    <button
                      className="btn"
                      onClick={() => navigate(`/product/${p["Product ID"]}`)}
                    >
                      Forecast & Accuracy
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="4">No high demand products</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
}

export default Home;
