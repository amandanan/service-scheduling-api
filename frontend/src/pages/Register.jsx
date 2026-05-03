import { useState } from "react";
import "../App.css";

function Register() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    // validação simples 
    if (password.length < 6) {
      setError("A senha deve ter pelo menos 6 caracteres");
      return;
    }

    try {
      // 👉 depois vamos conectar com FastAPI
      setSuccess("Conta criada com sucesso!");
      
      // limpa campos
      setUsername("");
      setEmail("");
      setPassword("");
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

          {/* ERRO */}
          {error && <span className="error">{error}</span>}

          {/* SUCESSO */}
          {success && <span className="success">{success}</span>}

          <button className="btn primary" type="submit">
            Cadastrar
          </button>
        </form>

        {/* link para login */}
        <p className="link">
          Já tem conta? <a href="/login">Entrar</a>
        </p>
      </div>
    </div>
  );
}

export default Register;