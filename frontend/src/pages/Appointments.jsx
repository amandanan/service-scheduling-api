import { useEffect, useState } from "react";

import FullCalendar from "@fullcalendar/react";

import dayGridPlugin from "@fullcalendar/daygrid";

import timeGridPlugin from "@fullcalendar/timegrid";

import interactionPlugin from "@fullcalendar/interaction";

import api from "../services/api";

import Navbar from "../components/Navbar";

import "../styles/appointments.css";

import { toast } from "react-toastify";

import {
  FaCalendarAlt,
  FaPlus,
} from "react-icons/fa";


export default function Appointments() {

  const [appointments, setAppointments] =
    useState([]);

  const [clients, setClients] =
    useState([]);

  const [services, setServices] =
    useState([]);

  const [clientId, setClientId] =
    useState("");

  const [serviceId, setServiceId] =
    useState("");

  const [scheduledAt, setScheduledAt] =
    useState("");


  async function loadData() {

    try {

      const [
        appointmentsRes,
        clientsRes,
        servicesRes,
      ] = await Promise.all([

        api.get("/appointments/"),

        api.get("/clients/"),

        api.get("/services/"),
      ]);


      setClients(clientsRes.data);

      setServices(servicesRes.data);


      const formatted =
        appointmentsRes.data.map(
          (item) => {

            const client =
              clientsRes.data.find(
                (c) =>
                  c.id === item.client_id
              );

            const service =
              servicesRes.data.find(
                (s) =>
                  s.id === item.service_id
              );

            return {

              id: item.id,

              title:
                `${client?.full_name || "Cliente"} • ${service?.name || "Serviço"}`,

              start:
                item.scheduled_at,
            };
          }
        );

      setAppointments(formatted);

    } catch (error) {

      console.error(error);

      toast.error(
        "Erro ao carregar agenda"
      );
    }
  }


  useEffect(() => {
    loadData();
  }, []);


  async function handleSubmit(e) {

    e.preventDefault();

    const appointmentData = {

      client_id:
        Number(clientId),

      service_id:
        Number(serviceId),

      scheduled_at:
        scheduledAt,
    };

    try {

      await api.post(
        "/appointments/",
        appointmentData
      );

      toast.success(
        "Agendamento criado"
      );

      setClientId("");

      setServiceId("");

      setScheduledAt("");

      loadData();

    } catch (error) {

      console.error(error);

      toast.error(
        "Erro ao criar agendamento"
      );
    }
  }


  function handleDateClick(info) {

    const formatted =
      info.dateStr.slice(0, 16);

    setScheduledAt(formatted);
  }


  return (

    <div className="appointments-page">

      <Navbar />

      <div className="appointments-container">

        <div className="appointments-card">

          <h1 className="appointments-title">

            <FaCalendarAlt />

            Agenda

          </h1>


          <form
            onSubmit={handleSubmit}
            className="appointments-form"
          >

            <select
              value={clientId}
              onChange={(e) =>
                setClientId(
                  e.target.value
                )
              }
              required
            >

              <option value="">
                Selecione cliente
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
                setServiceId(
                  e.target.value
                )
              }
              required
            >

              <option value="">
                Selecione serviço
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
              value={scheduledAt}
              onChange={(e) =>
                setScheduledAt(
                  e.target.value
                )
              }
              required
            />


            <button
              type="submit"
              className="primary-btn"
            >

              <FaPlus />

              Agendar

            </button>

          </form>


          <div className="calendar-wrapper">

            <FullCalendar

              plugins={[
                dayGridPlugin,
                timeGridPlugin,
                interactionPlugin,
              ]}

              initialView="timeGridWeek"

              locale="pt-br"

              selectable={true}

              dateClick={
                handleDateClick
              }

              headerToolbar={{

                left:
                  "prev,next today",

                center: "title",

                right:
                  "dayGridMonth,timeGridWeek,timeGridDay",
              }}

              buttonText={{
                today: "Hoje",
                month: "Mês",
                week: "Semana",
                day: "Dia",
              }}

              slotMinTime="08:00:00"

              slotMaxTime="20:00:00"

              allDaySlot={false}

              height="auto"

              events={appointments}
            />

          </div>

        </div>

      </div>

    </div>
  );
}