import { useEffect, useState } from "react";

import {
  getWorkingHours,
  updateWorkingHours,
  getProfessionals,
  getMe,
} from "../services/api";

import Navbar from "../components/Navbar";

import { toast } from "react-toastify";

import { FaClock, FaSave, FaLink, FaCopy } from "react-icons/fa";

import "../styles/services.css";

const WEEKDAY_LABELS = [
  "Segunda-feira",
  "Terça-feira",
  "Quarta-feira",
  "Quinta-feira",
  "Sexta-feira",
  "Sábado",
  "Domingo",
];

export default function WorkingHours() {

  const [days, setDays] = useState([]);

  const [bookingLink, setBookingLink] = useState("");

  const [professionals, setProfessionals] = useState([]);

  const [selectedProfessionalId, setSelectedProfessionalId] = useState("");


  async function loadWorkingHours(professionalId) {

    if (!professionalId) return;

    try {

      const response = await getWorkingHours(professionalId);

      const sorted = [...response].sort(
        (a, b) => a.weekday - b.weekday
      );

      setDays(sorted);

    } catch (error) {

      console.error(error);

      toast.error(
        "Erro ao carregar horário de funcionamento"
      );
    }
  }


  async function loadProfessionals() {

    try {

      const data = await getProfessionals();

      setProfessionals(data);

      if (data.length > 0) {
        const firstId = data[0].id;
        setSelectedProfessionalId(firstId);
        loadWorkingHours(firstId);
      }

    } catch (error) {

      console.error(error);

      toast.error("Erro ao carregar profissionais");
    }
  }


  async function loadBookingLink() {

    try {

      const me = await getMe();

      setBookingLink(
        `${window.location.origin}/agendar/${me.booking_slug}`
      );

    } catch (error) {

      console.error(error);
    }
  }


  useEffect(() => {
    loadProfessionals();
    loadBookingLink();
  }, []);


  function handleProfessionalChange(e) {
    const id = Number(e.target.value);
    setSelectedProfessionalId(id);
    loadWorkingHours(id);
  }


  async function handleCopyLink() {

    try {

      await navigator.clipboard.writeText(bookingLink);

      toast.success("Link copiado!");

    } catch (error) {

      console.error(error);

      toast.error("Não foi possível copiar o link");
    }
  }


  function handleChange(weekday, field, value) {

    setDays((current) =>
      current.map((day) =>
        day.weekday === weekday
          ? { ...day, [field]: value }
          : day
      )
    );
  }


  async function handleSubmit(e) {

    e.preventDefault();

    try {

      const payload = days.map((day) => ({
        weekday: day.weekday,
        start_time: day.start_time,
        end_time: day.end_time,
        is_closed: day.is_closed,
      }));

      const response = await updateWorkingHours(selectedProfessionalId, payload);

      const sorted = [...response].sort(
        (a, b) => a.weekday - b.weekday
      );

      setDays(sorted);

      toast.success("Horário de funcionamento atualizado");

    } catch (error) {

      console.error(error);

      toast.error(
        "Erro ao salvar horário de funcionamento"
      );
    }
  }


  return (

    <div className="services-page">

      <Navbar />

      <div className="services-container">

        <div className="services-card">

          <h1 className="services-title">

            <FaClock />

            Horário de Funcionamento

          </h1>

          {bookingLink && (

            <div className="services-form" style={{ marginBottom: "30px" }}>

              <input
                type="text"
                readOnly
                value={bookingLink}
                onFocus={(e) => e.target.select()}
                style={{ flex: 1, minWidth: "260px" }}
              />

              <button
                type="button"
                className="primary-btn"
                onClick={handleCopyLink}
              >
                <FaCopy />
                Copiar link
              </button>

              <a
                href={bookingLink}
                target="_blank"
                rel="noreferrer"
                className="secondary-btn"
                style={{ display: "flex", alignItems: "center", gap: "8px", textDecoration: "none" }}
              >
                <FaLink />
                Abrir página de agendamento
              </a>

            </div>

          )}


          <div className="services-form" style={{ marginBottom: "20px" }}>

            <label style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              Profissional:
              <select
                value={selectedProfessionalId}
                onChange={handleProfessionalChange}
                style={{ padding: "12px", borderRadius: "10px", border: "1px solid #ccc" }}
              >
                {professionals.map((professional) => (
                  <option key={professional.id} value={professional.id}>
                    {professional.name}
                  </option>
                ))}
              </select>
            </label>

          </div>


          <form onSubmit={handleSubmit}>

            <table className="services-table">

              <thead>

                <tr>

                  <th>Dia</th>

                  <th>Abre</th>

                  <th>Fecha</th>

                  <th>Fechado</th>

                </tr>

              </thead>


              <tbody>

                {days.map((day) => (

                  <tr key={day.weekday}>

                    <td>
                      {WEEKDAY_LABELS[day.weekday]}
                    </td>

                    <td>

                      <input
                        type="time"
                        value={day.start_time?.slice(0, 5) || ""}
                        disabled={day.is_closed}
                        onChange={(e) =>
                          handleChange(
                            day.weekday,
                            "start_time",
                            e.target.value
                          )
                        }
                      />

                    </td>

                    <td>

                      <input
                        type="time"
                        value={day.end_time?.slice(0, 5) || ""}
                        disabled={day.is_closed}
                        onChange={(e) =>
                          handleChange(
                            day.weekday,
                            "end_time",
                            e.target.value
                          )
                        }
                      />

                    </td>

                    <td>

                      <input
                        type="checkbox"
                        checked={day.is_closed}
                        onChange={(e) =>
                          handleChange(
                            day.weekday,
                            "is_closed",
                            e.target.checked
                          )
                        }
                      />

                    </td>

                  </tr>

                ))}

              </tbody>

            </table>


            <button
              type="submit"
              className="primary-btn"
              style={{ marginTop: "20px" }}
            >

              <FaSave />

              Salvar

            </button>

          </form>

        </div>

      </div>

    </div>
  );
}
