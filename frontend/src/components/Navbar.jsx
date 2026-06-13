import {
  Link,
  useNavigate,
  useLocation,
} from "react-router-dom";

import {
  FaChartPie,
  FaUsers,
  FaUserTie,
  FaTools,
  FaCalendarAlt,
  FaClock,
  FaSignOutAlt,
  FaLayerGroup,
  FaStar,
  FaCog,
} from "react-icons/fa";

import "../styles/navbar.css";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    navigate("/");
  }

  return (
    <nav className="navbar">

      <div className="navbar-logo">
        <FaLayerGroup />
        <span>Agendador</span>
      </div>

      <div className="navbar-links">

        <Link
          to="/dashboard"
          className={
            location.pathname === "/dashboard"
              ? "navbar-link active"
              : "navbar-link"
          }
        >
          <FaChartPie />
          Dashboard
        </Link>

        <Link
          to="/clients"
          className={
            location.pathname === "/clients"
              ? "navbar-link active"
              : "navbar-link"
          }
        >
          <FaUsers />
          Clientes
        </Link>

        <Link
          to="/services"
          className={
            location.pathname === "/services"
              ? "navbar-link active"
              : "navbar-link"
          }
        >
          <FaTools />
          Serviços
        </Link>

        <Link
          to="/professionals"
          className={
            location.pathname === "/professionals"
              ? "navbar-link active"
              : "navbar-link"
          }
        >
          <FaUserTie />
          Profissionais
        </Link>

        <Link
          to="/appointments"
          className={
            location.pathname === "/appointments"
              ? "navbar-link active"
              : "navbar-link"
          }
        >
          <FaCalendarAlt />
          Agendamentos
        </Link>

        <Link
          to="/reviews"
          className={
            location.pathname === "/reviews"
              ? "navbar-link active"
              : "navbar-link"
          }
        >
          <FaStar />
          Avaliações
        </Link>

        <Link
          to="/working-hours"
          className={
            location.pathname === "/working-hours"
              ? "navbar-link active"
              : "navbar-link"
          }
        >
          <FaClock />
          Horários
        </Link>

        <Link
          to="/settings"
          className={
            location.pathname === "/settings"
              ? "navbar-link active"
              : "navbar-link"
          }
        >
          <FaCog />
          Configurações
        </Link>

        <button
          className="logout-btn"
          onClick={logout}
        >
          <FaSignOutAlt />
          Sair
        </button>

      </div>
    </nav>
  );
}