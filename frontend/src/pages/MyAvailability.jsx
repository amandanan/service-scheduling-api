import { useEffect, useState } from "react";
import { toast } from "react-toastify";

import {
  getMyWorkingHours,
  updateMyWorkingHours,
  getMyBlocks,
  createMyBlock,
  deleteMyBlock,
} from "../services/api";

import Navbar from "../components/Navbar";

import { FaClock, FaSave, FaBan, FaTrash, FaPlus } from "react-icons/fa";

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


export default function MyAvailability() {

  const [days, setDays] = useState([]);
  const [blocks, setBlocks] = useState([]);

  const [blockDate, setBlockDate] = useState("");
  const [blockAllDay, setBlockAllDay] = useState(true);
  const [blockStart, setBlockStart] = useState("12:00");
  const [blockEnd, setBlockEnd] = useState("13:00");
  const [blockReason, setBlockReason] = useState("");


  async function loadAll() {
    try {
      const [hours, myBlocks] = await Promise.all([getMyWorkingHours(), getMyBlocks()]);
      setDays([...hours].sort((a, b) => a.weekday - b.weekday));
      setBlocks(myBlocks);
    } catch (error) {
      console.error(error);
      toast.error("Erro ao carregar disponibilidade");
    }
  }


  useEffect(() => {
    loadAll();
  }, []);


  function handleChange(weekday, field, value) {
    setDays((current) =>
      current.map((day) =>
        day.weekday === weekday ? { ...day, [field]: value } : day
      )
    );
  }


  async function handleSaveHours(e) {
    e.preventDefault();
    try {
      const payload = days.map((day) => ({
        weekday: day.weekday,
        start_time: day.start_time,
        end_time: day.end_time,
        is_closed: day.is_closed,
      }));
      const updated = await updateMyWorkingHours(payload);
      setDays([...updated].sort((a, b) => a.weekday - b.weekday));
      toast.success("Horários atualizados");
    } catch (error) {
      console.error(error);
      toast.error("Erro ao salvar horários");
    }
  }


  async function handleAddBlock(e) {
    e.preventDefault();

    if (!blockDate) {
      toast.error("Informe a data do bloqueio");
      return;
    }
    const start_at = blockAllDay ? `${blockDate}T00:00:00` : `${blockDate}T${blockStart}:00`;
    const end_at = blockAllDay ? `${blockDate}T23:59:59` : `${blockDate}T${blockEnd}:00`;
    if (!blockAllDay && blockEnd <= blockStart) {
      toast.error("O fim deve ser depois do início");
      return;
    }

    try {
      await createMyBlock({ start_at, end_at, reason: blockReason.trim() || null });
      toast.success("Bloqueio adicionado");
      setBlockReason("");
      loadAll();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao adicionar bloqueio");
    }
  }


  async function handleDeleteBlock(id) {
    try {
      await deleteMyBlock(id);
      toast.success("Bloqueio removido");
      loadAll();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao remover bloqueio");
    }
  }


  function formatBlock(block) {
    const start = new Date(block.start_at);
    const end = new Date(block.end_at);
    const dateStr = start.toLocaleDateString("pt-BR");
    const isAllDay = start.getHours() === 0 && start.getMinutes() === 0 && end.getHours() === 23;
    if (isAllDay) return `${dateStr} · dia inteiro`;
    const fmt = (d) => d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
    return `${dateStr} · ${fmt(start)} às ${fmt(end)}`;
  }


  return (
    <div className="services-page">

      <Navbar />

      <div className="services-container">

        <div className="services-card">

          <h1 className="services-title">
            <FaClock />
            Meus Horários
          </h1>

          <form onSubmit={handleSaveHours}>
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
                    <td>{WEEKDAY_LABELS[day.weekday]}</td>
                    <td>
                      <input
                        type="time"
                        value={day.start_time?.slice(0, 5) || ""}
                        disabled={day.is_closed}
                        onChange={(e) => handleChange(day.weekday, "start_time", e.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        type="time"
                        value={day.end_time?.slice(0, 5) || ""}
                        disabled={day.is_closed}
                        onChange={(e) => handleChange(day.weekday, "end_time", e.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        type="checkbox"
                        checked={day.is_closed}
                        onChange={(e) => handleChange(day.weekday, "is_closed", e.target.checked)}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <button type="submit" className="primary-btn" style={{ marginTop: "20px" }}>
              <FaSave />
              Salvar
            </button>
          </form>


          <h1 className="services-title" style={{ marginTop: "45px" }}>
            <FaBan />
            Folgas e Bloqueios
          </h1>

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
                <input type="time" value={blockStart} onChange={(e) => setBlockStart(e.target.value)} />
                <input type="time" value={blockEnd} onChange={(e) => setBlockEnd(e.target.value)} />
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
                      <button className="delete-btn" onClick={() => handleDeleteBlock(block.id)}>
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
