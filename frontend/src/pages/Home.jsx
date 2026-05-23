import { useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../styles/home.css";

function Home() {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (token) {
      navigate("/dashboard");
    }
  }, [navigate]);

  return (
    <div className="home-container">
      <div className="home-card">
        <h1 className="home-title">
          Sistema de Agendamentos
        </h1>

        <p className="home-subtitle">
          Gerencie seus horários de forma simples e moderna
        </p>

        <div className="home-buttons">
          <Link
            to="/login"
            className="home-btn home-btn-primary"
          >
            Login
          </Link>

          <Link
            to="/register"
            className="home-btn home-btn-outline"
          >
            Cadastro
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Home;