import { useState } from "react";
import { register } from "../services/api";
import { useNavigate, Link } from "react-router-dom";

import "../styles/register.css";

function Register() {
  const [fullName, setFullName] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [cpf, setCpf] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const navigate = useNavigate();

  async function handleRegister(e) {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (password.length < 6) {
      setError("A senha deve ter pelo menos 6 caracteres");
      return;
    }

    try {
      await register({
        full_name: fullName,
        birth_date: birthDate,
        cpf,
        phone,
        email,
        password,
      });

      setSuccess("Conta criada com sucesso!");

      setFullName("");
      setBirthDate("");
      setCpf("");
      setPhone("");
      setEmail("");
      setPassword("");

      setTimeout(() => {
        navigate("/login");
      }, 1200);

    } catch (err) {
      setError("Erro ao cadastrar usuário");
    }
  }

  return (
    <div className="register-container">
      <div className="register-card">

        <h1 className="register-title">
          Criar conta
        </h1>

        <p className="register-subtitle">
          Preencha seus dados
        </p>

        <form
          className="register-form"
          onSubmit={handleRegister}
        >

          <input
            type="text"
            placeholder="Nome completo"
            value={fullName}
            onChange={(e) =>
              setFullName(e.target.value)
            }
            required
          />

          <input
            type="date"
            value={birthDate}
            onChange={(e) =>
              setBirthDate(e.target.value)
            }
            required
          />

          <input
            type="text"
            placeholder="CPF"
            value={cpf}
            onChange={(e) =>
              setCpf(e.target.value)
            }
            required
          />

          <input
            type="text"
            placeholder="Telefone"
            value={phone}
            onChange={(e) =>
              setPhone(e.target.value)
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
            <span className="error">
              {error}
            </span>
          )}

          {success && (
            <span className="success">
              {success}
            </span>
          )}

          <button
            className="register-btn"
            type="submit"
          >
            Cadastrar
          </button>

        </form>

        <p className="register-link">
          Já possui conta?{" "}
          <Link to="/login">
            Entrar
          </Link>
        </p>

      </div>
    </div>
  );
}

export default Register;