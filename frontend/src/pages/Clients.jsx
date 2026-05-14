import { useEffect, useState } from "react";
import api from "../services/api";
import Navbar from "../components/Navbar";

import {
  FaUserPlus,
  FaEdit,
  FaTrash,
  FaUsers,
  FaEnvelope,
  FaPhone,
} from "react-icons/fa";

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
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#f4f6fb",
        padding: "30px",
      }}
    >
      <Navbar />

      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            marginBottom: "30px",
          }}
        >
          <FaUsers size={32} color="#6d28d9" />

          <h1
            style={{
              fontSize: "32px",
              color: "#1e1e2f",
              margin: 0,
            }}
          >
            Gestão de Clientes
          </h1>
        </div>

        {/* FORM */}
        <div
          style={{
            backgroundColor: "#fff",
            padding: "25px",
            borderRadius: "18px",
            boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
            marginBottom: "30px",
          }}
        >
          <form
            onSubmit={handleSubmit}
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: "15px",
            }}
          >
            <div>
              <label
                style={{
                  display: "block",
                  marginBottom: "8px",
                  fontWeight: "600",
                }}
              >
                Nome
              </label>

              <input
                type="text"
                placeholder="Digite o nome"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                style={inputStyle}
              />
            </div>

            <div>
              <label
                style={{
                  display: "block",
                  marginBottom: "8px",
                  fontWeight: "600",
                }}
              >
                E-mail
              </label>

              <input
                type="email"
                placeholder="Digite o e-mail"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={inputStyle}
              />
            </div>

            <div>
              <label
                style={{
                  display: "block",
                  marginBottom: "8px",
                  fontWeight: "600",
                }}
              >
                Telefone
              </label>

              <input
                type="text"
                placeholder="Digite o telefone"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                required
                style={inputStyle}
              />
            </div>

            <div
              style={{
                display: "flex",
                alignItems: "end",
                gap: "10px",
              }}
            >
              <button type="submit" style={primaryButton}>
                <FaUserPlus />
                {editingId ? " Atualizar" : " Cadastrar"}
              </button>

              {editingId && (
                <button
                  type="button"
                  onClick={() => {
                    setEditingId(null);
                    clearForm();
                  }}
                  style={secondaryButton}
                >
                  Cancelar
                </button>
              )}
            </div>
          </form>
        </div>

        {/* TABELA */}
        <div
          style={{
            backgroundColor: "#fff",
            borderRadius: "18px",
            overflow: "hidden",
            boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
          }}
        >
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
            }}
          >
            <thead
              style={{
                backgroundColor: "#6d28d9",
                color: "#fff",
              }}
            >
              <tr>
                <th style={thStyle}>ID</th>
                <th style={thStyle}>Nome</th>
                <th style={thStyle}>E-mail</th>
                <th style={thStyle}>Telefone</th>
                <th style={thStyle}>Ações</th>
              </tr>
            </thead>

            <tbody>
              {clients.map((client) => (
                <tr
                  key={client.id}
                  style={{
                    borderBottom: "1px solid #eee",
                  }}
                >
                  <td style={tdStyle}>{client.id}</td>

                  <td style={tdStyle}>{client.name}</td>

                  <td style={tdStyle}>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                      }}
                    >
                      <FaEnvelope color="#6d28d9" />
                      {client.email}
                    </div>
                  </td>

                  <td style={tdStyle}>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "8px",
                      }}
                    >
                      <FaPhone color="#6d28d9" />
                      {client.phone}
                    </div>
                  </td>

                  <td style={tdStyle}>
                    <div
                      style={{
                        display: "flex",
                        gap: "10px",
                      }}
                    >
                      <button
                        onClick={() => handleEdit(client)}
                        style={editButton}
                      >
                        <FaEdit />
                      </button>

                      <button
                        onClick={() => handleDelete(client.id)}
                        style={deleteButton}
                      >
                        <FaTrash />
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

/* ESTILOS */

const inputStyle = {
  width: "100%",
  padding: "12px",
  borderRadius: "10px",
  border: "1px solid #d1d5db",
  fontSize: "15px",
  outline: "none",
};

const primaryButton = {
  backgroundColor: "#6d28d9",
  color: "#fff",
  border: "none",
  padding: "12px 18px",
  borderRadius: "10px",
  cursor: "pointer",
  fontWeight: "600",
  display: "flex",
  alignItems: "center",
  gap: "8px",
};

const secondaryButton = {
  backgroundColor: "#e5e7eb",
  color: "#111827",
  border: "none",
  padding: "12px 18px",
  borderRadius: "10px",
  cursor: "pointer",
  fontWeight: "600",
};

const editButton = {
  backgroundColor: "#2563eb",
  color: "#fff",
  border: "none",
  padding: "10px",
  borderRadius: "8px",
  cursor: "pointer",
};

const deleteButton = {
  backgroundColor: "#dc2626",
  color: "#fff",
  border: "none",
  padding: "10px",
  borderRadius: "8px",
  cursor: "pointer",
};

const thStyle = {
  padding: "16px",
  textAlign: "left",
};

const tdStyle = {
  padding: "16px",
};