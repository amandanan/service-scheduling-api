import { useState } from "react";
import "../App.css";


function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();

    console.log({
      email,
      password,
    });

    // aqui depois vamos conectar com o backend
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

          <button className="btn primary" type="submit">
            Entrar
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;