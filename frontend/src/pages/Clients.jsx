import { useEffect, useState } from "react";
import api from "../services/api";
import Navbar from "../components/Navbar";

export default function Clients() {
  const [clients, setClients] = useState([]);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");

  const [editingId, setEditingId] = useState(null);

  async function loadClients() {
    try {
      const response = await api.get("/clients");
      setClients(response.data);
    } catch (error) {
      console.error("Erro ao carregar clientes");
    }
  }

  useEffect(() => {
    loadClients();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();

    const clientData = {
      name,
      email,
      phone,
    };

    try {
      // EDITAR
      if (editingId) {
        await api.put(`/clients/${editingId}`, clientData);

        setEditingId(null);
      }

      // CRIAR
      else {
        await api.post("/clients", clientData);
      }

      clearForm();
      loadClients();

    } catch (error) {
      console.error("Erro ao salvar cliente");
    }
  }

  function handleEdit(client) {
    setEditingId(client.id);

    setName(client.name);
    setEmail(client.email);
    setPhone(client.phone);
  }

  async function handleDelete(id) {
    const confirmDelete = window.confirm(
      "Deseja realmente excluir este cliente?"
    );

    if (!confirmDelete) return;

    try {
      await api.delete(`/clients/${id}`);
      loadClients();
    } catch (error) {
      console.error("Erro ao excluir cliente");
    }
  }

  function clearForm() {
    setName("");
    setEmail("");
    setPhone("");
  }

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
          type="text"
          placeholder="Telefone"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          required
        />

        <button type="submit">
          {editingId ? "Atualizar" : "Cadastrar"}
        </button>

        {editingId && (
          <button
            type="button"
            onClick={() => {
              setEditingId(null);
              clearForm();
            }}
          >
            Cancelar
          </button>
        )}
      </form>

      <table
        border="1"
        cellPadding="10"
        style={{
          width: "100%",
          borderCollapse: "collapse",
        }}
      >
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

              <td
                style={{
                  display: "flex",
                  gap: "10px",
                }}
              >
                <button onClick={() => handleEdit(client)}>
                  Editar
                </button>

                <button
                  onClick={() => handleDelete(client.id)}
                >
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