import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";

import {
  getClients,
  createClient,
  deleteClient,
} from "../services/api";

export default function Clients() {
  const [clients, setClients] = useState([]);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");

  async function loadClients() {
    try {
      const data = await getClients();
      setClients(data);
    } catch (error) {
      console.error("Erro ao carregar clientes");
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();

    try {
      await createClient({
        name,
        email,
        phone,
      });

      setName("");
      setEmail("");
      setPhone("");

      loadClients();
    } catch (error) {
      console.error("Erro ao cadastrar cliente");
    }
  }

  async function handleDelete(id) {
    try {
      await deleteClient(id);
      loadClients();
    } catch (error) {
      console.error("Erro ao deletar cliente");
    }
  }

  useEffect(() => {
    loadClients();
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <Navbar />

      <h1>Clientes</h1>

      <form
        onSubmit={handleSubmit}
        style={{
          display: "flex",
          gap: "10px",
          marginBottom: "20px",
          flexWrap: "wrap",
        }}
      >
        <input
          type="text"
          placeholder="Nome"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <input
          type="email"
          placeholder="E-mail"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="text"
          placeholder="Telefone"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
        />

        <button type="submit">Cadastrar</button>
      </form>

      <table width="100%" border="1" cellPadding="10">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome</th>
            <th>E-mail</th>
            <th>Telefone</th>
            <th>Ações</th>
          </tr>
        </thead>

        <tbody>
          {clients.map((client) => (
            <tr key={client.id}>
              <td>{client.id}</td>
              <td>{client.name}</td>
              <td>{client.email}</td>
              <td>{client.phone}</td>

              <td>
                <button onClick={() => handleDelete(client.id)}>
                  Excluir
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}