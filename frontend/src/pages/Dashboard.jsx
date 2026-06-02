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

  const [nextAppointments, setNextAppointments] =
  useState([]);

  const [monthlyRevenue, setMonthlyRevenue] =
    useState(0);

  const [topServices, setTopServices] =
    useState([]);

  const [birthdayClients, setBirthdayClients] =
    useState([]);

  const [forecastRevenue, setForecastRevenue] =
    useState(0);

  const [occupancyRate, setOccupancyRate] =
    useState(0);

  const [monthlyGoal] =
    useState(10000);

  const [goalProgress, setGoalProgress] =
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

    const currentMonth =
      new Date().getMonth();

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
    
    const appointmentsToday =
      todayList.length;

    const dailyCapacity = 20;

    const occupancy =
      Math.round(
        (appointmentsToday /
          dailyCapacity) * 100
      );

    setOccupancyRate(
      occupancy > 100
        ? 100
        : occupancy
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

    // META MENSAL

    const progress =
      Math.min(
        (monthRevenue / monthlyGoal) * 100,
        100
      );

    setGoalProgress(progress);

    // FATURAMENTO PREVISTO

      let forecast = 0;

        appointmentsData.forEach(
          (appointment) => {

            const appointmentDate =
              new Date(
                appointment.scheduled_at
              );

            if (
              appointmentDate >= new Date()
            ) {

              const service =
                servicesData.find(
                  (s) =>
                    s.id === appointment.service_id
                );

              forecast += Number(
                service?.price || 0
              );
            }
          }
        );

        setForecastRevenue(forecast);

    // PROXIMOS AGENDAMENTOS 

      const upcoming =
        appointmentsData
          .filter(
            appointment =>
              new Date(
                appointment.scheduled_at
              ) > new Date()
          )
          .sort(
            (a, b) =>
              new Date(a.scheduled_at) -
              new Date(b.scheduled_at)
          )
          .slice(0, 5)
          .map((appointment) => {

            const client =
              clientsData.find(
                c =>
                  c.id === appointment.client_id
              );

            const service =
              servicesData.find(
                s =>
                  s.id === appointment.service_id
              );

            return {
              id: appointment.id,
              client: client?.full_name,
              service: service?.name,
              date: appointment.scheduled_at,
            };
          });

      setNextAppointments(upcoming);


    // SERVICOS MAIS REALIZADOS

      const serviceCount = {};

        appointmentsData.forEach(
          (appointment) => {

            serviceCount[
              appointment.service_id
            ] =
              (serviceCount[
                appointment.service_id
              ] || 0) + 1;
          }
        );

        const ranking =
          Object.entries(serviceCount)
            .map(([id, total]) => {

              const service =
                servicesData.find(
                  (s) =>
                    s.id === Number(id)
                );

              return {

                name:
                  service?.name ||
                  "Serviço",

                total,
              };
            })
            .sort(
              (a, b) =>
                b.total - a.total
            )
            .slice(0, 5);

        setTopServices(ranking);

    // ANIVERSARIANTE

      const birthdays =
        clientsData.filter((client) => {

          if (!client.birth_date)
            return false;

          const month =
            Number(
              client.birth_date.split("-")[1]
            );

          return month === currentMonth;
        });

      setBirthdayClients(
        birthdays.slice(0, 5)
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
          
          {/* OCUPACAO */}
          </div>

          <div className="dashboard-card">

            <div className="dashboard-card-top">

              <div>

                <p className="dashboard-card-title">
                  Ocupação
                </p>

                <h2 className="dashboard-card-value">
                  {occupancyRate}%
                </h2>

              </div>

              <div className="dashboard-icon">

                <FaCalendarCheck />

              </div>

            </div>

            <div className="dashboard-card-footer">
              Agenda ocupada hoje
            </div>

          </div>
        

        </div>

         {/* FATURAMENTO */}

          <div className="dashboard-card">

            <div className="dashboard-card-top">

              <div>

                <p className="dashboard-card-title">
                  Hoje
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
            Receita mensal
          </div>
        </div>

        {/* META MENSAL*/}

        <div className="dashboard-card">

          <div className="dashboard-card-top">

            <div>

              <p className="dashboard-card-title">
                Meta Mensal
              </p>

              <h2 className="dashboard-card-value">
                {goalProgress.toFixed(0)}%
              </h2>

            </div>

            <div className="dashboard-icon">

              <FaMoneyBillWave />

            </div>

          </div>

          <div className="goal-progress-bar">

            <div
              className="goal-progress-fill"
              style={{
                width: `${goalProgress}%`,
              }}
            />

          </div>

          <div className="dashboard-card-footer">

            R$ {monthlyRevenue.toFixed(2)}
            {" / "}
            R$ {monthlyGoal.toFixed(2)}

          </div>

        </div>

        {/* FATURAMENTO PREVISTO */}

          <div className="dashboard-card">

            <div className="dashboard-card-top">

              <div>

                <p className="dashboard-card-title">
                  Previsto
                </p>

                <h2 className="dashboard-card-value">
                  R$ {forecastRevenue.toFixed(2)}
                </h2>

              </div>

              <div className="dashboard-icon">

                <FaMoneyBillWave />

              </div>

            </div>

            <div className="dashboard-card-footer">
              Receita futura agendada
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

      <div className="dashboard-charts-grid">

        {/* SERVICOS MAIS USADOS */}

          <div className="dashboard-chart-card">

            <h3 className="dashboard-chart-title">
              Serviços Mais Realizados
            </h3>

            {topServices.map((service) => {

              const maxValue =
                topServices[0]?.total || 1;

              const percentage =
                (service.total / maxValue) * 100;

              return (

                <div
                  key={service.name}
                  className="service-ranking-item"
                >

                  <div className="service-ranking-header">

                    <strong>
                      {service.name}
                    </strong>

                    <span>
                      {service.total}
                    </span>

                  </div>

                  <div className="service-ranking-bar">

                    <div
                      className="service-ranking-fill"
                      style={{
                        width: `${percentage}%`
                      }}
                    />

                  </div>

                </div>

                  );

                })}

          </div>

      {/* ANIVERSARIANTES */}

        <div className="dashboard-chart-card">

            <h3 className="dashboard-chart-title">
              Aniversariantes do Mês
            </h3>

            {birthdayClients.length === 0 ? (

              <div className="empty-state">
                Nenhum aniversariante este mês
              </div>

            ) : (

              birthdayClients.map(
                (client) => (

                  <div
                    key={client.id}
                    className="appointment-item"
                  >

                    <div className="appointment-info">

                      <strong>
                        {client.full_name}
                      </strong>

                      <span>
                        {client.birth_date}
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