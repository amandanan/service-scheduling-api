import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";

import {
  getManagedAppointment,
  getManageAvailableSlots,
  cancelManagedAppointment,
  rescheduleManagedAppointment,
  submitReview,
} from "../services/api";

import StarRating from "../components/StarRating";

import "../styles/public-booking.css";
import "../styles/reviews.css";

export default function ManageAppointment() {

  const { token } = useParams();

  const [appointment, setAppointment] = useState(null);
  const [notFound, setNotFound] = useState(false);

  const [rescheduling, setRescheduling] = useState(false);
  const [selectedDate, setSelectedDate] = useState("");
  const [availableSlots, setAvailableSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState("");

  const [loadingAction, setLoadingAction] = useState(false);

  const [reviewRating, setReviewRating] = useState(0);
  const [reviewComment, setReviewComment] = useState("");
  const [submittingReview, setSubmittingReview] = useState(false);


  useEffect(() => {

    async function loadAppointment() {

      try {

        const data = await getManagedAppointment(token);
        setAppointment(data);

      } catch (error) {

        console.error(error);
        setNotFound(true);
      }
    }

    loadAppointment();
  }, [token]);


  async function loadAvailableSlots(date) {

    if (!date) return;

    try {

      const slots = await getManageAvailableSlots(token, date);
      setAvailableSlots(slots);

    } catch (error) {

      console.error(error);

      toast.error("Erro ao carregar horários disponíveis");
    }
  }


  function handleSelectDate(date) {

    setSelectedDate(date);
    setSelectedSlot("");
    setAvailableSlots([]);

    loadAvailableSlots(date);
  }


  function startReschedule() {

    setRescheduling(true);
    setSelectedDate("");
    setSelectedSlot("");
    setAvailableSlots([]);
  }


  function cancelReschedule() {

    setRescheduling(false);
    setSelectedDate("");
    setSelectedSlot("");
    setAvailableSlots([]);
  }


  async function handleCancel() {

    if (!window.confirm("Tem certeza que deseja cancelar este agendamento?")) {
      return;
    }

    setLoadingAction(true);

    try {

      const data = await cancelManagedAppointment(token);

      setAppointment(data);

      toast.success("Agendamento cancelado");

    } catch (error) {

      console.error(error);

      toast.error("Erro ao cancelar agendamento");

    } finally {
      setLoadingAction(false);
    }
  }


  async function handleReschedule() {

    if (!selectedDate || !selectedSlot) {
      toast.error("Selecione um horário");
      return;
    }

    setLoadingAction(true);

    try {

      const data = await rescheduleManagedAppointment(
        token,
        `${selectedDate}T${selectedSlot}:00`
      );

      setAppointment(data);

      cancelReschedule();

      toast.success("Agendamento remarcado");

    } catch (error) {

      console.error(error);

      if (error.response?.status === 409) {
        toast.error("Esse horário não está disponível. Escolha outro.");
        loadAvailableSlots(selectedDate);
        setSelectedSlot("");
      } else {
        toast.error("Erro ao remarcar agendamento");
      }

    } finally {
      setLoadingAction(false);
    }
  }


  async function handleSubmitReview() {

    if (!reviewRating) {
      toast.error("Selecione uma nota de 1 a 5");
      return;
    }

    setSubmittingReview(true);

    try {

      const data = await submitReview(token, reviewRating, reviewComment.trim() || null);

      setAppointment(data);

      toast.success("Avaliação enviada. Obrigado!");

    } catch (error) {

      console.error(error);

      toast.error("Erro ao enviar avaliação");

    } finally {
      setSubmittingReview(false);
    }
  }


  if (notFound) {
    return (
      <div className="public-booking-container">
        <div className="public-booking-card">
          <div className="public-booking-success">
            <h2>Agendamento não encontrado</h2>
            <p>Verifique o link e tente novamente.</p>
          </div>
        </div>
      </div>
    );
  }

  if (!appointment) {
    return (
      <div className="public-booking-container">
        <div className="public-booking-card">
          <p className="public-booking-empty">Carregando...</p>
        </div>
      </div>
    );
  }

  const scheduledDate = new Date(appointment.scheduled_at);
  const dateLabel = scheduledDate.toLocaleDateString("pt-BR");
  const timeLabel = scheduledDate.toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });

  const isCancelled = appointment.status === "cancelled";

  return (
    <div className="public-booking-container">
      <div className="public-booking-card">

        <h1 className="public-booking-title">{appointment.business_name}</h1>
        <p className="public-booking-subtitle">Gerenciar agendamento</p>

        <div className="manage-appointment-details">
          <p><strong>Serviço:</strong> {appointment.service_name}</p>
          <p><strong>Profissional:</strong> {appointment.professional_name}</p>
          <p><strong>Data:</strong> {dateLabel} às {timeLabel}</p>
          <p>
            <span className={`manage-appointment-status ${isCancelled ? "cancelled" : "scheduled"}`}>
              {isCancelled ? "Cancelado" : "Agendado"}
            </span>
          </p>
        </div>

        {isCancelled && (
          <div className="public-booking-success">
            <p>Este agendamento foi cancelado.</p>
          </div>
        )}

        {!isCancelled && !rescheduling && (
          <div className="public-booking-form">
            <button
              type="button"
              className="public-booking-btn"
              onClick={startReschedule}
            >
              Remarcar
            </button>

            <button
              type="button"
              className="public-booking-btn danger"
              onClick={handleCancel}
              disabled={loadingAction}
            >
              {loadingAction ? "Cancelando..." : "Cancelar agendamento"}
            </button>
          </div>
        )}

        {!isCancelled && rescheduling && (
          <>
            <div className="public-booking-step">
              <label>Nova data</label>

              <input
                type="date"
                value={selectedDate}
                onChange={(e) => handleSelectDate(e.target.value)}
              />
            </div>

            {selectedDate && (
              <div className="public-booking-step">
                <label>Novo horário</label>

                <div className="slots-grid">
                  {availableSlots.map((slot) => (
                    <button
                      key={slot}
                      type="button"
                      className={
                        selectedSlot === slot
                          ? "slot-btn active"
                          : "slot-btn"
                      }
                      onClick={() => setSelectedSlot(slot)}
                    >
                      {slot}
                    </button>
                  ))}

                  {availableSlots.length === 0 && (
                    <p className="public-booking-empty">
                      Nenhum horário disponível nesta data.
                    </p>
                  )}
                </div>
              </div>
            )}

            <div className="public-booking-form">
              <button
                type="button"
                className="public-booking-btn"
                onClick={handleReschedule}
                disabled={loadingAction || !selectedSlot}
              >
                {loadingAction ? "Salvando..." : "Confirmar nova data"}
              </button>

              <button
                type="button"
                className="public-booking-btn secondary"
                onClick={cancelReschedule}
              >
                Voltar
              </button>
            </div>
          </>
        )}

        {appointment.review && (
          <div className="public-booking-step review-form">
            <label>Sua avaliação</label>

            <StarRating value={appointment.review.rating} readOnly />

            {appointment.review.comment && (
              <p className="review-card-comment" style={{ marginTop: "10px" }}>
                {appointment.review.comment}
              </p>
            )}
          </div>
        )}

        {appointment.can_review && (
          <div className="public-booking-step review-form">
            <label>Avalie o atendimento</label>

            <StarRating value={reviewRating} onChange={setReviewRating} />

            <textarea
              placeholder="Conte como foi sua experiência (opcional)"
              value={reviewComment}
              onChange={(e) => setReviewComment(e.target.value)}
              style={{ marginTop: "14px" }}
            />

            <button
              type="button"
              className="public-booking-btn"
              onClick={handleSubmitReview}
              disabled={submittingReview}
            >
              {submittingReview ? "Enviando..." : "Enviar avaliação"}
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
