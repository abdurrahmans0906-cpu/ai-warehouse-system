import React from "react";

function DecisionBox({ decision, stock, rop }) {
  const color = decision === "REORDER" ? "#ef4444" : "#22c55e";

  return (
    <div style={{
      background: "rgba(255,255,255,0.03)",
      border: `1px solid ${color}`,
      borderRadius: "16px",
      padding: "20px",
      backdropFilter: "blur(10px)"
    }}>
      <h3 style={{ color }}>Decision Analysis</h3>

      <p style={{ marginTop: "10px" }}>
        Current Stock: {stock}
      </p>

      <p>
        Reorder Point: {rop}
      </p>

      <p style={{ marginTop: "10px", color }}>
        Final Decision: {decision}
      </p>
    </div>
  );
}

export default DecisionBox;