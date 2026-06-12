import { useEffect, useState } from "react";

import { getDashboardStats, getSettings } from "../services/api";

import Navbar from "../components/Navbar";

import {
  FaUsers,
  FaCalendarCheck,
  FaMoneyBillWave,
  FaTools,
  FaClock,
  FaStar,
} from "react-icons/fa";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line,
} from "recharts";

import "../styles/dashboard.css";

function brl(value) {
  return `R$ ${Number(value || 0).toFixed(2)}`;
}

export default function Dashboard() {

  const [stats, setStats] = useState(null);
  const [term, setTerm] = useState({ singular: "Cliente", plural: "Clientes" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  async function loadData() {

    setLoading(true);
    setError(false);

    try {

      const [data, settings] = await Promise.all([
        getDashboardStats(),
        getSettings(),
      ]);

      setStats(data);
      setTerm({
        singular: settings.client_term_singular,
        plural: settings.client_term_plural,
      });

    } catch (err) {

      console.error("Erro ao carregar dashboard:", err);
      setError(true);

    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="dashboard-page">
        <Navbar />
        <div className="dashboard-container">
          <div className="dashboard-state">Carregando dashboard...</div>
        </div>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="dashboard-page">
        <Navbar />
        <div className="dashboard-container">
          <div className="dashboard-state">
            <p>Não foi possível carregar o dashboard.</p>
            <button className="dashboard-retry-btn" onClick={loadData}>
              Tentar novamente
            </button>
          </div>
        </div>
      </div>
    );
  }

  const { kpis } = stats;

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

          {/* RECEITA MES */}
          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">Mês</p>
                <h2 className="dashboard-card-value">{brl(kpis.month_revenue)}</h2>
              </div>
              <div className="dashboard-icon"><FaMoneyBillWave /></div>
            </div>
            <div className="dashboard-card-footer">Receita mensal</div>
          </div>

          {/* META MENSAL */}
          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">Meta Mensal</p>
                <h2 className="dashboard-card-value">{kpis.goal_progress.toFixed(0)}%</h2>
              </div>
              <div className="dashboard-icon"><FaMoneyBillWave /></div>
            </div>
            <div className="goal-progress-bar">
              <div
                className="goal-progress-fill"
                style={{ width: `${kpis.goal_progress}%` }}
              />
            </div>
            <div className="dashboard-card-footer">
              {brl(kpis.month_revenue)} {" / "} {brl(kpis.monthly_goal)}
            </div>
          </div>

          {/* CRESCIMENTO MENSAL */}
          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">Crescimento</p>
                <h2 className="dashboard-card-value">
                  {kpis.monthly_growth >= 0 ? "↑" : "↓"}{" "}
                  {Math.abs(kpis.monthly_growth).toFixed(1)}%
                </h2>
              </div>
              <div className="dashboard-icon"><FaCalendarCheck /></div>
            </div>
            <div className="dashboard-card-footer">Comparado ao mês anterior</div>
          </div>

          {/* FATURAMENTO PREVISTO */}
          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">Previsto</p>
                <h2 className="dashboard-card-value">{brl(kpis.forecast_revenue)}</h2>
              </div>
              <div className="dashboard-icon"><FaMoneyBillWave /></div>
            </div>
            <div className="dashboard-card-footer">Receita futura agendada</div>
          </div>

          {/* AGENDAMENTOS HOJE */}
          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">Hoje</p>
                <h2 className="dashboard-card-value">{kpis.today_appointments}</h2>
              </div>
              <div className="dashboard-icon"><FaCalendarCheck /></div>
            </div>
            <div className="dashboard-card-footer">Agendamentos do dia</div>
          </div>

          {/* OCUPACAO */}
          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">Ocupação</p>
                <h2 className="dashboard-card-value">{kpis.occupancy_rate}%</h2>
              </div>
              <div className="dashboard-icon"><FaCalendarCheck /></div>
            </div>
            <div className="dashboard-card-footer">Agenda ocupada hoje</div>
          </div>

          {/* TICKET MEDIO */}
          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">Ticket Médio</p>
                <h2 className="dashboard-card-value">{brl(kpis.average_ticket)}</h2>
              </div>
              <div className="dashboard-icon"><FaMoneyBillWave /></div>
            </div>
            <div className="dashboard-card-footer">Receita média por atendimento</div>
          </div>

          {/* FATURAMENTO HOJE */}
          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">Hoje</p>
                <h2 className="dashboard-card-value">{brl(kpis.today_revenue)}</h2>
              </div>
              <div className="dashboard-icon"><FaMoneyBillWave /></div>
            </div>
            <div className="dashboard-card-footer">Receita de hoje</div>
          </div>

        </div>

        <div className="dashboard-grid">

          {/* CLIENTES */}
          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">{term.plural}</p>
                <h2 className="dashboard-card-value">{kpis.total_clients}</h2>
              </div>
              <div className="dashboard-icon"><FaUsers /></div>
            </div>
            <div className="dashboard-card-footer">
              Total de {term.plural.toLowerCase()} cadastrados
            </div>
          </div>

          {/* NOVOS CLIENTES */}
          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">Novos {term.plural}</p>
                <h2 className="dashboard-card-value">{kpis.new_clients_month}</h2>
              </div>
              <div className="dashboard-icon"><FaUsers /></div>
            </div>
            <div className="dashboard-card-footer">Cadastros realizados este mês</div>
          </div>

          {/* SERVIÇOS */}
          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">Serviços</p>
                <h2 className="dashboard-card-value">{kpis.total_services}</h2>
              </div>
              <div className="dashboard-icon"><FaTools /></div>
            </div>
            <div className="dashboard-card-footer">Serviços disponíveis</div>
          </div>

          {/* AVALIAÇÕES */}
          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">Avaliações</p>
                <h2 className="dashboard-card-value">
                  {kpis.average_rating != null ? kpis.average_rating.toFixed(1) : "—"}
                </h2>
              </div>
              <div className="dashboard-icon"><FaStar /></div>
            </div>
            <div className="dashboard-card-footer">
              {kpis.total_reviews} {kpis.total_reviews === 1 ? "avaliação" : "avaliações"}
            </div>
          </div>

        </div>

        {/* GRÁFICOS */}

        <div className="dashboard-charts-grid">
          <div className="dashboard-chart-card">
            <h3 className="dashboard-chart-title">Agendamentos da Semana</h3>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={stats.weekly_appointments}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="agendamentos" fill="#6d28d9" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="dashboard-charts-grid">
          <div className="dashboard-chart-card">
            <h3 className="dashboard-chart-title">Faturamento Últimos 6 Meses</h3>
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={stats.monthly_revenue_chart}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => brl(value)} />
                <Line
                  type="monotone"
                  dataKey="revenue"
                  stroke="#6d28d9"
                  strokeWidth={3}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="dashboard-charts-grid">

          {/* PRÓXIMOS */}
          <div className="dashboard-chart-card">
            <h3 className="dashboard-chart-title">Próximos Atendimentos</h3>
            {stats.today_appointments_list.length === 0 ? (
              <div className="empty-state">Nenhum agendamento hoje</div>
            ) : (
              stats.today_appointments_list.map((appointment) => (
                <div key={appointment.id} className="appointment-item">
                  <div className="appointment-time">
                    <FaClock />
                    {appointment.time}
                  </div>
                  <div className="appointment-info">
                    <strong>{appointment.client}</strong>
                    <span>{appointment.service}</span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* AGENDA DE AMANHÃ */}
          <div className="dashboard-chart-card">
            <h3 className="dashboard-chart-title">Agenda de Amanhã</h3>
            {stats.tomorrow_appointments.length === 0 ? (
              <div className="empty-state">Nenhum agendamento amanhã</div>
            ) : (
              stats.tomorrow_appointments.map((appointment) => (
                <div key={appointment.id} className="appointment-item">
                  <div className="appointment-time">
                    <FaClock />
                    {appointment.time}
                  </div>
                  <div className="appointment-info">
                    <strong>{appointment.client}</strong>
                    <span>{appointment.service}</span>
                  </div>
                </div>
              ))
            )}
          </div>

        </div>

        <div className="dashboard-charts-grid">

          {/* SERVIÇOS MAIS USADOS */}
          <div className="dashboard-chart-card">
            <h3 className="dashboard-chart-title">Serviços Mais Realizados</h3>
            {stats.top_services.length === 0 ? (
              <div className="empty-state">Nenhum serviço realizado</div>
            ) : (
              stats.top_services.map((service) => {
                const maxValue = stats.top_services[0]?.total || 1;
                const percentage = (service.total / maxValue) * 100;
                return (
                  <div key={service.name} className="service-ranking-item">
                    <div className="service-ranking-header">
                      <strong>{service.name}</strong>
                      <span>{service.total}</span>
                    </div>
                    <div className="service-ranking-bar">
                      <div
                        className="service-ranking-fill"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* TOP CLIENTES */}
          <div className="dashboard-chart-card">
            <h3 className="dashboard-chart-title">Top {term.plural}</h3>
            {stats.top_clients.length === 0 ? (
              <div className="empty-state">Nenhum {term.singular.toLowerCase()}</div>
            ) : (
              stats.top_clients.map((patient, index) => (
                <div key={patient.id} className="appointment-item">
                  <div className="appointment-info">
                    <strong>#{index + 1} {patient.name}</strong>
                    <span>{patient.total} atendimentos</span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* CLIENTES SEM RETORNO */}
          <div className="dashboard-chart-card">
            <h3 className="dashboard-chart-title">{term.plural} Sem Retorno</h3>
            {stats.inactive_clients.length === 0 ? (
              <div className="empty-state">Nenhum {term.singular.toLowerCase()} sem retorno</div>
            ) : (
              stats.inactive_clients.map((patient) => (
                <div key={patient.id} className="appointment-item">
                  <div className="appointment-info">
                    <strong>{patient.name}</strong>
                    <span>{patient.days} dias sem atendimento</span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* ANIVERSARIANTES */}
          <div className="dashboard-chart-card">
            <h3 className="dashboard-chart-title">Aniversariantes do Mês</h3>
            {stats.birthday_clients.length === 0 ? (
              <div className="empty-state">Nenhum aniversariante este mês</div>
            ) : (
              stats.birthday_clients.map((client) => (
                <div key={client.id} className="appointment-item">
                  <div className="appointment-info">
                    <strong>{client.name}</strong>
                    <span>{client.birth_date.split("-").reverse().join("/")}</span>
                  </div>
                </div>
              ))
            )}
          </div>

        </div>

        <div className="dashboard-charts-grid">
          {/* ALERTAS */}
          <div className="dashboard-chart-card">
            <h3 className="dashboard-chart-title">Alertas Inteligentes</h3>
            {stats.alerts.length === 0 ? (
              <div className="empty-state">Nenhum alerta</div>
            ) : (
              stats.alerts.map((alert, index) => (
                <div key={index} className={`alert-item ${alert.type}`}>
                  {alert.text}
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
