import { useEffect, useState } from "react";
import api from "../services/api";
import Navbar from "../components/Navbar";

import {
  FaUsers,
  FaEdit,
  FaTrash,
  FaPlus,
  FaEnvelope,
  FaPhone,
} from "react-icons/fa";

import "../styles/clients.css";

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
      if (editingId) {
        await api.put(`/clients/${editingId}`, clientData);
        setEditingId(null);
      } else {
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
    <div className="clients-page">
      <Navbar />

      <div className="clients-container">

        <div className="clients-card">

          <h1 className="clients-title">
            <FaUsers />
            Clientes
          </h1>

          <form
            onSubmit={handleSubmit}
            className="clients-form"
          >
            <input
              type="text"
              placeholder="Nome do cliente"
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

            <button
              type="submit"
              className="primary-btn"
            >
              {editingId ? <FaEdit /> : <FaPlus />}
              {editingId ? "Atualizar" : "Cadastrar"}
            </button>

            {editingId && (
              <button
                type="button"
                className="secondary-btn"
                onClick={() => {
                  setEditingId(null);
                  clearForm();
                }}
              >
                Cancelar
              </button>
            )}
          </form>

          <table className="clients-table">
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

                  <td>
                    <div className="info-cell">
                      <FaEnvelope />
                      {client.email}
                    </div>
                  </td>

                  <td>
                    <div className="info-cell">
                      <FaPhone />
                      {client.phone}
                    </div>
                  </td>

                  <td>
                    <div className="actions">
                      <button
                        className="edit-btn"
                        onClick={() => handleEdit(client)}
                      >
                        <FaEdit />
                        Editar
                      </button>

                      <button
                        className="delete-btn"
                        onClick={() => handleDelete(client.id)}
                      >
                        <FaTrash />
                        Excluir
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>

          </table>
        </div>
      </div>
    </div>
  );
}