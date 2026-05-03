import { useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../App.css";

function Home() {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (token) {
      navigate("/dashboard");
    }
  }, [navigate]);

  return (
    <div className="container">
      <div className="card">
        <h1 className="title">Sistema de Agendamentos</h1>
        <p className="subtitle">
          Gerencie seus horários de forma simples e moderna
        </p>

        <div className="buttons">
          <Link to="/login" className="btn primary">
            Login
          </Link>

          <Link to="/register" className="btn outline">
            Cadastro
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Home;