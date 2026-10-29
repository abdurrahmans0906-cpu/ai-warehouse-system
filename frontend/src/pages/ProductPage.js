import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend, Cell
} from "recharts";
import { FaArrowLeft, FaBrain, FaTrophy, FaRedo, FaInfoCircle } from "react-icons/fa";
import { API_BASE } from "../api";

function ProductPage() {
  const { productId } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedModel, setSelectedModel] = useState("all"); // "all", "best", "prophet", "arima", "exponential_smoothing", "xgboost", "random_forest", "ridge"
  const [activeTab, setActiveTab] = useState("forecast"); // "forecast", "metrics", "insights"

  const fetchProductData = (refresh = false) => {
    setLoading(true);
    fetch(`${API_BASE}/product?product_id=${productId}&refresh=${refresh}`)
      .then(res => res.json())
      .then(result => {
        setData(result);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching product data:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchProductData();
  }, [productId]);

  if (loading) {
    return (
      <div style={{ padding: "40px", textAlign: "center", color: "#38bdf8" }}>
        <h2>Forecasting & Benchmarking 6 Models for Product {productId}...</h2>
        <p style={{ color: "#94a3b8" }}>Training Prophet, ARIMA, Exponential Smoothing, XGBoost, Random Forest, and Ridge on retail demand history.</p>
      </div>
    );
  }

  if (!data || data.error) {
    return (
      <div style={{ padding: "40px", textAlign: "center", color: "#ef4444" }}>
        <h2>Error Loading Product {productId}</h2>
        <p>{data?.error || "Unknown error"}</p>
        <button onClick={() => navigate(-1)} style={backBtn}>
          ← Go Back
        </button>
      </div>
    );
  }

  const {
    product_name,
    inventory_id,
    inventory,
    trend,
    best_model,
    models_accuracy,
    metrics_comparison_chart,
    graph
  } = data;

  const MODEL_COLORS = {
    prophet: "#a855f7",
    arima: "#f59e0b",
    exponential_smoothing: "#06b6d4",
    xgboost: "#10b981",
    random_forest: "#ec4899",
    ridge: "#6366f1"
  };

  const MODEL_NAMES = {
    prophet: "Prophet",
    arima: "ARIMA",
    exponential_smoothing: "Exponential Smoothing",
    xgboost: "XGBoost",
    random_forest: "Random Forest",
    ridge: "Ridge Regression"
  };

  const isModelVisible = (mId) => {
    if (selectedModel === "all") return true;
    if (selectedModel === "best") return best_model?.id === mId;
    return selectedModel === mId;
  };

  return (
    <div style={{ padding: "30px", maxWidth: "1350px", margin: "0 auto", color: "#f8fafc" }}>
      
      {/* 🔙 HEADER */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "15px", marginBottom: "25px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
          <button onClick={() => navigate(-1)} style={backBtn} title="Back">
            <FaArrowLeft />
          </button>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <h1 style={{ margin: 0, fontSize: "26px", color: "#38bdf8", letterSpacing: "1px" }}>
                {product_name}
              </h1>
              <span style={{ fontSize: "12px", background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8", padding: "4px 10px", borderRadius: "12px", border: "1px solid rgba(56, 189, 248, 0.3)" }}>
                ID: {productId}
              </span>
              <span style={{ fontSize: "12px", background: "rgba(148, 163, 184, 0.1)", color: "#94a3b8", padding: "4px 10px", borderRadius: "12px" }}>
                Category: {inventory_id}
              </span>
            </div>
            <p style={{ margin: "6px 0 0 0", fontSize: "13px", color: "#64748b" }}>
              Multi-model time series forecasting & automated inventory replenishment analysis
            </p>
          </div>
        </div>

        <button onClick={() => fetchProductData(true)} style={refreshBtn}>
          <FaRedo /> Re-Fit Models
        </button>
      </div>

      {/* 🔥 KPI CARDS */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "15px", marginBottom: "30px" }}>
        <KpiCard
          title="Current Stock"
          value={inventory.current_stock}
          sub="Units in Warehouse"
          color="#38bdf8"
        />
        <KpiCard
          title="Reorder Point (ROP)"
          value={inventory.rop}
          sub="Safety threshold"
          color="#facc15"
        />
        <KpiCard
          title="Decision"
          value={inventory.decision}
          sub={inventory.decision === "REORDER" ? "Replenish immediately" : "Stock is adequate"}
          color={inventory.decision === "REORDER" ? "#ef4444" : "#22c55e"}
        />
        <KpiCard
          title="Reorder Quantity"
          value={`${inventory.reorder_quantity} units`}
          sub="Projected 7-day demand"
          color="#10b981"
        />
        <KpiCard
          title="Demand Trend"
          value={trend}
          sub="Velocity indicator"
          color={trend === "Increasing" ? "#38bdf8" : trend === "Decreasing" ? "#ef4444" : "#94a3b8"}
        />
        <KpiCard
          title="Best Model"
          value={best_model?.name || "N/A"}
          sub={`Accuracy: ${best_model?.accuracy || 0}%`}
          color="#facc15"
          badge="★ Top Performer"
        />
      </div>

      {/* 🔘 SECTION TABS */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "25px", borderBottom: "1px solid #1e293b", paddingBottom: "10px" }}>
        <button
          onClick={() => setActiveTab("forecast")}
          style={{ ...tabBtn, borderBottom: activeTab === "forecast" ? "2px solid #38bdf8" : "none", color: activeTab === "forecast" ? "#38bdf8" : "#94a3b8" }}
        >
          Demand Forecast Graph (Multi-Model)
        </button>
        <button
          onClick={() => setActiveTab("metrics")}
          style={{ ...tabBtn, borderBottom: activeTab === "metrics" ? "2px solid #38bdf8" : "none", color: activeTab === "metrics" ? "#38bdf8" : "#94a3b8" }}
        >
          Accuracy & Metrics Evaluation
        </button>
        <button
          onClick={() => setActiveTab("insights")}
          style={{ ...tabBtn, borderBottom: activeTab === "insights" ? "2px solid #38bdf8" : "none", color: activeTab === "insights" ? "#38bdf8" : "#94a3b8" }}
        >
          AI Inventory Insights & Formulas
        </button>
      </div>

      {/* TAB 1: FORECAST GRAPH & MODEL FILTER */}
      {activeTab === "forecast" && (
        <div style={panelBox}>
          {/* MODEL SELECTION PILLS */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "15px", marginBottom: "20px" }}>
            <div>
              <h3 style={{ margin: 0, color: "#f8fafc", fontSize: "18px" }}>
                Multi-Model Demand Forecast (Next 7 Days Ahead)
              </h3>
              <p style={{ margin: "4px 0 0 0", color: "#64748b", fontSize: "13px" }}>
                Showing past 30 days actual retail demand + 7-day projections across 6 models
              </p>
            </div>

            {/* Model Selector Buttons */}
            <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
              <button
                onClick={() => setSelectedModel("all")}
                style={{ ...pillBtn, backgroundColor: selectedModel === "all" ? "#38bdf8" : "#0f172a", color: selectedModel === "all" ? "#000" : "#94a3b8" }}
              >
                All 6 Models
              </button>
              <button
                onClick={() => setSelectedModel("best")}
                style={{ ...pillBtn, backgroundColor: selectedModel === "best" ? "#facc15" : "#0f172a", color: selectedModel === "best" ? "#000" : "#94a3b8" }}
              >
                Best Model ({best_model?.name})
              </button>
              {Object.keys(MODEL_NAMES).map((mId) => (
                <button
                  key={mId}
                  onClick={() => setSelectedModel(mId)}
                  style={{
                    ...pillBtn,
                    backgroundColor: selectedModel === mId ? MODEL_COLORS[mId] : "#0f172a",
                    color: selectedModel === mId ? "#000" : "#94a3b8",
                    borderColor: MODEL_COLORS[mId]
                  }}
                >
                  {MODEL_NAMES[mId]}
                </button>
              ))}
            </div>
          </div>

          {/* RECHARTS MULTI-MODEL LINE GRAPH */}
          <div style={{ height: "420px", width: "100%", marginTop: "10px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={graph} margin={{ top: 15, right: 30, left: 10, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="ds" stroke="#94a3b8" angle={-25} textAnchor="end" height={60} />
                <YAxis stroke="#94a3b8" />
                <Tooltip content={<CustomForecastTooltip />} />
                <Legend wrapperStyle={{ paddingTop: "15px" }} />

                {/* Actual Demand Line */}
                <Line
                  type="monotone"
                  dataKey="actual"
                  name="Actual Demand (Units)"
                  stroke="#f8fafc"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: "#f8fafc" }}
                  connectNulls={false}
                />

                {/* 6 Model Forecast Lines */}
                {isModelVisible("prophet") && (
                  <Line
                    type="monotone"
                    dataKey="prophet"
                    name="Prophet"
                    stroke={MODEL_COLORS.prophet}
                    strokeWidth={selectedModel === "prophet" ? 3 : 2}
                    strokeDasharray="4 4"
                    dot={{ r: 3 }}
                    connectNulls={true}
                  />
                )}

                {isModelVisible("arima") && (
                  <Line
                    type="monotone"
                    dataKey="arima"
                    name="ARIMA(1,1,1)"
                    stroke={MODEL_COLORS.arima}
                    strokeWidth={selectedModel === "arima" ? 3 : 2}
                    strokeDasharray="4 4"
                    dot={{ r: 3 }}
                    connectNulls={true}
                  />
                )}

                {isModelVisible("exponential_smoothing") && (
                  <Line
                    type="monotone"
                    dataKey="exponential_smoothing"
                    name="Exponential Smoothing"
                    stroke={MODEL_COLORS.exponential_smoothing}
                    strokeWidth={selectedModel === "exponential_smoothing" ? 3 : 2}
                    strokeDasharray="4 4"
                    dot={{ r: 3 }}
                    connectNulls={true}
                  />
                )}

                {isModelVisible("xgboost") && (
                  <Line
                    type="monotone"
                    dataKey="xgboost"
                    name="XGBoost"
                    stroke={MODEL_COLORS.xgboost}
                    strokeWidth={selectedModel === "xgboost" ? 3 : 2}
                    strokeDasharray="4 4"
                    dot={{ r: 3 }}
                    connectNulls={true}
                  />
                )}

                {isModelVisible("random_forest") && (
                  <Line
                    type="monotone"
                    dataKey="random_forest"
                    name="Random Forest"
                    stroke={MODEL_COLORS.random_forest}
                    strokeWidth={selectedModel === "random_forest" ? 3 : 2}
                    strokeDasharray="4 4"
                    dot={{ r: 3 }}
                    connectNulls={true}
                  />
                )}

                {isModelVisible("ridge") && (
                  <Line
                    type="monotone"
                    dataKey="ridge"
                    name="Ridge Regression"
                    stroke={MODEL_COLORS.ridge}
                    strokeWidth={selectedModel === "ridge" ? 3 : 2}
                    strokeDasharray="4 4"
                    dot={{ r: 3 }}
                    connectNulls={true}
                  />
                )}

              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Forecast Value Summary Pills */}
          <div style={{ marginTop: "20px", display: "flex", flexWrap: "wrap", gap: "12px", borderTop: "1px solid #1e293b", paddingTop: "15px" }}>
            <span style={{ fontSize: "13px", color: "#94a3b8", alignSelf: "center" }}>Next 3 Days Forecast:</span>
            {data.last_3_days.map((item, idx) => (
              <div key={idx} style={{ background: "#0f172a", border: "1px solid #1e293b", padding: "6px 14px", borderRadius: "8px", fontSize: "13px" }}>
                <span style={{ color: "#64748b", marginRight: "6px" }}>{item.date}:</span>
                <span style={{ color: "#38bdf8", fontWeight: "bold" }}>{item.value} units</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 2: ACCURACY & METRICS EVALUATION */}
      {activeTab === "metrics" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "30px" }}>
          
          {/* 📊 ACCURACY & ERROR BAR CHARTS */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(480px, 1fr))", gap: "25px" }}>
            
            {/* Accuracy Bar Chart */}
            <div style={panelBox}>
              <h3 style={panelTitle}>Product Forecast Accuracy (%) Across Models</h3>
              <p style={panelDesc}>Normalized demand accuracy evaluated on held-out 14-day test split.</p>
              <div style={{ height: "280px", width: "100%" }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={metrics_comparison_chart} margin={{ top: 10, right: 30, left: 0, bottom: 25 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="model" stroke="#94a3b8" angle={-15} textAnchor="end" height={50} />
                    <YAxis stroke="#94a3b8" domain={[50, 85]} />
                    <Tooltip content={<CustomMetricTooltip unit="%" />} />
                    <Bar dataKey="accuracy" name="Accuracy (%)" radius={[6, 6, 0, 0]}>
                      {metrics_comparison_chart.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={MODEL_COLORS[entry.model.toLowerCase().replace(/ /g, "_")] || "#38bdf8"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* MAE & RMSE Error Bar Chart */}
            <div style={panelBox}>
              <h3 style={panelTitle}>Forecast Error Magnitude: MAE vs RMSE</h3>
              <p style={panelDesc}>Lower is better. Units sold deviation against ground truth demand.</p>
              <div style={{ height: "280px", width: "100%" }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={metrics_comparison_chart} margin={{ top: 10, right: 30, left: 0, bottom: 25 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="model" stroke="#94a3b8" angle={-15} textAnchor="end" height={50} />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip content={<CustomMetricTooltip unit=" units" />} />
                    <Legend wrapperStyle={{ paddingTop: "10px" }} />
                    <Bar dataKey="mae" name="MAE (Units)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="rmse" name="RMSE (Units)" fill="#ef4444" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>

          {/* 📋 DETAILED ACCURACY TABLE */}
          <div style={panelBox}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
              <div>
                <h3 style={panelTitle}>Model Performance Leaderboard for {product_name}</h3>
                <span style={{ fontSize: "12px", color: "#64748b" }}>Ranked by Demand Accuracy % and MAE</span>
              </div>
              <span style={bestBadge}>★ Best: {best_model?.name} ({best_model?.accuracy}%)</span>
            </div>

            <div style={{ overflowX: "auto" }}>
              <table style={tableStyle}>
                <thead>
                  <tr style={tableHeaderRow}>
                    <th style={thStyle}>Rank</th>
                    <th style={thStyle}>Model</th>
                    <th style={thStyle}>Category</th>
                    <th style={thStyle}>Accuracy (%)</th>
                    <th style={thStyle}>MAE</th>
                    <th style={thStyle}>RMSE</th>
                    <th style={thStyle}>MAPE (%)</th>
                    <th style={thStyle}>R²</th>
                    <th style={thStyle}>Latency (ms)</th>
                    <th style={thStyle}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {models_accuracy.map((m) => (
                    <tr key={m.id} style={{ ...tableRow, backgroundColor: m.is_best ? "rgba(56, 189, 248, 0.08)" : "transparent" }}>
                      <td style={tdStyle}>
                        <span style={{
                          display: "inline-block",
                          width: "22px",
                          height: "22px",
                          borderRadius: "50%",
                          textAlign: "center",
                          lineHeight: "22px",
                          fontWeight: "bold",
                          fontSize: "11px",
                          backgroundColor: m.rank === 1 ? "#facc15" : "#1e293b",
                          color: m.rank === 1 ? "#000" : "#94a3b8"
                        }}>
                          {m.rank}
                        </span>
                      </td>
                      <td style={{ ...tdStyle, fontWeight: "600", color: MODEL_COLORS[m.id] || "#f8fafc" }}>
                        {m.name}
                      </td>
                      <td style={{ ...tdStyle, color: "#94a3b8", fontSize: "12px" }}>
                        {m.category}
                      </td>
                      <td style={{ ...tdStyle, fontWeight: "bold", color: "#38bdf8" }}>
                        {m.accuracy}%
                      </td>
                      <td style={{ ...tdStyle, color: "#facc15" }}>{m.mae}</td>
                      <td style={{ ...tdStyle, color: "#ef4444" }}>{m.rmse}</td>
                      <td style={tdStyle}>{m.mape}%</td>
                      <td style={tdStyle}>{m.r2}</td>
                      <td style={{ ...tdStyle, color: "#10b981" }}>{m.latency_ms} ms</td>
                      <td style={tdStyle}>
                        {m.is_best ? (
                          <span style={bestBadge}>★ Best Model</span>
                        ) : (
                          <span style={rankBadge}>Rank #{m.rank}</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}

      {/* TAB 3: INSIGHTS & FORMULAS */}
      {activeTab === "insights" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "25px" }}>
          
          {/* AI Decision Rationale */}
          <div style={panelBox}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "12px" }}>
              <FaBrain style={{ color: "#38bdf8", fontSize: "20px" }} />
              <h3 style={panelTitle}>Automated Replenishment Rationale</h3>
            </div>
            <p style={{ color: "#cbd5e1", fontSize: "14px", lineHeight: "1.6" }}>
              {inventory.decision === "REORDER" ? (
                <>
                  <strong style={{ color: "#ef4444" }}>CRITICAL REORDER TRIGGERED: </strong>
                  Current stock level of <strong>{inventory.current_stock} units</strong> has dropped below the calculated Reorder Point (ROP) of <strong>{inventory.rop} units</strong>.
                  The best forecasting model (<strong>{best_model?.name}</strong>, {best_model?.accuracy}% accuracy) anticipates a 7-day cumulative demand of <strong>{inventory.reorder_quantity} units</strong>.
                  Place an order immediately to prevent stockouts during the 3-day supplier lead time.
                </>
              ) : (
                <>
                  <strong style={{ color: "#22c55e" }}>STOCK LEVEL SUFFICIENT: </strong>
                  Current warehouse inventory of <strong>{inventory.current_stock} units</strong> comfortably exceeds the Reorder Point of <strong>{inventory.rop} units</strong>.
                  No replenishment order is required at this time.
                </>
              )}
            </p>

            <div style={{ background: "rgba(0,0,0,0.25)", padding: "14px", borderRadius: "10px", marginTop: "15px" }}>
              <div style={{ fontSize: "13px", color: "#94a3b8", marginBottom: "6px" }}>Reorder Threshold Formula:</div>
              <code style={{ color: "#38bdf8", fontSize: "13px" }}>ROP = (Average Daily Demand × Lead Time) + (2 × σ_Demand)</code>
              <div style={{ fontSize: "12px", color: "#64748b", marginTop: "6px" }}>
                Lead Time: 3 days | Safety Buffer: 2 standard deviations (97.7% service level)
              </div>
            </div>
          </div>

          {/* Model Accuracy Formulas */}
          <div style={panelBox}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "12px" }}>
              <FaInfoCircle style={{ color: "#38bdf8", fontSize: "20px" }} />
              <h3 style={panelTitle}>Evaluation Metrics Reference</h3>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div>
                <strong style={{ color: "#38bdf8", fontSize: "13px" }}>Normalized Demand Accuracy (%):</strong>
                <code style={{ display: "block", background: "#020617", padding: "6px 10px", borderRadius: "6px", color: "#94a3b8", fontSize: "12px", margin: "4px 0" }}>
                  Accuracy = max(0, 100% × (1 - (Σ |y - ŷ| / Σ y)))
                </code>
              </div>

              <div>
                <strong style={{ color: "#facc15", fontSize: "13px" }}>Mean Absolute Error (MAE):</strong>
                <code style={{ display: "block", background: "#020617", padding: "6px 10px", borderRadius: "6px", color: "#94a3b8", fontSize: "12px", margin: "4px 0" }}>
                  MAE = (1/n) × Σ |y_t - ŷ_t|
                </code>
              </div>

              <div>
                <strong style={{ color: "#ef4444", fontSize: "13px" }}>Root Mean Squared Error (RMSE):</strong>
                <code style={{ display: "block", background: "#020617", padding: "6px 10px", borderRadius: "6px", color: "#94a3b8", fontSize: "12px", margin: "4px 0" }}>
                  RMSE = √[(1/n) × Σ (y_t - ŷ_t)²]
                </code>
              </div>
            </div>
          </div>

        </div>
      )}

    </div>
  );
}

// ------------------ SUBCOMPONENTS ------------------

function KpiCard({ title, value, sub, color, badge }) {
  return (
    <div style={{
      padding: "18px",
      borderRadius: "14px",
      background: "rgba(15, 23, 42, 0.5)",
      border: `1px solid ${color}`,
      backdropFilter: "blur(8px)",
      position: "relative"
    }}>
      {badge && (
        <span style={{
          position: "absolute",
          top: "10px",
          right: "10px",
          fontSize: "11px",
          background: "rgba(250, 204, 21, 0.15)",
          color: "#facc15",
          padding: "2px 8px",
          borderRadius: "10px"
        }}>
          {badge}
        </span>
      )}
      <div style={{ color: "#94a3b8", fontSize: "12px", fontWeight: "500", marginBottom: "6px" }}>{title}</div>
      <div style={{ fontSize: "22px", fontWeight: "700", color }}>{value}</div>
      <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>{sub}</div>
    </div>
  );
}

function CustomForecastTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div style={{ background: "#0f172a", border: "1px solid #38bdf8", padding: "10px 14px", borderRadius: "8px", minWidth: "180px" }}>
        <p style={{ margin: "0 0 6px 0", fontWeight: "bold", color: "#f8fafc", borderBottom: "1px solid #1e293b", paddingBottom: "4px" }}>
          Date: {label}
        </p>
        {payload.map((entry, index) => {
          if (entry.value === null || entry.value === undefined) return null;
          return (
            <p key={`tip-${index}`} style={{ margin: "3px 0", color: entry.color || "#38bdf8", fontSize: "12px" }}>
              {entry.name}: <strong>{entry.value} units</strong>
            </p>
          );
        })}
      </div>
    );
  }
  return null;
}

function CustomMetricTooltip({ active, payload, label, unit = "" }) {
  if (active && payload && payload.length) {
    return (
      <div style={{ background: "#0f172a", border: "1px solid #38bdf8", padding: "10px 14px", borderRadius: "8px" }}>
        <p style={{ margin: 0, fontWeight: "bold", color: "#f8fafc" }}>{label}</p>
        {payload.map((entry, index) => (
          <p key={`m-${index}`} style={{ margin: "4px 0 0 0", color: entry.color || "#38bdf8", fontSize: "13px" }}>
            {entry.name}: <strong>{entry.value}{unit}</strong>
          </p>
        ))}
      </div>
    );
  }
  return null;
}

// ------------------ STYLES ------------------
const backBtn = {
  background: "#020617",
  border: "1px solid #38bdf8",
  color: "#38bdf8",
  padding: "8px 14px",
  borderRadius: "10px",
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  fontSize: "14px"
};

const refreshBtn = {
  background: "#020617",
  border: "1px solid #38bdf8",
  color: "#38bdf8",
  padding: "8px 16px",
  borderRadius: "10px",
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  gap: "8px",
  fontWeight: "600",
  fontSize: "13px"
};

const tabBtn = {
  background: "none",
  border: "none",
  padding: "10px 16px",
  cursor: "pointer",
  fontSize: "14px",
  fontWeight: "600",
  transition: "0.2s"
};

const pillBtn = {
  background: "#0f172a",
  border: "1px solid #1e293b",
  padding: "6px 12px",
  borderRadius: "8px",
  cursor: "pointer",
  fontSize: "12px",
  fontWeight: "600",
  transition: "0.2s"
};

const panelBox = {
  padding: "24px",
  borderRadius: "16px",
  background: "rgba(15, 23, 42, 0.4)",
  border: "1px solid #1e293b",
  backdropFilter: "blur(6px)"
};

const panelTitle = {
  margin: "0 0 4px 0",
  fontSize: "18px",
  color: "#f8fafc",
  fontWeight: "600"
};

const panelDesc = {
  margin: "0 0 15px 0",
  fontSize: "13px",
  color: "#64748b"
};

const tableStyle = {
  width: "100%",
  borderCollapse: "collapse",
  fontSize: "13px"
};

const tableHeaderRow = {
  borderBottom: "2px solid #1e293b"
};

const thStyle = {
  textAlign: "left",
  padding: "12px",
  color: "#64748b",
  fontWeight: "600",
  fontSize: "12px",
  textTransform: "uppercase",
  letterSpacing: "0.5px"
};

const tableRow = {
  borderBottom: "1px solid #1e293b",
  transition: "0.2s"
};

const tdStyle = {
  padding: "12px"
};

const bestBadge = {
  background: "rgba(250, 204, 21, 0.15)",
  color: "#facc15",
  padding: "4px 10px",
  borderRadius: "12px",
  border: "1px solid rgba(250, 204, 21, 0.3)",
  fontSize: "11px",
  fontWeight: "700"
};

const rankBadge = {
  background: "rgba(148, 163, 184, 0.1)",
  color: "#94a3b8",
  padding: "3px 8px",
  borderRadius: "10px",
  fontSize: "11px"
};

export default ProductPage;
