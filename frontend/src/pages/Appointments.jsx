import { useEffect, useState } from "react";

import api from "../services/api";
import Navbar from "../components/Navbar";

import { toast } from "react-toastify";

import {
  FaCalendarAlt,
  FaEdit,
  FaTrash,
  FaPlus,
  FaClock,
} from "react-icons/fa";

import "../styles/appointments.css";

export default function Appointments() {

  const [appointments, setAppointments] = useState([]);

  const [clients, setClients] = useState([]);
  const [services, setServices] = useState([]);

  const [clientId, setClientId] = useState("");
  const [serviceId, setServiceId] = useState("");
  const [date, setDate] = useState("");

  const [editingId, setEditingId] = useState(null);


  async function loadData() {

    try {

      const [
        appointmentsResponse,
        clientsResponse,
        servicesResponse,
      ] = await Promise.all([
        api.get("/appointments"),
        api.get("/clients"),
        api.get("/services"),
      ]);

      setAppointments(
        appointmentsResponse.data
      );

      setClients(
        clientsResponse.data
      );

      setServices(
        servicesResponse.data
      );

    } catch (error) {

      console.error(error);

      toast.error(
        "Erro ao carregar dados"
      );
    }
  }


  useEffect(() => {
    loadData();
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

      loadData();

    } catch (error) {

      console.error(error);

      toast.error(
        "Erro ao salvar agendamento"
      );
    }
  }


  function handleEdit(appointment) {

    setEditingId(appointment.id);

    setClientId(
      appointment.client_id
    );

    setServiceId(
      appointment.service_id
    );

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
        "Agendamento excluído"
      );

      loadData();

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

    <div className="appointments-page">

      <Navbar />

      <div className="appointments-container">

        <div className="appointments-card">

          <h1 className="appointments-title">
            <FaCalendarAlt />
            Agendamentos
          </h1>


          <form
            onSubmit={handleSubmit}
            className="appointments-form"
          >

            <select
              value={clientId}
              onChange={(e) =>
                setClientId(e.target.value)
              }
              required
            >

              <option value="">
                Selecione o cliente
              </option>

              {clients.map((client) => (

                <option
                  key={client.id}
                  value={client.id}
                >
                  {client.full_name}
                </option>

              ))}

            </select>


            <select
              value={serviceId}
              onChange={(e) =>
                setServiceId(e.target.value)
              }
              required
            >

              <option value="">
                Selecione o serviço
              </option>

              {services.map((service) => (

                <option
                  key={service.id}
                  value={service.id}
                >
                  {service.name}
                </option>

              ))}

            </select>


            <input
              type="datetime-local"
              value={date}
              onChange={(e) =>
                setDate(e.target.value)
              }
              required
            />


            <button
              type="submit"
              className="primary-btn"
            >

              {editingId
                ? <FaEdit />
                : <FaPlus />
              }

              {editingId
                ? "Atualizar"
                : "Cadastrar"}

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


          <table className="appointments-table">

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

              {appointments.map((appointment) => {

                const client = clients.find(
                  (c) =>
                    c.id === appointment.client_id
                );

                const service = services.find(
                  (s) =>
                    s.id === appointment.service_id
                );

                return (

                  <tr key={appointment.id}>

                    <td>
                      {appointment.id}
                    </td>

                    <td>
                      {client?.full_name}
                    </td>

                    <td>
                      {service?.name}
                    </td>

                    <td>

                      <div className="info-cell">

                        <FaClock />

                        {appointment.date}

                      </div>

                    </td>

                    <td>

                      <div className="actions">

                        <button
                          className="edit-btn"
                          onClick={() =>
                            handleEdit(
                              appointment
                            )
                          }
                        >

                          <FaEdit />
                          Editar

                        </button>


                        <button
                          className="delete-btn"
                          onClick={() =>
                            handleDelete(
                              appointment.id
                            )
                          }
                        >

                          <FaTrash />
                          Excluir

                        </button>

                      </div>

                    </td>

                  </tr>
                );
              })}

            </tbody>

          </table>

        </div>
      </div>
    </div>
  );
}