import { useEffect, useState } from "react";
import api from "../services/api";
import Navbar from "../components/Navbar";
import "../styles/appointments.css";
import { toast } from "react-toastify";

import {
  FaCalendarAlt,
  FaEdit,
  FaTrash,
  FaPlus,
  FaClock,
} from "react-icons/fa";

export default function Appointments() {
  const [appointments, setAppointments] = useState([]);

  const [clientId, setClientId] = useState("");
  const [serviceId, setServiceId] = useState("");
  const [date, setDate] = useState("");

  const [editingId, setEditingId] = useState(null);

  async function loadAppointments() {

  try {

    const response = await api.get(
      "/appointments"
    );

    setAppointments(response.data);

  } catch (error) {

    console.error(error);

    toast.error(
      "Erro ao carregar agendamentos"
    );
  }
  }

  useEffect(() => {
    loadAppointments();
  }, []);

  async function handleSubmit(e) {

  e.preventDefault();

  const appointmentData = {
    client_id: Number(clientId),
    service_id: Number(serviceId),
    date,
  };

  try {

    if (editingId) {

      await api.put(
        `/appointments/${editingId}`,
        appointmentData
      );

      toast.success(
        "Agendamento atualizado"
      );

      setEditingId(null);

    } else {

      await api.post(
        "/appointments",
        appointmentData
      );

      toast.success(
        "Agendamento criado"
      );
    }

    clearForm();

    loadAppointments();

  } catch (error) {

    console.error(error);

    toast.error(
      "Erro ao salvar agendamento"
    );
  }
  }

  function handleEdit(appointment) {
    setEditingId(appointment.id);

    setClientId(appointment.client_id);
    setServiceId(appointment.service_id);
    setDate(appointment.date);
  }

  async function handleDelete(id) {

  const confirmDelete = window.confirm(
    "Deseja realmente excluir este agendamento?"
  );

  if (!confirmDelete) return;

  try {

    await api.delete(
      `/appointments/${id}`
    );

    toast.success(
      "Agendamento removido"
    );

    loadAppointments();

  } catch (error) {

    console.error(error);

    toast.error(
      "Erro ao excluir agendamento"
    );
  }
 }

  function clearForm() {
    setClientId("");
    setServiceId("");
    setDate("");
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
          <FaCalendarAlt />
          Agendamentos
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
            type="number"
            placeholder="ID Cliente"
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
            required
            style={inputStyle}
          />

          <input
            type="number"
            placeholder="ID Serviço"
            value={serviceId}
            onChange={(e) => setServiceId(e.target.value)}
            required
            style={inputStyle}
          />

          <input
            type="datetime-local"
            value={date}
            onChange={(e) => setDate(e.target.value)}
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
              <th style={thStyle}>Cliente</th>
              <th style={thStyle}>Serviço</th>
              <th style={thStyle}>Data</th>
              <th style={thStyle}>Ações</th>
            </tr>
          </thead>

          <tbody>
            {appointments.map((appointment) => (
              <tr
                key={appointment.id}
                style={{
                  borderBottom: "1px solid #ddd",
                }}
              >
                <td style={tdStyle}>{appointment.id}</td>

                <td style={tdStyle}>
                  {appointment.client_id}
                </td>

                <td style={tdStyle}>
                  {appointment.service_id}
                </td>

                <td style={tdStyle}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                    }}
                  >
                    <FaClock color="#6d28d9" />
                    {appointment.date}
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
                      onClick={() => handleEdit(appointment)}
                      style={editButton}
                    >
                      <FaEdit />
                      Editar
                    </button>

                    <button
                      onClick={() => handleDelete(appointment.id)}
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