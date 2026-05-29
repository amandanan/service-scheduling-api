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

  const [clientId, setClientId] =
    useState("");

  const [serviceId, setServiceId] =
    useState("");

  const [scheduledAt, setScheduledAt] =
    useState("");


  async function loadAppointments() {

    try {

      const response =
        await api.get("/appointments/");

      const formatted =
        response.data.map((item) => ({

          id: item.id,

          title:
            `${item.client_id} • ${item.service_id}`,

          start: item.scheduled_at,
        }));

      setAppointments(formatted);

    } catch (error) {

      console.error(error);

      toast.error(
        "Erro ao carregar agenda"
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

      scheduled_at: scheduledAt,
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

      loadAppointments();

    } catch (error) {

      console.error(error);

      toast.error(
        "Erro ao criar agendamento"
      );
    }
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

            <input
              type="number"
              placeholder="ID Cliente"
              value={clientId}
              onChange={(e) =>
                setClientId(e.target.value)
              }
              required
            />

            <input
              type="number"
              placeholder="ID Serviço"
              value={serviceId}
              onChange={(e) =>
                setServiceId(e.target.value)
              }
              required
            />

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