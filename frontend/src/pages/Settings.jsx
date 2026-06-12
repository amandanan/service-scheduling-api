import { useEffect, useState } from "react";
import { toast } from "react-toastify";

import { getSettings, updateSettings } from "../services/api";

import Navbar from "../components/Navbar";

import { FaCog, FaSave } from "react-icons/fa";

import "../styles/services.css";

export default function Settings() {

  const [businessName, setBusinessName] = useState("");
  const [bookingSlug, setBookingSlug] = useState("");

  const [monthlyGoal, setMonthlyGoal] = useState("");
  const [dailyCapacity, setDailyCapacity] = useState("");
  const [termSingular, setTermSingular] = useState("");
  const [termPlural, setTermPlural] = useState("");

  const [saving, setSaving] = useState(false);


  async function loadData() {

    try {

      const data = await getSettings();

      setBusinessName(data.full_name);
      setBookingSlug(data.booking_slug);
      setMonthlyGoal(data.monthly_goal);
      setDailyCapacity(data.daily_capacity);
      setTermSingular(data.client_term_singular);
      setTermPlural(data.client_term_plural);

    } catch (error) {

      console.error(error);

      toast.error("Erro ao carregar configurações");
    }
  }


  useEffect(() => {
    loadData();
  }, []);


  async function handleSubmit(e) {

    e.preventDefault();

    if (!termSingular.trim() || !termPlural.trim()) {
      toast.error("Informe como você chama seus clientes");
      return;
    }

    if (!monthlyGoal || Number(monthlyGoal) < 0) {
      toast.error("Informe uma meta mensal válida");
      return;
    }

    if (!dailyCapacity || Number(dailyCapacity) < 1) {
      toast.error("A capacidade diária deve ser ao menos 1");
      return;
    }

    setSaving(true);

    try {

      await updateSettings({
        monthly_goal: Number(monthlyGoal),
        daily_capacity: Number(dailyCapacity),
        client_term_singular: termSingular.trim(),
        client_term_plural: termPlural.trim(),
      });

      toast.success("Configurações salvas");

    } catch (error) {

      console.error(error);

      toast.error("Erro ao salvar configurações");

    } finally {
      setSaving(false);
    }
  }


  const publicLink = `${window.location.origin}/agendar/${bookingSlug}`;


  return (

    <div className="services-page">

      <Navbar />

      <div className="services-container">

        <div className="services-card">

          <h1 className="services-title">
            <FaCog />
            Configurações
          </h1>

          <form onSubmit={handleSubmit} className="settings-form">

            <div className="settings-section">
              <h3 className="settings-section-title">Estabelecimento</h3>

              <div className="settings-field">
                <label>Nome do negócio</label>
                <input type="text" value={businessName} disabled />
              </div>

              <div className="settings-field">
                <label>Link público de agendamento</label>
                <input type="text" value={publicLink} disabled />
              </div>
            </div>

            <div className="settings-section">
              <h3 className="settings-section-title">Terminologia</h3>
              <p className="settings-hint">
                Como você chama quem atende? Ex.: Cliente, Paciente, Tutor, Aluno.
                Esse termo é usado nos rótulos do painel.
              </p>

              <div className="settings-row">
                <div className="settings-field">
                  <label>Singular</label>
                  <input
                    type="text"
                    value={termSingular}
                    onChange={(e) => setTermSingular(e.target.value)}
                    placeholder="Cliente"
                  />
                </div>

                <div className="settings-field">
                  <label>Plural</label>
                  <input
                    type="text"
                    value={termPlural}
                    onChange={(e) => setTermPlural(e.target.value)}
                    placeholder="Clientes"
                  />
                </div>
              </div>
            </div>

            <div className="settings-section">
              <h3 className="settings-section-title">Metas e capacidade</h3>

              <div className="settings-row">
                <div className="settings-field">
                  <label>Meta de faturamento mensal (R$)</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={monthlyGoal}
                    onChange={(e) => setMonthlyGoal(e.target.value)}
                  />
                </div>

                <div className="settings-field">
                  <label>Capacidade de atendimentos por dia</label>
                  <input
                    type="number"
                    min="1"
                    value={dailyCapacity}
                    onChange={(e) => setDailyCapacity(e.target.value)}
                  />
                </div>
              </div>
            </div>

            <button type="submit" className="primary-btn" disabled={saving}>
              <FaSave />
              {saving ? "Salvando..." : "Salvar configurações"}
            </button>

          </form>

        </div>

      </div>

    </div>
  );
}
