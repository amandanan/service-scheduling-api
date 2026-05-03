import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../services/api";
import "../App.css";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    setError("");

    try {
      const data = await login({ email, password });

      // salva token
      localStorage.setItem("token", data.access_token);

      // redireciona
      navigate("/dashboard");

    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1 className="title">Login</h1>
        <p className="subtitle">Acesse sua conta</p>

        <form onSubmit={handleLogin} className="form">
          <input
            type="email"
            placeholder="Seu e-mail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Sua senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {/* erro */}
          {error && <span className="error">{error}</span>}

          <button className="btn primary" type="submit">
            Entrar
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;