import { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { toast } from "react-toastify";

import { resetPassword } from "../services/api";

import "../styles/login.css";

export default function ResetPassword() {

  const { token } = useParams();
  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();

    if (password.length < 6) {
      toast.error("A senha deve ter ao menos 6 caracteres");
      return;
    }

    if (password !== confirm) {
      toast.error("As senhas não coincidem");
      return;
    }

    setLoading(true);

    try {
      await resetPassword(token, password);
      toast.success("Senha redefinida com sucesso");
      navigate("/login");
    } catch (err) {
      const message =
        err.response?.status === 400
          ? "Link inválido ou expirado. Solicite um novo."
          : "Não foi possível redefinir a senha.";
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">

        <h1 className="login-title">Nova senha</h1>

        <p className="login-subtitle">Crie uma nova senha para sua conta.</p>

        <form onSubmit={handleSubmit} className="login-form">
          <input
            type="password"
            placeholder="Nova senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Confirmar nova senha"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required
          />

          <button className="login-btn" type="submit" disabled={loading}>
            {loading ? "Salvando..." : "Redefinir senha"}
          </button>
        </form>

        <p className="login-link">
          <Link to="/login">Voltar para o login</Link>
        </p>

      </div>
    </div>
  );
}
