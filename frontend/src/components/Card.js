function Card({ title, value }) {
  return (
    <div
      className="card"
      style={{
        flex: 1,
        border: "1px solid #38bdf8",
        boxShadow: "0 0 10px rgba(56,189,248,0.2)"
      }}
    >
      <h3>{title}</h3>
      <p style={{ fontSize: "24px", color: "#38bdf8" }}>
        {value}
      </p>
    </div>
  );
}

export default Card;