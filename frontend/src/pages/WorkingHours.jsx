import { useEffect, useState } from "react";

import {
  getWorkingHours,
  updateWorkingHours,
  getProfessionals,
  getMe,
  getTimeBlocks,
  createTimeBlock,
  deleteTimeBlock,
} from "../services/api";

import Navbar from "../components/Navbar";

import { toast } from "react-toastify";

import { FaClock, FaSave, FaLink, FaCopy, FaBan, FaTrash, FaPlus } from "react-icons/fa";

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

  const [blocks, setBlocks] = useState([]);

  const [blockDate, setBlockDate] = useState("");
  const [blockAllDay, setBlockAllDay] = useState(true);
  const [blockStart, setBlockStart] = useState("12:00");
  const [blockEnd, setBlockEnd] = useState("13:00");
  const [blockReason, setBlockReason] = useState("");


  async function loadBlocks(professionalId) {

    if (!professionalId) return;

    try {

      const data = await getTimeBlocks(professionalId);

      setBlocks(data);

    } catch (error) {

      console.error(error);

      toast.error("Erro ao carregar bloqueios");
    }
  }


  async function handleAddBlock(e) {

    e.preventDefault();

    if (!blockDate) {
      toast.error("Informe a data do bloqueio");
      return;
    }

    const start_at = blockAllDay
      ? `${blockDate}T00:00:00`
      : `${blockDate}T${blockStart}:00`;

    const end_at = blockAllDay
      ? `${blockDate}T23:59:59`
      : `${blockDate}T${blockEnd}:00`;

    if (!blockAllDay && blockEnd <= blockStart) {
      toast.error("O fim deve ser depois do início");
      return;
    }

    try {

      await createTimeBlock({
        professional_id: Number(selectedProfessionalId),
        start_at,
        end_at,
        reason: blockReason.trim() || null,
      });

      toast.success("Bloqueio adicionado");

      setBlockReason("");

      loadBlocks(selectedProfessionalId);

    } catch (error) {

      console.error(error);

      toast.error("Erro ao adicionar bloqueio");
    }
  }


  async function handleDeleteBlock(id) {

    try {

      await deleteTimeBlock(id);

      toast.success("Bloqueio removido");

      loadBlocks(selectedProfessionalId);

    } catch (error) {

      console.error(error);

      toast.error("Erro ao remover bloqueio");
    }
  }


  function formatBlock(block) {

    const start = new Date(block.start_at);
    const end = new Date(block.end_at);

    const dateStr = start.toLocaleDateString("pt-BR");

    const isAllDay =
      start.getHours() === 0 && start.getMinutes() === 0 &&
      end.getHours() === 23;

    if (isAllDay) {
      return `${dateStr} · dia inteiro`;
    }

    const fmt = (d) =>
      d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });

    return `${dateStr} · ${fmt(start)} às ${fmt(end)}`;
  }


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
        loadBlocks(firstId);
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
    loadBlocks(id);
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


          <h1 className="services-title" style={{ marginTop: "45px" }}>
            <FaBan />
            Folgas e Bloqueios
          </h1>

          <p className="settings-hint" style={{ marginBottom: "18px" }}>
            Bloqueie um dia inteiro (folga, férias) ou um intervalo específico.
            Esses períodos não aparecem como horários disponíveis no agendamento.
          </p>

          <form onSubmit={handleAddBlock} className="services-form">

            <input
              type="date"
              value={blockDate}
              onChange={(e) => setBlockDate(e.target.value)}
              required
            />

            <label style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <input
                type="checkbox"
                checked={blockAllDay}
                onChange={(e) => setBlockAllDay(e.target.checked)}
              />
              Dia inteiro
            </label>

            {!blockAllDay && (
              <>
                <input
                  type="time"
                  value={blockStart}
                  onChange={(e) => setBlockStart(e.target.value)}
                />
                <input
                  type="time"
                  value={blockEnd}
                  onChange={(e) => setBlockEnd(e.target.value)}
                />
              </>
            )}

            <input
              type="text"
              placeholder="Motivo (opcional)"
              value={blockReason}
              onChange={(e) => setBlockReason(e.target.value)}
            />

            <button type="submit" className="primary-btn">
              <FaPlus />
              Adicionar
            </button>

          </form>

          <table className="services-table">

            <thead>
              <tr>
                <th>Período</th>
                <th>Motivo</th>
                <th>Ações</th>
              </tr>
            </thead>

            <tbody>

              {blocks.length > 0 ? (

                blocks.map((block) => (

                  <tr key={block.id}>
                    <td>{formatBlock(block)}</td>
                    <td>{block.reason || "—"}</td>
                    <td>
                      <button
                        className="delete-btn"
                        onClick={() => handleDeleteBlock(block.id)}
                      >
                        <FaTrash />
                        Remover
                      </button>
                    </td>
                  </tr>
                ))

              ) : (

                <tr>
                  <td colSpan="3" style={{ textAlign: "center", padding: "20px" }}>
                    Nenhum bloqueio cadastrado
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
