import { useEffect, useState } from "react";

import FullCalendar from "@fullcalendar/react";

import dayGridPlugin from "@fullcalendar/daygrid";

import timeGridPlugin from "@fullcalendar/timegrid";

import interactionPlugin from "@fullcalendar/interaction";

import Select from "react-select";

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

  const [availableSlots, setAvailableSlots] =
    useState([]);

  const [showSlots, setShowSlots] =
    useState(false);

  const [selectedDate, setSelectedDate] =
    useState("");

  const [clientId, setClientId] =
    useState("");

  const [serviceId, setServiceId] =
    useState("");

  const [scheduledAt, setScheduledAt] =
    useState("");

  const [selectedClient, setSelectedClient] =
    useState(null);

  const [selectedService, setSelectedService] =
    useState(null);

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

            const startDate =
              new Date(item.scheduled_at);

            const duration =
              service?.duration_minutes || 60;

            const endDate =
              new Date(
                startDate.getTime() +
                duration * 60 * 1000
              );

            return {

              id: item.id,

              title:
                `${client?.full_name || "Cliente"} • ${service?.name || "Serviço"}`,

              start: startDate,

              end: endDate,
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

  async function loadAvailableSlots(
    date,
    selectedServiceId
  ) {

    if (!date || !selectedServiceId)
      return;

    try {

      const response = await api.get(
        "/appointments/available-slots",
        {
          params: {
            date,
            service_id:
              selectedServiceId,
          },
        }
      );

      setAvailableSlots(
        response.data
      );

    } catch (error) {

      console.error(error);

      toast.error(
        "Erro ao carregar horários"
      );
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function handleSubmit(e) {

    e.preventDefault();

    if (!clientId) {

      toast.error(
        "Selecione um paciente"
      );

      return;
    }

    if (!serviceId) {

      toast.error(
        "Selecione um serviço"
      );

      return;
    }

    if (!scheduledAt) {

      toast.error(
        "Selecione um horário"
      );

      return;
    }

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

      setSelectedDate("");

      setSelectedClient(null);

      setSelectedService(null);

      setAvailableSlots([]);

      setShowSlots(false);

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

  async function handleEventClick(info) {

    const confirmDelete = window.confirm(
      "Deseja excluir este agendamento?"
    );

    if (!confirmDelete) return;

    try {

      await api.delete(
        `/appointments/${info.event.id}`
      );

      toast.success(
        "Agendamento removido"
      );

      loadData();

    } catch (error) {

      console.error(error);

      toast.error(
        "Erro ao excluir agendamento"
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

            {/* CLIENTE */}

            <div className="client-select-wrapper">

              <Select

                options={clients.map((client) => ({

                  value: client.id,

                  label:
                    `${client.full_name} • CPF ${client.cpf}`,

                  search:
                    `${client.full_name} ${client.cpf}`,

                  client,
                }))}

                placeholder="Pesquisar paciente por nome ou CPF..."

                value={
                  clientId && selectedClient
                    ? {
                        value: clientId,
                        label:
                          `${selectedClient.full_name} • CPF ${selectedClient.cpf}`,
                      }
                    : null
                }

                filterOption={(option, inputValue) => {

                  const text =
                    option.data.search.toLowerCase();

                  return text.includes(
                    inputValue.toLowerCase()
                  );
                }}

                onChange={(selected) => {

                  setClientId(
                    selected.value
                  );

                  setSelectedClient(
                    selected.client
                  );
                }}

                className="react-select-container"

                classNamePrefix="react-select"

              />

            </div>

            {/* SERVIÇO */}

            <div className="service-select-wrapper">

              <Select

                options={services.map((service) => ({

                  value: service.id,

                  label:
                    `${service.id} - ${service.name}`,

                  search:
                    `${service.id} ${service.name}`,

                  service,
                }))}

                placeholder="Pesquisar serviço por código ou nome..."

                value={
                  serviceId && selectedService
                    ? {
                        value: serviceId,
                        label:
                          `${selectedService.id} - ${selectedService.name}`,
                      }
                    : null
                }

                filterOption={(option, inputValue) => {

                  const text =
                    option.data.search.toLowerCase();

                  return text.includes(
                    inputValue.toLowerCase()
                  );
                }}

                onChange={(selected) => {

                  setServiceId(
                    selected.value
                  );

                  setSelectedService(
                    selected.service
                  );

                  if (selectedDate) {

                    loadAvailableSlots(
                      selectedDate,
                      selected.value
                    );
                  }
                }}

                className="react-select-container"

                classNamePrefix="react-select"

              />

            </div>

            {/* DATA */}

            <input
              type="date"
              value={selectedDate}
              onChange={(e) => {

                const date =
                  e.target.value;

                setSelectedDate(date);

                loadAvailableSlots(
                  date,
                  serviceId
                );
              }}
              required
            />

            {/* DROPDOWN HORÁRIOS */}

            <div className="slots-dropdown">

              <button
                type="button"
                className="slots-toggle-btn"
                onClick={() =>
                  setShowSlots(!showSlots)
                }
              >

                Ver horários disponíveis

              </button>

              {showSlots &&
                availableSlots.length > 0 && (

                <div className="slots-content">

                  <div className="slots-grid">

                    {availableSlots.map((slot) => (

                      <button
                        key={slot}
                        type="button"
                        className={
                          scheduledAt ===
                          `${selectedDate}T${slot}`
                            ? "slot-btn active"
                            : "slot-btn"
                        }
                        onClick={() =>
                          setScheduledAt(
                            `${selectedDate}T${slot}`
                          )
                        }
                      >

                        {slot}

                      </button>

                    ))}

                  </div>

                  {/* HORÁRIO MANUAL */}

                  <div className="manual-time-wrapper">

                    <label>
                      Ou escolha manualmente
                    </label>

                    <input
                      type="time"
                      onChange={(e) => {

                        if (!selectedDate)
                          return;

                        setScheduledAt(
                          `${selectedDate}T${e.target.value}`
                        );
                      }}
                    />

                  </div>

                </div>

              )}

            </div>

            {/* HORÁRIO ESCOLHIDO */}

            {scheduledAt && (

              <div className="selected-time-preview">

                Horário selecionado:
                {" "}

                <strong>
                  {scheduledAt}
                </strong>

              </div>

            )}

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

              eventClick={
                handleEventClick
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

              slotDuration="00:30:00"

              nowIndicator={true}

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