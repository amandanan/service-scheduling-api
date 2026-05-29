import { useEffect, useState } from "react";

import {
  Calendar,
  momentLocalizer,
} from "react-big-calendar";

import moment from "moment";

import "react-big-calendar/lib/css/react-big-calendar.css";

import api from "../services/api";

import Navbar from "../components/Navbar";

import "../styles/appointments.css";

import { toast } from "react-toastify";

import {
  FaCalendarAlt,
  FaPlus,
} from "react-icons/fa";

const localizer = momentLocalizer(moment);

export default function Appointments() {

  const [appointments, setAppointments] =
    useState([]);

  const [clientId, setClientId] =
    useState("");

  const [serviceId, setServiceId] =
    useState("");

  const [date, setDate] =
    useState("");


  async function loadAppointments() {

    try {

      const response = await api.get(
        "/appointments/"
      );

      const formatted =
        response.data.map((item) => ({

          id: item.id,

          title:
            `Cliente ${item.client_id} • Serviço ${item.service_id}`,

          start: new Date(
            item.scheduled_at
          ),

          end: moment(
            item.scheduled_at
          )
            .add(1, "hour")
            .toDate(),
        }));

      setAppointments(formatted);

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

      scheduled_at: date,
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
      setDate("");

      loadAppointments();

    } catch (error) {

      console.error(error);

      console.log(
        JSON.stringify(
          error.response?.data,
          null,
          2
        )
      );

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

              <FaPlus />
              Agendar

            </button>

          </form>


          <div className="calendar-wrapper">

            <Calendar
              localizer={localizer}
              events={appointments}
              startAccessor="start"
              endAccessor="end"
              style={{ height: 650 }}
              messages={{
                next: "Próximo",
                previous: "Anterior",
                today: "Hoje",
                month: "Mês",
                week: "Semana",
                day: "Dia",
                agenda: "Agenda",
              }}
            />

          </div>

        </div>

      </div>

    </div>
  );
}