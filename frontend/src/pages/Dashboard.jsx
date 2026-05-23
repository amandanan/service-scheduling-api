import { useEffect, useState } from "react";
import api from "../services/api";
import Navbar from "../components/Navbar";

import {
  FaUsers,
  FaTools,
  FaCalendarAlt,
} from "react-icons/fa";

import "../styles/dashboard.css";

export default function Dashboard() {
  const [clients, setClients] = useState(0);
  const [services, setServices] = useState(0);
  const [appointments, setAppointments] = useState(0);

  async function loadData() {
    try {
      const [c, s, a] = await Promise.all([
        api.get("/clients"),
        api.get("/services"),
        api.get("/appointments"),
      ]);

      setClients(c.data.length);
      setServices(s.data.length);
      setAppointments(a.data.length);

    } catch (error) {
      console.error("Erro ao carregar dashboard:", error);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="dashboard-page">
      <Navbar />

      <div className="dashboard-container">

        <div className="dashboard-header">
          <h1 className="dashboard-title">
            Dashboard
          </h1>

          <p className="dashboard-subtitle">
            Visão geral do sistema
          </p>
        </div>

        <div className="dashboard-grid">

          <Card
            title="Clientes"
            value={clients}
            icon={<FaUsers />}
          />

          <Card
            title="Serviços"
            value={services}
            icon={<FaTools />}
          />

          <Card
            title="Agendamentos"
            value={appointments}
            icon={<FaCalendarAlt />}
          />

        </div>
      </div>
    </div>
  );
}

function Card({ title, value, icon }) {
  return (
    <div className="dashboard-card">

      <div className="dashboard-card-top">

        <div>
          <p className="dashboard-card-title">
            {title}
          </p>

          <h2 className="dashboard-card-value">
            {value}
          </h2>
        </div>

        <div className="dashboard-icon">
          {icon}
        </div>

      </div>

      <div className="dashboard-card-footer">
        Total cadastrados
      </div>

    </div>
  );
}

