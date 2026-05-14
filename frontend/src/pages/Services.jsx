import { useEffect, useState } from "react";
import api from "../services/api";
import Navbar from "../components/Navbar";

import {
  FaTools,
  FaEdit,
  FaTrash,
  FaPlus,
  FaDollarSign,
} from "react-icons/fa";

export default function Services() {
  const [services, setServices] = useState([]);

  const [name, setName] = useState("");
  const [price, setPrice] = useState("");

  const [editingId, setEditingId] = useState(null);

  async function loadServices() {
    try {
      const response = await api.get("/services");
      setServices(response.data);
    } catch (error) {
      console.error("Erro ao carregar serviços");
    }
  }

  useEffect(() => {
    loadServices();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();

    const serviceData = {
      name,
      price: Number(price),
    };

    try {
      if (editingId) {
        await api.put(`/services/${editingId}`, serviceData);
        setEditingId(null);
      } else {
        await api.post("/services", serviceData);
      }

      clearForm();
      loadServices();

    } catch (error) {
      console.error("Erro ao salvar serviço");
    }
  }

  function handleEdit(service) {
    setEditingId(service.id);

    setName(service.name);
    setPrice(service.price);
  }

  async function handleDelete(id) {
    const confirmDelete = window.confirm(
      "Deseja realmente excluir este serviço?"
    );

    if (!confirmDelete) return;

    try {
      await api.delete(`/services/${id}`);
      loadServices();
    } catch (error) {
      console.error("Erro ao excluir serviço");
    }
  }

  function clearForm() {
    setName("");
    setPrice("");
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#f5f5f5",
        padding: "30px",
      }}
    >
      <Navbar />

      <div
        style={{
          backgroundColor: "white",
          padding: "30px",
          borderRadius: "20px",
          boxShadow: "0 4px 15px rgba(0,0,0,0.08)",
        }}
      >
        <h1
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
            marginBottom: "25px",
            fontSize: "32px",
            color: "#4c1d95",
          }}
        >
          <FaTools />
          Serviços
        </h1>

        <form
          onSubmit={handleSubmit}
          style={{
            display: "flex",
            gap: "15px",
            marginBottom: "30px",
            flexWrap: "wrap",
          }}
        >
          <input
            type="text"
            placeholder="Nome do serviço"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            style={inputStyle}
          />

          <input
            type="number"
            placeholder="Preço"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            required
            style={inputStyle}
          />

          <button type="submit" style={primaryButton}>
            {editingId ? <FaEdit /> : <FaPlus />}
            {editingId ? "Atualizar" : "Cadastrar"}
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
        </form>

        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
          }}
        >
          <thead>
            <tr
              style={{
                backgroundColor: "#ede9fe",
              }}
            >
              <th style={thStyle}>ID</th>
              <th style={thStyle}>Nome</th>
              <th style={thStyle}>Preço</th>
              <th style={thStyle}>Ações</th>
            </tr>
          </thead>

          <tbody>
            {services.map((service) => (
              <tr
                key={service.id}
                style={{
                  borderBottom: "1px solid #ddd",
                }}
              >
                <td style={tdStyle}>{service.id}</td>

                <td style={tdStyle}>{service.name}</td>

                <td style={tdStyle}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                    }}
                  >
                    <FaDollarSign color="#16a34a" />
                    R$ {service.price}
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
                      onClick={() => handleEdit(service)}
                      style={editButton}
                    >
                      <FaEdit />
                      Editar
                    </button>

                    <button
                      onClick={() => handleDelete(service.id)}
                      style={deleteButton}
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
  );
}

const inputStyle = {
  padding: "12px",
  borderRadius: "10px",
  border: "1px solid #ccc",
  minWidth: "220px",
};

const primaryButton = {
  backgroundColor: "#6d28d9",
  color: "white",
  border: "none",
  padding: "12px 18px",
  borderRadius: "10px",
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  gap: "8px",
  fontWeight: "bold",
};

const secondaryButton = {
  backgroundColor: "#e5e7eb",
  border: "none",
  padding: "12px 18px",
  borderRadius: "10px",
  cursor: "pointer",
  fontWeight: "bold",
};

const editButton = {
  backgroundColor: "#2563eb",
  color: "white",
  border: "none",
  padding: "8px 12px",
  borderRadius: "8px",
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  gap: "6px",
};

const deleteButton = {
  backgroundColor: "#dc2626",
  color: "white",
  border: "none",
  padding: "8px 12px",
  borderRadius: "8px",
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  gap: "6px",
};

const thStyle = {
  padding: "15px",
  textAlign: "left",
  color: "#4c1d95",
};

const tdStyle = {
  padding: "15px",
};