import { useNavigate } from "react-router-dom";

function InventoryCard({ id, name, image }) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/inventory/${id}`)}
      style={{
        width: "260px",
        height: "240px",
        borderRadius: "20px",
        padding: "25px",
        cursor: "pointer",

        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(56,189,248,0.25)",
        backdropFilter: "blur(12px)",

        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        alignItems: "center",

        transition: "all 0.3s ease-in-out"
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = "translateY(-10px) scale(1.02)";
        e.currentTarget.style.boxShadow = "0 0 25px rgba(56,189,248,0.5)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = "translateY(0) scale(1)";
        e.currentTarget.style.boxShadow = "none";
      }}
    >
      {/* ICON */}
      <img
        src={image}
        alt={name}
        style={{
          width: "90px",
          height: "90px",
          objectFit: "contain",
          filter: "drop-shadow(0 0 8px rgba(56,189,248,0.5))"
        }}
      />

      {/* NAME */}
      <h3
        style={{
          color: "#38bdf8",
          fontWeight: "600",
          textAlign: "center",
          letterSpacing: "1px",
          fontSize: "18px",
          marginTop: "10px"
        }}
      >
        {name}
      </h3>

      {/* ARROW */}
      <div
        style={{
          color: "#38bdf8",
          fontSize: "22px",
          opacity: "0.7"
        }}
      >
        →
      </div>
    </div>
  );
}

export default InventoryCard;