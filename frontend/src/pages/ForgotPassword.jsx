import { useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "react-toastify";

import { forgotPassword } from "../services/api";

import "../styles/login.css";

export default function ForgotPassword() {

  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();

    setLoading(true);

    try {
      await forgotPassword(email);
      setSent(true);
    } catch (err) {
      console.error(err);
      toast.error("Não foi possível enviar o e-mail. Tente novamente.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">

        <h1 className="login-title">Recuperar senha</h1>

        {sent ? (
          <>
            <p className="login-subtitle">
              Se o e-mail estiver cadastrado, enviamos um link para você
              redefinir a senha. Verifique sua caixa de entrada.
            </p>

            <p className="login-link">
              <Link to="/login">Voltar para o login</Link>
            </p>
          </>
        ) : (
          <>
            <p className="login-subtitle">
              Informe seu e-mail e enviaremos um link para redefinir a senha.
            </p>

            <form onSubmit={handleSubmit} className="login-form">
              <input
                type="email"
                placeholder="Seu e-mail"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

              <button className="login-btn" type="submit" disabled={loading}>
                {loading ? "Enviando..." : "Enviar link"}
              </button>
            </form>

            <p className="login-link">
              <Link to="/login">Voltar para o login</Link>
            </p>
          </>
        )}

      </div>
    </div>
  );
}
