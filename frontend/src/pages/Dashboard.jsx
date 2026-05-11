import { useEffect, useState } from "react";
import api from "../services/api";
import Navbar from "../components/Navbar";
import "../App.css";

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
    <div style={{ padding: "20px" }}>
      <Navbar />

      <h1 style={{ marginBottom: "20px" }}>Dashboard</h1>

      <div
        style={{
          display: "flex",
          gap: "20px",
          flexWrap: "wrap",
        }}
      >
        <Card title="Clientes" value={clients} />
        <Card title="Serviços" value={services} />
        <Card title="Agendamentos" value={appointments} />
      </div>
    </div>
  );
}

function Card({ title, value }) {
  return (
    <div
      style={{
        padding: "20px",
        border: "1px solid #ccc",
        borderRadius: "10px",
        minWidth: "180px",
        backgroundColor: "#fff",
        boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
      }}
    >
      <h3>{title}</h3>

      <p
        style={{
          fontSize: "28px",
          fontWeight: "bold",
          marginTop: "10px",
        }}
      >
        {value}
      </p>
    </div>
  );
}

