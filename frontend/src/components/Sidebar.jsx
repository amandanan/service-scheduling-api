import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <div
      style={{
        width: "250px",
        background: "white",
        padding: "30px 20px",
        borderRight: "1px solid #e5e7eb",
      }}
    >
      <h2
        style={{
          marginBottom: "40px",
          fontSize: "28px",
          color: "#6d28d9",
          fontWeight: "bold",
        }}
      >
        AgendaPro
      </h2>

      <nav
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "14px",
        }}
      >
        <Link style={linkStyle} to="/dashboard">
          Dashboard
        </Link>

        <Link style={linkStyle} to="/clients">
          Clientes
        </Link>

        <Link style={linkStyle} to="/services">
          Serviços
        </Link>

        <Link style={linkStyle} to="/appointments">
          Agendamentos
        </Link>
      </nav>
    </div>
  );
}

const linkStyle = {
  color: "#374151",
  padding: "14px",
  borderRadius: "12px",
  background: "#f5f3ff",
  fontWeight: "600",
};