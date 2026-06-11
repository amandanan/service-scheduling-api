import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { toast } from "react-toastify";
import { IMaskInput } from "react-imask";

import {
  getPublicBusiness,
  getPublicServices,
  getPublicProfessionals,
  getPublicAvailableSlots,
  createPublicBooking,
} from "../services/api";

import "../styles/public-booking.css";

export default function PublicBooking() {

  const { slug } = useParams();

  const [business, setBusiness] = useState(null);
  const [notFound, setNotFound] = useState(false);

  const [services, setServices] = useState([]);
  const [selectedService, setSelectedService] = useState(null);

  const [professionals, setProfessionals] = useState([]);
  const [selectedProfessional, setSelectedProfessional] = useState(null);

  const [selectedDate, setSelectedDate] = useState("");
  const [availableSlots, setAvailableSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState("");

  const [fullName, setFullName] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [cpf, setCpf] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);


  useEffect(() => {

    async function loadBusiness() {

      try {

        const businessData = await getPublicBusiness(slug);
        const servicesData = await getPublicServices(slug);
        const professionalsData = await getPublicProfessionals(slug);

        setBusiness(businessData);
        setServices(servicesData);
        setProfessionals(professionalsData);

      } catch (error) {

        console.error(error);
        setNotFound(true);
      }
    }

    loadBusiness();
  }, [slug]);


  async function loadAvailableSlots(date, serviceId, professionalId) {

    if (!date || !serviceId || !professionalId) return;

    try {

      const slots = await getPublicAvailableSlots(slug, date, serviceId, professionalId);
      setAvailableSlots(slots);

    } catch (error) {

      console.error(error);

      toast.error("Erro ao carregar horários disponíveis");
    }
  }


  function handleSelectService(service) {

    setSelectedService(service);
    setSelectedSlot("");

    if (selectedDate && selectedProfessional) {
      loadAvailableSlots(selectedDate, service.id, selectedProfessional.id);
    }
  }


  function handleSelectProfessional(professional) {

    setSelectedProfessional(professional);
    setSelectedSlot("");

    if (selectedDate && selectedService) {
      loadAvailableSlots(selectedDate, selectedService.id, professional.id);
    }
  }


  function handleSelectDate(date) {

    setSelectedDate(date);
    setSelectedSlot("");
    setAvailableSlots([]);

    if (selectedService && selectedProfessional) {
      loadAvailableSlots(date, selectedService.id, selectedProfessional.id);
    }
  }


  async function handleSubmit(e) {

    e.preventDefault();

    if (!selectedService) {
      toast.error("Selecione um serviço");
      return;
    }

    if (!selectedProfessional) {
      toast.error("Selecione um profissional");
      return;
    }

    if (!selectedDate || !selectedSlot) {
      toast.error("Selecione um horário");
      return;
    }

    setSubmitting(true);

    try {

      await createPublicBooking(slug, {
        full_name: fullName,
        birth_date: birthDate,
        cpf,
        phone,
        email,
        service_id: selectedService.id,
        professional_id: selectedProfessional.id,
        scheduled_at: `${selectedDate}T${selectedSlot}:00`,
      });

      setSuccess(true);

    } catch (error) {

      console.error(error);

      if (error.response?.status === 409) {
        toast.error("Esse horário acabou de ficar indisponível. Escolha outro.");
        loadAvailableSlots(selectedDate, selectedService.id, selectedProfessional.id);
        setSelectedSlot("");
      } else if (error.response?.status === 422) {
        toast.error("CPF inválido");
      } else if (error.response?.status === 429) {
        toast.error("Muitas tentativas. Aguarde um momento e tente novamente.");
      } else {
        toast.error("Erro ao criar agendamento");
      }

    } finally {
      setSubmitting(false);
    }
  }


  if (notFound) {
    return (
      <div className="public-booking-container">
        <div className="public-booking-card">
          <div className="public-booking-success">
            <h2>Página não encontrada</h2>
            <p>Verifique o link e tente novamente.</p>
          </div>
        </div>
      </div>
    );
  }

  if (!business) {
    return (
      <div className="public-booking-container">
        <div className="public-booking-card">
          <p className="public-booking-empty">Carregando...</p>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="public-booking-container">
        <div className="public-booking-card">
          <div className="public-booking-success">
            <h2>Agendamento confirmado!</h2>
            <p>
              {selectedService?.name} em{" "}
              {selectedDate.split("-").reverse().join("/")} às {selectedSlot}
            </p>
            <p>Você receberá a confirmação em breve.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="public-booking-container">
      <div className="public-booking-card">

        <h1 className="public-booking-title">{business.full_name}</h1>
        <p className="public-booking-subtitle">Agende seu horário</p>

        <form className="public-booking-form" onSubmit={handleSubmit}>

          <div className="public-booking-step">
            <label>1. Escolha o serviço</label>

            <div className="service-options">
              {services.map((service) => (
                <div
                  key={service.id}
                  className={
                    selectedService?.id === service.id
                      ? "service-option active"
                      : "service-option"
                  }
                  onClick={() => handleSelectService(service)}
                >
                  <span>{service.name}</span>
                  <span className="service-option-price">
                    R$ {service.price.toFixed(2)}
                  </span>
                </div>
              ))}

              {services.length === 0 && (
                <p className="public-booking-empty">
                  Nenhum serviço disponível no momento.
                </p>
              )}
            </div>
          </div>

          <div className="public-booking-step">
            <label>2. Escolha o profissional</label>

            <div className="service-options">
              {professionals.map((professional) => (
                <div
                  key={professional.id}
                  className={
                    selectedProfessional?.id === professional.id
                      ? "service-option active"
                      : "service-option"
                  }
                  onClick={() => handleSelectProfessional(professional)}
                >
                  <span>{professional.name}</span>
                </div>
              ))}

              {professionals.length === 0 && (
                <p className="public-booking-empty">
                  Nenhum profissional disponível no momento.
                </p>
              )}
            </div>
          </div>

          <div className="public-booking-step">
            <label>3. Escolha a data</label>

            <input
              type="date"
              value={selectedDate}
              onChange={(e) => handleSelectDate(e.target.value)}
              required
            />
          </div>

          {selectedDate && selectedService && selectedProfessional && (
            <div className="public-booking-step">
              <label>4. Escolha o horário</label>

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

          {selectedSlot && (
            <div className="public-booking-step">
              <label>5. Seus dados</label>

              <div className="public-booking-form" style={{ gap: "12px" }}>

                <input
                  type="text"
                  placeholder="Nome completo"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                />

                <input
                  type="date"
                  placeholder="Data de nascimento"
                  value={birthDate}
                  onChange={(e) => setBirthDate(e.target.value)}
                  required
                />

                <IMaskInput
                  mask="000.000.000-00"
                  value={cpf}
                  onAccept={(value) => setCpf(value)}
                  placeholder="CPF"
                  className="masked-input"
                />

                <IMaskInput
                  mask="(00) 00000-0000"
                  value={phone}
                  onAccept={(value) => setPhone(value)}
                  placeholder="Telefone"
                  className="masked-input"
                />

                <input
                  type="email"
                  placeholder="E-mail"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />

              </div>
            </div>
          )}

          {selectedSlot && (
            <button
              type="submit"
              className="public-booking-btn"
              disabled={submitting}
            >
              {submitting ? "Agendando..." : "Confirmar agendamento"}
            </button>
          )}

        </form>

      </div>
    </div>
  );
}
