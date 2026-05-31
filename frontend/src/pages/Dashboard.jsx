import { useEffect, useState } from "react";

import api from "../services/api";

import Navbar from "../components/Navbar";

import {
  FaUsers,
  FaCalendarCheck,
  FaMoneyBillWave,
  FaTools,
  FaClock,
} from "react-icons/fa";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

import "../styles/dashboard.css";

export default function Dashboard() {

  const [clients, setClients] =
    useState([]);

  const [services, setServices] =
    useState([]);

  const [appointments, setAppointments] =
    useState([]);

  const [weeklyData, setWeeklyData] =
    useState([]);

  const [todayRevenue, setTodayRevenue] =
    useState(0);

  const [todayAppointments, setTodayAppointments] =
    useState([]);

  const [monthlyRevenue, setMonthlyRevenue] =
  useState(0);

  async function loadData() {

    try {

      const [
        clientsRes,
        servicesRes,
        appointmentsRes,
      ] = await Promise.all([

        api.get("/clients/"),

        api.get("/services/"),

        api.get("/appointments/"),
      ]);

      setClients(clientsRes.data);

      setServices(servicesRes.data);

      setAppointments(
        appointmentsRes.data
      );

      calculateDashboardData(
        appointmentsRes.data,
        servicesRes.data,
        clientsRes.data
      );

    } catch (error) {

      console.error(
        "Erro ao carregar dashboard:",
        error
      );
    }
  }

  function calculateDashboardData(
    appointmentsData,
    servicesData,
    clientsData
  ) {

    const today =
      new Date()
        .toISOString()
        .split("T")[0];

    let revenue = 0;

    const todayList =
      appointmentsData.filter(
        (appointment) => {

          const appointmentDate =
            appointment.scheduled_at
              .split("T")[0];

          return appointmentDate === today;
        }
      );

    todayList.forEach((appointment) => {

      const service =
        servicesData.find(
          (s) =>
            s.id === appointment.service_id
        );

      revenue +=
        Number(service?.price || 0);
    });

    setTodayRevenue(revenue);

    // FATURAMENTO DO MÊS

        const currentMonth =
          new Date().getMonth();

        const currentYear =
          new Date().getFullYear();

        let monthRevenue = 0;

        appointmentsData.forEach(
          (appointment) => {

            const appointmentDate =
              new Date(
                appointment.scheduled_at
              );

            if (
              appointmentDate.getMonth() ===
                currentMonth &&
              appointmentDate.getFullYear() ===
                currentYear
            ) {

              const service =
                servicesData.find(
                  (s) =>
                    s.id === appointment.service_id
                );

              monthRevenue += Number(
                service?.price || 0
              );
            }
          }
        );

        setMonthlyRevenue(
          monthRevenue
        );

    const formattedTodayAppointments =
      todayList.map((appointment) => {

        const client =
          clientsData.find(
            (c) =>
              c.id === appointment.client_id
          );

        const service =
          servicesData.find(
            (s) =>
              s.id === appointment.service_id
          );

        return {

          id: appointment.id,

          client:
            client?.full_name ||
            "Cliente",

          service:
            service?.name ||
            "Serviço",

          time:
            appointment.scheduled_at
              .split("T")[1]
              ?.slice(0, 5),
        };
      });

    setTodayAppointments(
      formattedTodayAppointments
    );

    const weekMap = {

      Dom: 0,
      Seg: 0,
      Ter: 0,
      Qua: 0,
      Qui: 0,
      Sex: 0,
      Sab: 0,
    };

    appointmentsData.forEach(
      (appointment) => {

        const date =
          new Date(
            appointment.scheduled_at
          );

        const day =
          [
            "Dom",
            "Seg",
            "Ter",
            "Qua",
            "Qui",
            "Sex",
            "Sab",
          ][date.getDay()];

        weekMap[day]++;
      }
    );

    const chartData =
      Object.keys(weekMap).map(
        (day) => ({
          day,
          agendamentos:
            weekMap[day],
        })
      );

    setWeeklyData(chartData);
  }

  useEffect(() => {
    loadData();
  }, []);

  return (

    <div className="dashboard-page">

      <Navbar />

      <div className="dashboard-container">

        {/* HEADER */}

        <div className="dashboard-header">

          <h1 className="dashboard-title">
            Dashboard
          </h1>

          <p className="dashboard-subtitle">
            Visão geral do sistema
          </p>

        </div>

        {/* CARDS */}

        <div className="dashboard-grid">

          {/* PACIENTES */}

          <div className="dashboard-card">

            <div className="dashboard-card-top">

              <div>

                <p className="dashboard-card-title">
                  Pacientes
                </p>

                <h2 className="dashboard-card-value">
                  {clients.length}
                </h2>

              </div>

              <div className="dashboard-icon">

                <FaUsers />

              </div>

            </div>

            <div className="dashboard-card-footer">
              Total de pacientes cadastrados
            </div>

          </div>

          {/* SERVIÇOS */}

          <div className="dashboard-card">

            <div className="dashboard-card-top">

              <div>

                <p className="dashboard-card-title">
                  Serviços
                </p>

                <h2 className="dashboard-card-value">
                  {services.length}
                </h2>

              </div>

              <div className="dashboard-icon">

                <FaTools />

              </div>

            </div>

            <div className="dashboard-card-footer">
              Serviços disponíveis
            </div>

          </div>

          {/* AGENDAMENTOS */}

          <div className="dashboard-card">

            <div className="dashboard-card-top">

              <div>

                <p className="dashboard-card-title">
                  Hoje
                </p>

                <h2 className="dashboard-card-value">
                  {
                    todayAppointments.length
                  }
                </h2>

              </div>

              <div className="dashboard-icon">

                <FaCalendarCheck />

              </div>

            </div>

            <div className="dashboard-card-footer">
              Agendamentos do dia
            </div>

          </div>

          {/* FATURAMENTO */}

          <div className="dashboard-card">

            <div className="dashboard-card-top">

              <div>

                <p className="dashboard-card-title">
                  Faturamento
                </p>

                <h2 className="dashboard-card-value">
                  R$ {todayRevenue}
                </h2>

              </div>

              <div className="dashboard-icon">

                <FaMoneyBillWave />

              </div>

            </div>

            <div className="dashboard-card-footer">
              Receita de hoje
            </div>

          </div>

        </div>

        <div className="dashboard-card">

          <div className="dashboard-card-top">

            <div>

              <p className="dashboard-card-title">
                Mês
              </p>

              <h2 className="dashboard-card-value">
                R$ {monthlyRevenue}
              </h2>

            </div>

            <div className="dashboard-icon">

              <FaMoneyBillWave />

            </div>

          </div>

          <div className="dashboard-card-footer">
            Faturamento mensal
          </div>

        </div>

        {/* GRÁFICOS */}

        <div className="dashboard-charts-grid">

          {/* GRÁFICO */}

          <div className="dashboard-chart-card">

            <h3 className="dashboard-chart-title">
              Agendamentos da Semana
            </h3>

            <ResponsiveContainer
              width="100%"
              height={320}
            >

              <BarChart
                data={weeklyData}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                />

                <XAxis dataKey="day" />

                <YAxis />

                <Tooltip />

                <Bar
                  dataKey="agendamentos"
                  radius={[8, 8, 0, 0]}
                />

              </BarChart>

            </ResponsiveContainer>

          </div>

          {/* PRÓXIMOS */}

          <div className="dashboard-chart-card">

            <h3 className="dashboard-chart-title">
              Próximos Atendimentos
            </h3>

            {todayAppointments.length === 0 ? (

              <div className="empty-state">

                Nenhum agendamento hoje

              </div>

            ) : (

              todayAppointments.map(
                (appointment) => (

                  <div
                    key={appointment.id}
                    className="appointment-item"
                  >

                    <div className="appointment-time">

                      <FaClock />

                      {appointment.time}

                    </div>

                    <div className="appointment-info">

                      <strong>
                        {appointment.client}
                      </strong>

                      <span>
                        {appointment.service}
                      </span>

                    </div>

                  </div>
                )
              )

            )}

          </div>

        </div>

      </div>

    </div>
  );
}