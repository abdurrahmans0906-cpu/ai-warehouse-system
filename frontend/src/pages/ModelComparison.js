import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend, Cell
} from "recharts";
import { FaBrain, FaTrophy, FaBolt, FaCheckCircle, FaCalculator, FaRedo, FaInfoCircle } from "react-icons/fa";
import { API_BASE } from "../api";

function ModelComparison() {
  const [benchmark, setBenchmark] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  const fetchBenchmark = (refresh = false) => {
    setLoading(true);
    fetch(`${API_BASE}/models/benchmark?sample_size=6&refresh=${refresh}`)
      .then(res => res.json())
      .then(data => {
        setBenchmark(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching benchmark:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchBenchmark();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: "40px", textAlign: "center", color: "#38bdf8" }}>
        <h2>Evaluating 6 AI Forecasting Models on Retail Inventory Dataset...</h2>
        <p style={{ color: "#94a3b8" }}>Running Prophet, ARIMA, Exponential Smoothing, XGBoost, Random Forest, and Ridge Regression.</p>
      </div>
    );
  }

  if (!benchmark || !benchmark.models) {
    return (
      <div style={{ padding: "40px", textAlign: "center", color: "#ef4444" }}>
        <h2>Failed to load model benchmark</h2>
        <button onClick={() => fetchBenchmark(true)} style={btnStyle}>
          Retry Evaluation
        </button>
      </div>
    );
  }

  const { models, best_overall, chart_data } = benchmark;
  const bestModel = best_overall || models[0];

  const avgAccuracy = (models.reduce((sum, m) => sum + m.accuracy, 0) / models.length).toFixed(1);
  const fastestModel = [...models].sort((a, b) => a.latency_ms - b.latency_ms)[0];
  const lowestMaeModel = [...models].sort((a, b) => a.mae - b.mae)[0];

  const MODEL_COLORS = {
    "Exponential Smoothing": "#06b6d4",
    "Prophet": "#a855f7",
    "ARIMA": "#f59e0b",
    "XGBoost": "#10b981",
    "Ridge Regression": "#6366f1",
    "Random Forest": "#ec4899"
  };

  return (
    <div style={{ padding: "30px", maxWidth: "1350px", margin: "0 auto", color: "#f8fafc" }}>
      {/* 🚀 HEADER */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "15px", marginBottom: "30px" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <FaBrain style={{ color: "#38bdf8", fontSize: "28px" }} />
            <h1 style={{ margin: 0, fontSize: "28px", color: "#38bdf8", letterSpacing: "1px" }}>
              Multi-Model AI Forecasting & Accuracy Evaluation
            </h1>
          </div>
          <p style={{ color: "#94a3b8", margin: "8px 0 0 0", fontSize: "14px" }}>
            Rigorous evaluation of 6 time-series & machine learning models on the Retail Store Inventory Dataset (<code>inventory_final.csv</code>).
          </p>
        </div>

        <button onClick={() => fetchBenchmark(true)} style={btnStyle}>
          <FaRedo /> Re-Run Benchmark
        </button>
      </div>

      {/* 🏆 SUMMARY KPI CARDS */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "20px", marginBottom: "35px" }}>
        <SummaryCard
          icon={<FaTrophy style={{ color: "#facc15", fontSize: "22px" }} />}
          title="Best Model Overall"
          value={bestModel.name}
          sub={`Accuracy: ${bestModel.accuracy}% | MAE: ${bestModel.mae}`}
          borderColor="#facc15"
        />
        <SummaryCard
          icon={<FaCheckCircle style={{ color: "#38bdf8", fontSize: "22px" }} />}
          title="Average Demand Accuracy"
          value={`${avgAccuracy}%`}
          sub="Across all 6 evaluated models"
          borderColor="#38bdf8"
        />
        <SummaryCard
          icon={<FaBolt style={{ color: "#10b981", fontSize: "22px" }} />}
          title="Fastest Inference"
          value={fastestModel.name}
          sub={`Latency: ${fastestModel.latency_ms} ms`}
          borderColor="#10b981"
        />
        <SummaryCard
          icon={<FaCalculator style={{ color: "#a855f7", fontSize: "22px" }} />}
          title="Lowest Error (MAE)"
          value={`${lowestMaeModel.mae} units`}
          sub={`Model: ${lowestMaeModel.name}`}
          borderColor="#a855f7"
        />
      </div>

      {/* 🔘 TAB NAVIGATION */}
      <div style={{ display: "flex", gap: "12px", marginBottom: "25px", borderBottom: "1px solid #1e293b", paddingBottom: "12px" }}>
        <TabButton label="Benchmark Overview & Charts" active={activeTab === "overview"} onClick={() => setActiveTab("overview")} />
        <TabButton label="Model Architectures & Specs" active={activeTab === "specs"} onClick={() => setActiveTab("specs")} />
        <TabButton label="Evaluation Formulas & Metrics" active={activeTab === "formulas"} onClick={() => setActiveTab("formulas")} />
      </div>

      {/* TAB 1: OVERVIEW & CHARTS */}
      {activeTab === "overview" && (
        <>
          {/* 📊 ACCURACY & ERROR COMPARISON CHARTS */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(480px, 1fr))", gap: "25px", marginBottom: "35px" }}>
            
            {/* Chart 1: Accuracy % */}
            <div style={panelBox}>
              <h3 style={panelTitle}>Model Forecast Accuracy Comparison (%)</h3>
              <p style={panelDesc}>Normalized demand accuracy: Higher is better (WAPE-derived metric).</p>
              <div style={{ height: "300px", width: "100%", marginTop: "15px" }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chart_data} margin={{ top: 10, right: 30, left: 0, bottom: 25 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="model" stroke="#94a3b8" angle={-15} textAnchor="end" height={60} />
                    <YAxis stroke="#94a3b8" domain={[50, 85]} />
                    <Tooltip content={<CustomTooltip unit="%" />} />
                    <Bar dataKey="accuracy" name="Accuracy (%)" radius={[6, 6, 0, 0]}>
                      {chart_data.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={MODEL_COLORS[entry.model] || "#38bdf8"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 2: MAE & RMSE Errors */}
            <div style={panelBox}>
              <h3 style={panelTitle}>Forecast Error Comparison: MAE vs RMSE (Units)</h3>
              <p style={panelDesc}>Mean Absolute Error & Root Mean Squared Error (Lower is better).</p>
              <div style={{ height: "300px", width: "100%", marginTop: "15px" }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chart_data} margin={{ top: 10, right: 30, left: 0, bottom: 25 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                    <XAxis dataKey="model" stroke="#94a3b8" angle={-15} textAnchor="end" height={60} />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip content={<CustomTooltip unit=" units" />} />
                    <Legend wrapperStyle={{ paddingTop: "10px" }} />
                    <Bar dataKey="mae" name="MAE (Units)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="rmse" name="RMSE (Units)" fill="#ef4444" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>

          {/* 📋 COMPREHENSIVE BENCHMARK TABLE */}
          <div style={panelBox}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
              <h3 style={panelTitle}>Complete Model Accuracy & Evaluation Benchmark</h3>
              <span style={{ fontSize: "12px", color: "#64748b" }}>Evaluated across retail store inventory products</span>
            </div>

            <div style={{ overflowX: "auto" }}>
              <table style={tableStyle}>
                <thead>
                  <tr style={tableHeaderRow}>
                    <th style={thStyle}>Rank</th>
                    <th style={thStyle}>Model Name</th>
                    <th style={thStyle}>Category</th>
                    <th style={thStyle}>Accuracy (%)</th>
                    <th style={thStyle}>MAE</th>
                    <th style={thStyle}>RMSE</th>
                    <th style={thStyle}>MAPE (%)</th>
                    <th style={thStyle}>R² Score</th>
                    <th style={thStyle}>Latency (ms)</th>
                    <th style={thStyle}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {models.map((m) => (
                    <tr key={m.id} style={{ ...tableRow, backgroundColor: m.is_best ? "rgba(56, 189, 248, 0.08)" : "transparent" }}>
                      <td style={tdStyle}>
                        <span style={{
                          display: "inline-block",
                          width: "24px",
                          height: "24px",
                          borderRadius: "50%",
                          textAlign: "center",
                          lineHeight: "24px",
                          fontWeight: "bold",
                          fontSize: "12px",
                          backgroundColor: m.rank === 1 ? "#facc15" : "#1e293b",
                          color: m.rank === 1 ? "#000" : "#94a3b8"
                        }}>
                          {m.rank}
                        </span>
                      </td>
                      <td style={{ ...tdStyle, fontWeight: "600", color: MODEL_COLORS[m.name] || "#f8fafc" }}>
                        {m.name}
                      </td>
                      <td style={{ ...tdStyle, color: "#94a3b8", fontSize: "12px" }}>
                        {m.category}
                      </td>
                      <td style={{ ...tdStyle, fontWeight: "bold", color: "#38bdf8" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <span>{m.accuracy}%</span>
                          <div style={{ width: "60px", height: "6px", backgroundColor: "#1e293b", borderRadius: "3px", overflow: "hidden" }}>
                            <div style={{ width: `${Math.min(100, m.accuracy)}%`, height: "100%", backgroundColor: "#38bdf8" }} />
                          </div>
                        </div>
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
        </>
      )}

      {/* TAB 2: MODEL ARCHITECTURES & SPECS */}
      {activeTab === "specs" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "20px" }}>
          {models.map((m) => (
            <div key={m.id} style={{ ...panelBox, borderLeft: `4px solid ${MODEL_COLORS[m.name] || "#38bdf8"}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "10px" }}>
                <div>
                  <h3 style={{ margin: 0, color: MODEL_COLORS[m.name] || "#38bdf8", fontSize: "18px" }}>{m.name}</h3>
                  <span style={{ fontSize: "12px", color: "#64748b", textTransform: "uppercase", letterSpacing: "0.5px" }}>{m.category}</span>
                </div>
                {m.is_best && <span style={bestBadge}>★ Highest Accuracy</span>}
              </div>

              <p style={{ color: "#cbd5e1", fontSize: "14px", lineHeight: "1.5", margin: "10px 0 15px 0" }}>
                {m.description}
              </p>

              <div style={{ background: "rgba(0,0,0,0.2)", padding: "12px", borderRadius: "8px", fontSize: "13px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                  <span style={{ color: "#94a3b8" }}>Demand Accuracy:</span>
                  <span style={{ color: "#38bdf8", fontWeight: "bold" }}>{m.accuracy}%</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                  <span style={{ color: "#94a3b8" }}>Mean Absolute Error:</span>
                  <span style={{ color: "#facc15" }}>{m.mae} units</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                  <span style={{ color: "#94a3b8" }}>Root Mean Sq Error:</span>
                  <span style={{ color: "#ef4444" }}>{m.rmse} units</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ color: "#94a3b8" }}>Inference Latency:</span>
                  <span style={{ color: "#10b981" }}>{m.latency_ms} ms</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* TAB 3: EVALUATION FORMULAS & METRICS */}
      {activeTab === "formulas" && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))", gap: "20px" }}>
          
          <FormulaCard
            name="Normalized Demand Accuracy (%)"
            formula="Accuracy = max(0, 100% * (1 - (sum |y - yhat| / sum y)))"
            description="Derived from Weighted Absolute Percentage Error (WAPE). Evaluates the percentage of demand successfully anticipated without blowing up when sales approach zero."
            interpretation="Scores above 70% represent high-grade retail forecasting suitable for automated reordering."
          />

          <FormulaCard
            name="Mean Absolute Error (MAE)"
            formula="MAE = (1 / n) * sum_{t=1}^n |y_t - yhat_t|"
            description="Measures the average magnitude of the errors in a set of forecasts, without considering their direction. Expressed directly in units sold."
            interpretation="Lower values denote tighter forecasts. A difference of 10 units implies daily projections deviate by 10 units on average."
          />

          <FormulaCard
            name="Root Mean Squared Error (RMSE)"
            formula="RMSE = sqrt((1 / n) * sum_{t=1}^n (y_t - yhat_t)^2)"
            description="Quadratic scoring rule that measures average error magnitude while assigning disproportionate weight to large outliers and sudden demand spikes."
            interpretation="When RMSE is notably higher than MAE, large sporadic demand variance occurred in that time window."
          />

          <FormulaCard
            name="Mean Absolute Percentage Error (MAPE)"
            formula="MAPE = (100% / n) * sum_{t=1}^n |(y_t - yhat_t) / y_t|"
            description="Expresses forecast error as a relative percentage of actual daily sales, providing intuitive scale-independent interpretation."
            interpretation="Standard retail inventory benchmark. Scores below 40% are typical for highly variable daily store demand."
          />

          <FormulaCard
            name="Coefficient of Determination (R² Score)"
            formula="R² = 1 - (sum (y_t - yhat_t)^2 / sum (y_t - y_bar)^2)"
            description="Proportion of variance in retail demand that is explained by the forecasting model versus a naïve mean predictor."
            interpretation="Measures structural predictive power across the test window."
          />

          <FormulaCard
            name="Reorder Point Formula (ROP)"
            formula="ROP = (Average Daily Demand * Lead Time) + (2 * Standard Deviation)"
            description="Determines the minimum safety inventory threshold before replenishment triggers, protecting against stockouts during supplier lead time."
            interpretation="When Current Stock <= ROP, the system issues an automated REORDER decision."
          />

        </div>
      )}

    </div>
  );
}

// ------------------ SUBCOMPONENTS ------------------

function SummaryCard({ icon, title, value, sub, borderColor }) {
  return (
    <div style={{
      padding: "20px",
      borderRadius: "14px",
      background: "rgba(15, 23, 42, 0.6)",
      border: `1px solid ${borderColor}`,
      backdropFilter: "blur(8px)"
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px" }}>
        {icon}
        <span style={{ color: "#94a3b8", fontSize: "13px", fontWeight: "500" }}>{title}</span>
      </div>
      <div style={{ fontSize: "22px", fontWeight: "700", color: "#f8fafc", marginBottom: "4px" }}>
        {value}
      </div>
      <div style={{ fontSize: "12px", color: "#64748b" }}>{sub}</div>
    </div>
  );
}

function TabButton({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: "10px 18px",
        borderRadius: "8px",
        background: active ? "rgba(56, 189, 248, 0.15)" : "transparent",
        color: active ? "#38bdf8" : "#94a3b8",
        border: active ? "1px solid rgba(56, 189, 248, 0.4)" : "1px solid transparent",
        cursor: "pointer",
        fontWeight: active ? "600" : "500",
        fontSize: "14px",
        transition: "0.2s"
      }}
    >
      {label}
    </button>
  );
}

function FormulaCard({ name, formula, description, interpretation }) {
  return (
    <div style={panelBox}>
      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px" }}>
        <FaInfoCircle style={{ color: "#38bdf8" }} />
        <h4 style={{ margin: 0, color: "#f8fafc", fontSize: "16px" }}>{name}</h4>
      </div>
      <div style={{
        background: "#020617",
        padding: "10px 14px",
        borderRadius: "8px",
        border: "1px solid #1e293b",
        fontFamily: "monospace",
        color: "#38bdf8",
        fontSize: "13px",
        marginBottom: "12px",
        overflowX: "auto"
      }}>
        {formula}
      </div>
      <p style={{ color: "#94a3b8", fontSize: "13px", lineHeight: "1.5", marginBottom: "8px" }}>
        {description}
      </p>
      <div style={{ fontSize: "12px", color: "#64748b", borderTop: "1px solid #1e293b", paddingTop: "8px" }}>
        <strong style={{ color: "#cbd5e1" }}>Application: </strong>{interpretation}
      </div>
    </div>
  );
}

function CustomTooltip({ active, payload, label, unit = "" }) {
  if (active && payload && payload.length) {
    return (
      <div style={{ background: "#0f172a", border: "1px solid #38bdf8", padding: "10px 14px", borderRadius: "8px" }}>
        <p style={{ margin: 0, fontWeight: "bold", color: "#f8fafc" }}>{label}</p>
        {payload.map((entry, index) => (
          <p key={`item-${index}`} style={{ margin: "4px 0 0 0", color: entry.color || "#38bdf8", fontSize: "13px" }}>
            {entry.name}: <strong>{entry.value}{unit}</strong>
          </p>
        ))}
      </div>
    );
  }
  return null;
}

// ------------------ STYLES ------------------
const btnStyle = {
  background: "#020617",
  border: "1px solid #38bdf8",
  color: "#38bdf8",
  padding: "10px 18px",
  borderRadius: "10px",
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  gap: "8px",
  fontWeight: "600",
  fontSize: "14px"
};

const panelBox = {
  padding: "22px",
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
  fontSize: "14px"
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
  fontSize: "12px",
  fontWeight: "700"
};

const rankBadge = {
  background: "rgba(148, 163, 184, 0.1)",
  color: "#94a3b8",
  padding: "4px 8px",
  borderRadius: "12px",
  fontSize: "11px"
};

export default ModelComparison;
