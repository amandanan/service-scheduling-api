import { useState } from "react";
import { register } from "../services/api";
import { useNavigate, Link } from "react-router-dom";
import "../App.css";

function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (password.length < 6) {
      setError("A senha deve ter pelo menos 6 caracteres");
      return;
    }

    try {
      await register({
        username,
        email,
        password,
      });

      setSuccess("Conta criada com sucesso!");

      // limpa campos
      setUsername("");
      setEmail("");
      setPassword("");

      // redireciona pro login
      setTimeout(() => {
        navigate("/login");
      }, 1000);

    } catch (err) {
      setError("Erro ao cadastrar");
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1 className="title">Criar conta</h1>
        <p className="subtitle">Preencha os dados abaixo</p>

        <form className="form" onSubmit={handleRegister}>
          <input
            type="text"
            placeholder="Usuário"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <input
            type="email"
            placeholder="E-mail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && <span className="error">{error}</span>}
          {success && <span className="success">{success}</span>}

          <button className="btn primary" type="submit">
            Cadastrar
          </button>
        </form>

        <p className="link">
          Já tem conta? <Link to="/login">Entrar</Link>
        </p>
      </div>
    </div>
  );
}

export default Register;