import { Link, useLocation } from "react-router-dom";
import { FaHome, FaBoxes, FaBars, FaBrain } from "react-icons/fa";
import { useState } from "react";

function Sidebar({ collapsed: propCollapsed, setCollapsed: propSetCollapsed }) {
  const [internalCollapsed, setInternalCollapsed] = useState(false);
  const location = useLocation();

  const collapsed = propCollapsed !== undefined ? propCollapsed : internalCollapsed;
  const setCollapsed = propSetCollapsed || setInternalCollapsed;

  const navItems = [
    { to: "/", label: "Home", icon: <FaHome /> },
    { to: "/inventory", label: "Inventory", icon: <FaBoxes /> },
    { to: "/models", label: "Model Benchmark", icon: <FaBrain /> }
  ];

  return (
    <div style={{
      width: collapsed ? "80px" : "240px",
      height: "100vh",
      background: "#020617",
      padding: "20px",
      display: "flex",
      flexDirection: "column",
      gap: "20px",
      borderRight: "1px solid #1e293b",
      position: "fixed",
      left: 0,
      top: 0,
      transition: "0.3s",
      zIndex: 100
    }}>
      
      {/* 🔘 Toggle Button */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        style={{
          background: "none",
          border: "none",
          color: "#38bdf8",
          fontSize: "20px",
          cursor: "pointer",
          alignSelf: collapsed ? "center" : "flex-end"
        }}
        title={collapsed ? "Expand Sidebar" : "Collapse Sidebar"}
      >
        <FaBars />
      </button>

      {/* Title */}
      {!collapsed && (
        <div style={{ textAlign: "center", marginBottom: "10px" }}>
          <h2 style={{
            color: "#38bdf8",
            margin: 0,
            fontSize: "20px",
            letterSpacing: "1px",
            fontWeight: "700"
          }}>
            AI Warehouse
          </h2>
          <span style={{ fontSize: "11px", color: "#64748b", textTransform: "uppercase", letterSpacing: "1px" }}>
            Multi-Model Suite
          </span>
        </div>
      )}

      {/* Links */}
      <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.to || (item.to !== "/" && location.pathname.startsWith(item.to));
          return (
            <Link
              key={item.to}
              to={item.to}
              style={{
                color: isActive ? "#38bdf8" : "#94a3b8",
                textDecoration: "none",
                padding: "12px 14px",
                borderRadius: "10px",
                display: "flex",
                alignItems: "center",
                gap: "12px",
                background: isActive ? "rgba(56, 189, 248, 0.12)" : "rgba(255,255,255,0.02)",
                border: isActive ? "1px solid rgba(56, 189, 248, 0.3)" : "1px solid transparent",
                transition: "0.2s",
                fontWeight: isActive ? "600" : "500",
                justifyContent: collapsed ? "center" : "flex-start"
              }}
              title={collapsed ? item.label : undefined}
            >
              <span style={{ fontSize: "18px" }}>{item.icon}</span>
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </div>

      {/* Model Count Badge at Bottom */}
      {!collapsed && (
        <div style={{
          marginTop: "auto",
          padding: "12px",
          background: "rgba(56, 189, 248, 0.05)",
          borderRadius: "8px",
          border: "1px solid rgba(56, 189, 248, 0.15)",
          fontSize: "12px",
          color: "#94a3b8"
        }}>
          <div style={{ color: "#38bdf8", fontWeight: "600", marginBottom: "4px" }}>
            6 Active Models
          </div>
          <div>Prophet, ARIMA, Holt-Winters, XGBoost, Random Forest, Ridge</div>
        </div>
      )}
    </div>
  );
}

export default Sidebar;
