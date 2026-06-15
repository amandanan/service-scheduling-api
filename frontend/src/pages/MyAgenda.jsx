import { useEffect, useState } from "react";
import { toast } from "react-toastify";

import { getMyAppointments, updateAppointmentStatus } from "../services/api";

import Navbar from "../components/Navbar";

import { FaCalendarAlt, FaCheck, FaTimes } from "react-icons/fa";

import "../styles/services.css";

const STATUS_LABELS = {
  scheduled: "Agendado",
  confirmed: "Confirmado",
  completed: "Concluído",
  no_show: "Falta",
};


export default function MyAgenda() {

  const [appointments, setAppointments] = useState([]);


  async function loadAppointments() {
    try {
      const data = await getMyAppointments();
      setAppointments(data);
    } catch (error) {
      console.error(error);
      toast.error("Erro ao carregar a agenda");
    }
  }


  useEffect(() => {
    loadAppointments();
  }, []);


  async function handleStatus(id, status) {
    try {
      await updateAppointmentStatus(id, status);
      toast.success(status === "completed" ? "Atendimento concluído" : "Marcado como falta");
      loadAppointments();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao atualizar status");
    }
  }


  function formatDateTime(value) {
    const d = new Date(value);
    return `${d.toLocaleDateString("pt-BR")} ${d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}`;
  }


  return (
    <div className="services-page">

      <Navbar />

      <div className="services-container">

        <div className="services-card">

          <h1 className="services-title">
            <FaCalendarAlt />
            Minha Agenda
          </h1>

          <table className="services-table">

            <thead>
              <tr>
                <th>Data</th>
                <th>Cliente</th>
                <th>Serviço</th>
                <th>Status</th>
                <th>Ações</th>
              </tr>
            </thead>

            <tbody>

              {appointments.length > 0 ? (

                appointments.map((a) => {
                  const active = a.status === "scheduled" || a.status === "confirmed";
                  return (
                    <tr key={a.id}>
                      <td>{formatDateTime(a.scheduled_at)}</td>
                      <td>{a.client_name}</td>
                      <td>{a.service_name}</td>
                      <td>
                        <span className={`agenda-status ${a.status}`}>
                          {STATUS_LABELS[a.status] || a.status}
                        </span>
                      </td>
                      <td>
                        {active ? (
                          <div className="actions">
                            <button
                              className="edit-btn"
                              onClick={() => handleStatus(a.id, "completed")}
                            >
                              <FaCheck />
                              Concluir
                            </button>
                            <button
                              className="delete-btn"
                              onClick={() => handleStatus(a.id, "no_show")}
                            >
                              <FaTimes />
                              Falta
                            </button>
                          </div>
                        ) : (
                          <span style={{ color: "#9ca3af" }}>—</span>
                        )}
                      </td>
                    </tr>
                  );
                })

              ) : (

                <tr>
                  <td colSpan="5" style={{ textAlign: "center", padding: "20px" }}>
                    Nenhum atendimento na agenda
                  </td>
                </tr>

              )}

            </tbody>

          </table>

        </div>

      </div>

    </div>
  );
}
