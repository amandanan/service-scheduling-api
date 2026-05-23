import { useState } from "react";
import { register } from "../services/api";
import { useNavigate, Link } from "react-router-dom";

import "../styles/register.css";

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

      setUsername("");
      setEmail("");
      setPassword("");

      setTimeout(() => {
        navigate("/login");
      }, 1000);

    } catch (err) {
      setError("Erro ao cadastrar");
    }
  };

  return (
    <div className="register-container">

      <div className="register-card">

        <h1 className="register-title">
          Criar conta
        </h1>

        <p className="register-subtitle">
          Preencha os dados abaixo
        </p>

        <form
          className="register-form"
          onSubmit={handleRegister}
        >
          <input
            type="text"
            placeholder="Usuário"
            value={username}
            onChange={(e) =>
              setUsername(e.target.value)
            }
            required
          />

          <input
            type="email"
            placeholder="E-mail"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
            required
          />

          <input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            required
          />

          {error && (
            <span className="register-error">
              {error}
            </span>
          )}

          {success && (
            <span className="register-success">
              {success}
            </span>
          )}

          <button className="register-btn" type="submit">
            Cadastrar
          </button>
        </form>

        <p className="register-link">
          Já tem conta?

          <Link to="/login">
            Entrar
          </Link>
        </p>

      </div>
    </div>
  );
}

export default Register;