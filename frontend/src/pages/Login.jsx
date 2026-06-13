import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../services/api";
import { toast } from "react-toastify";

import "../styles/login.css";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleLogin = async (e) => {
  e.preventDefault();

  setError("");

  try {

      const data = await login({
       email,
       password,
      });

      localStorage.setItem(
       "token",
       data.access_token
      );

      localStorage.setItem(
       "refresh_token",
       data.refresh_token
      );

      toast.success("Login realizado com sucesso");

      navigate("/dashboard");

     } 
     
    catch (err) {

      toast.error("E-mail ou senha inválidos");

      setError(err.message);
    }
};

  return (
    <div className="login-container">

      <div className="login-card">

        <h1 className="login-title">
          Login
        </h1>

        <p className="login-subtitle">
          Acesse sua conta
        </p>

        <form
          onSubmit={handleLogin}
          className="login-form"
        >
          <input
            type="email"
            placeholder="Seu e-mail"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
            required
          />

          <input
            type="password"
            placeholder="Sua senha"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            required
          />

          {error && (
            <span className="login-error">
              {error}
            </span>
          )}

          <button className="login-btn" type="submit">
           Entrar
          </button>
        </form>

        <p className="login-link">
          <Link to="/esqueci-senha">
            Esqueci minha senha
          </Link>
        </p>

        <p className="login-link">
          Não possui conta?

          <Link to="/register">
            Cadastrar
          </Link>
        </p>

      </div>
    </div>
  );
}

export default Login;