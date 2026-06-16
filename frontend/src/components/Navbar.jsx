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
  FaUserShield,
} from "react-icons/fa";

import "../styles/navbar.css";

function NavItem({ to, icon, label }) {
  const location = useLocation();
  return (
    <Link
      to={to}
      title={label}
      className={location.pathname === to ? "navbar-link active" : "navbar-link"}
    >
      {icon}
      <span className="nav-label">{label}</span>
    </Link>
  );
}

export default function Navbar() {
  const navigate = useNavigate();

  const role = localStorage.getItem("role") || "owner";
  const isProfessional = role === "professional";
  const isOwner = role === "owner";

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("role");
    navigate("/");
  }

  return (
    <nav className="navbar">

      <div className="navbar-logo">
        <FaLayerGroup />
        <span>Agendador</span>
      </div>

      <div className="navbar-links">

        {isProfessional ? (
          <>
            <NavItem to="/minha-agenda" icon={<FaCalendarAlt />} label="Minha Agenda" />
            <NavItem to="/meus-servicos" icon={<FaTools />} label="Meus Serviços" />
            <NavItem to="/meus-horarios" icon={<FaClock />} label="Meus Horários" />
          </>
        ) : (
          <>
            <NavItem to="/dashboard" icon={<FaChartPie />} label="Dashboard" />
            <NavItem to="/clients" icon={<FaUsers />} label="Clientes" />
            <NavItem to="/services" icon={<FaTools />} label="Serviços" />
            <NavItem to="/professionals" icon={<FaUserTie />} label="Profissionais" />
            <NavItem to="/appointments" icon={<FaCalendarAlt />} label="Agendamentos" />
            <NavItem to="/reviews" icon={<FaStar />} label="Avaliações" />
            <NavItem to="/working-hours" icon={<FaClock />} label="Horários" />
            {isOwner && (
              <NavItem to="/staff" icon={<FaUserShield />} label="Equipe" />
            )}
            {isOwner && (
              <NavItem to="/settings" icon={<FaCog />} label="Configurações" />
            )}
          </>
        )}

        <button className="logout-btn" onClick={logout} title="Sair">
          <FaSignOutAlt />
          <span className="nav-label">Sair</span>
        </button>

      </div>
    </nav>
  );
}
