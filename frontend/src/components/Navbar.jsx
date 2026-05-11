 import { Link, useNavigate } from "react-router-dom";
import "../App.css"; 

export default function Navbar() {
  const navigate = useNavigate();

  function logout() {
    localStorage.removeItem("token");
    navigate("/");
  }

  return (
    <nav style={{ display: "flex", gap: "15px", marginBottom: "20px" }}>
      <Link to="/dashboard">Dashboard</Link>
      <Link to="/clients">Clientes</Link>
      <Link to="/services">Serviços</Link>
      <Link to="/appointments">Agendamentos</Link>

      <button onClick={logout}>Sair</button>
    </nav>
  );
}
