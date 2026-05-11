import { useEffect, useState } from "react";
import api from "../services/api";
import Navbar from "../components/Navbar";

export default function Appointments() {
  const [appointments, setAppointments] = useState([]);
  const [clients, setClients] = useState([]);
  const [services, setServices] = useState([]);

  const [clientId, setClientId] = useState("");
  const [serviceId, setServiceId] = useState("");
  const [date, setDate] = useState("");

  async function loadData() {
    try {
      const [appointmentsRes, clientsRes, servicesRes] = await Promise.all([
        api.get("/appointments"),
        api.get("/clients"),
        api.get("/services"),
      ]);

      setAppointments(appointmentsRes.data);
      setClients(clientsRes.data);
      setServices(servicesRes.data);
    } catch (error) {
      console.error("Erro ao carregar dados");
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();

    try {
      await api.post("/appointments", {
        client_id: Number(clientId),
        service_id: Number(serviceId),
        appointment_date: date,
      });

      setClientId("");
      setServiceId("");
      setDate("");

      loadData();
    } catch (error) {
      console.error("Erro ao criar agendamento");
    }
  }

  async function handleDelete(id) {
    try {
      await api.delete(`/appointments/${id}`);
      loadData();
    } catch (error) {
      console.error("Erro ao deletar agendamento");
    }
  }

  return (
    <div style={{ padding: "20px" }}>
      <Navbar />

      <h1>Agendamentos</h1>

      <form
        onSubmit={handleSubmit}
        style={{
          display: "flex",
          gap: "10px",
          marginBottom: "20px",
          flexWrap: "wrap",
        }}
      >
        <select
          value={clientId}
          onChange={(e) => setClientId(e.target.value)}
          required
        >
          <option value="">Selecione o cliente</option>

          {clients.map((client) => (
            <option key={client.id} value={client.id}>
              {client.name}
            </option>
          ))}
        </select>

        <select
          value={serviceId}
          onChange={(e) => setServiceId(e.target.value)}
          required
        >
          <option value="">Selecione o serviço</option>

          {services.map((service) => (
            <option key={service.id} value={service.id}>
              {service.name}
            </option>
          ))}
        </select>

        <input
          type="datetime-local"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          required
        />

        <button type="submit">Agendar</button>
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
            <th>Cliente</th>
            <th>Serviço</th>
            <th>Data</th>
            <th>Ações</th>
          </tr>
        </thead>

        <tbody>
          {appointments.map((appointment) => (
            <tr key={appointment.id}>
              <td>{appointment.id}</td>

              <td>
                {appointment.client?.name || appointment.client_id}
              </td>

              <td>
                {appointment.service?.name || appointment.service_id}
              </td>

              <td>
                {new Date(
                  appointment.appointment_date
                ).toLocaleString()}
              </td>

              <td>
                <button
                  onClick={() => handleDelete(appointment.id)}
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