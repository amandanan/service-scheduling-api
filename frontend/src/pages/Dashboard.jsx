import { useEffect, useState } from "react";

import {
  getDashboardStats,
  getDashboardMetrics,
  getSettings,
  getProfessionals,
  downloadReport,
  downloadCsv,
} from "../services/api";

import Navbar from "../components/Navbar";

import {
  FaUsers,
  FaCalendarCheck,
  FaMoneyBillWave,
  FaTools,
  FaClock,
  FaStar,
  FaChartLine,
  FaReceipt,
  FaUserSlash,
  FaBan,
  FaCheckDouble,
  FaDownload,
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

function pct(value) {
  return `${Number(value || 0).toFixed(1)}%`;
}

function toISODate(date) {
  return date.toISOString().split("T")[0];
}

// Period presets compute a {startDate, endDate} range (or {} for "this month").
const PERIODS = [
  { key: "today", label: "Hoje" },
  { key: "7d", label: "7 dias" },
  { key: "30d", label: "30 dias" },
  { key: "month", label: "Este mês" },
];

function rangeForPeriod(key) {
  const today = new Date();

  if (key === "today") {
    const d = toISODate(today);
    return { startDate: d, endDate: d };
  }

  if (key === "7d") {
    const start = new Date(today);
    start.setDate(start.getDate() - 6);
    return { startDate: toISODate(start), endDate: toISODate(today) };
  }

  if (key === "30d") {
    const start = new Date(today);
    start.setDate(start.getDate() - 29);
    return { startDate: toISODate(start), endDate: toISODate(today) };
  }

  // "month" → let the backend default to the current month
  return {};
}

export default function Dashboard() {

  const [stats, setStats] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [term, setTerm] = useState({ singular: "Cliente", plural: "Clientes" });
  const [professionals, setProfessionals] = useState([]);

  const [period, setPeriod] = useState("month");
  const [professionalId, setProfessionalId] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [exporting, setExporting] = useState(null); // "pdf" | "csv" | null

  async function loadStaticData() {
    try {
      const [settings, pros] = await Promise.all([
        getSettings(),
        getProfessionals(),
      ]);
      setTerm({
        singular: settings.client_term_singular,
        plural: settings.client_term_plural,
      });
      setProfessionals(pros);
    } catch (err) {
      console.error("Erro ao carregar configurações:", err);
    }
  }

  async function loadStats() {
    setLoading(true);
    setError(false);

    try {
      const range = rangeForPeriod(period);
      // metrics are account-wide (no professional filter on the endpoint)
      const [data, metricsData] = await Promise.all([
        getDashboardStats({
          professionalId: professionalId || undefined,
          ...range,
        }),
        getDashboardMetrics(range),
      ]);
      setStats(data);
      setMetrics(metricsData);
    } catch (err) {
      console.error("Erro ao carregar dashboard:", err);
      setError(true);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadStaticData();
  }, []);

  useEffect(() => {
    loadStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [period, professionalId]);

  async function handleExportPdf() {
    setExporting("pdf");
    try {
      await downloadReport(rangeForPeriod(period));
    } catch (err) {
      console.error("Erro ao gerar PDF:", err);
    } finally {
      setExporting(null);
    }
  }

  async function handleExportCsv() {
    setExporting("csv");
    try {
      await downloadCsv(rangeForPeriod(period));
    } catch (err) {
      console.error("Erro ao exportar CSV:", err);
    } finally {
      setExporting(null);
    }
  }

  function periodLabel() {
    if (!stats) return "";
    const { start, end } = stats.period;
    const fmt = (s) => s.split("-").reverse().join("/");
    return start === end ? fmt(start) : `${fmt(start)} – ${fmt(end)}`;
  }

  const controls = (
    <div className="dashboard-controls">
      <select
        className="dashboard-select"
        value={professionalId}
        onChange={(e) => setProfessionalId(e.target.value)}
      >
        <option value="">Todos os profissionais</option>
        {professionals.map((p) => (
          <option key={p.id} value={p.id}>{p.name}</option>
        ))}
      </select>

      <div className="dashboard-period">
        {PERIODS.map((p) => (
          <button
            key={p.key}
            type="button"
            className={period === p.key ? "period-btn active" : "period-btn"}
            onClick={() => setPeriod(p.key)}
          >
            {p.label}
          </button>
        ))}
      </div>

      <div className="dashboard-exports">
        <button
          type="button"
          className="export-btn export-pdf"
          onClick={handleExportPdf}
          disabled={exporting !== null}
        >
          <FaDownload />
          {exporting === "pdf" ? "Gerando relatório..." : "Relatório PDF"}
        </button>
        <button
          type="button"
          className="export-btn export-csv"
          onClick={handleExportCsv}
          disabled={exporting !== null}
        >
          {exporting === "csv" ? "..." : "CSV"}
        </button>
      </div>
    </div>
  );

  const header = (
    <div className="dashboard-header">
      <div>
        <h1 className="dashboard-title">Dashboard</h1>
        <p className="dashboard-subtitle">Visão geral do seu negócio</p>
      </div>
      {controls}
    </div>
  );

  if (loading && !stats) {
    return (
      <div className="dashboard-page">
        <Navbar />
        <div className="dashboard-container">
          {header}
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
          {header}
          <div className="dashboard-state">
            <p>Não foi possível carregar o dashboard.</p>
            <button className="dashboard-retry-btn" onClick={loadStats}>
              Tentar novamente
            </button>
          </div>
        </div>
      </div>
    );
  }

  const { kpis, period: periodData } = stats;

  return (
    <div className="dashboard-page">
      <Navbar />

      <div className={`dashboard-container ${loading ? "is-refreshing" : ""}`}>

        {header}

        {/* RESUMO DO PERÍODO */}
        <div className="period-summary">
          <div className="period-summary-head">
            <h3>Resumo do período</h3>
            <span className="period-summary-range">{periodLabel()}</span>
          </div>

          <div className="period-summary-grid">
            <div className="period-summary-card">
              <div className="period-summary-icon"><FaChartLine /></div>
              <div>
                <p className="period-summary-label">Faturamento</p>
                <h2 className="period-summary-value">{brl(periodData.revenue)}</h2>
              </div>
            </div>

            <div className="period-summary-card">
              <div className="period-summary-icon"><FaCalendarCheck /></div>
              <div>
                <p className="period-summary-label">Atendimentos</p>
                <h2 className="period-summary-value">{periodData.appointments}</h2>
              </div>
            </div>

            <div className="period-summary-card">
              <div className="period-summary-icon"><FaReceipt /></div>
              <div>
                <p className="period-summary-label">Ticket médio</p>
                <h2 className="period-summary-value">{brl(periodData.ticket)}</h2>
              </div>
            </div>
          </div>
        </div>

        {/* INDICADORES DE DESEMPENHO */}
        {metrics && (
          <div className="metrics-section">
            <div className="period-summary-head">
              <h3>Indicadores de desempenho</h3>
              <span className="period-summary-range">{periodLabel()}</span>
            </div>

            {metrics.total_appointments === 0 ? (
              <div className="dashboard-chart-card">
                <div className="empty-state">
                  Nenhum atendimento no período selecionado
                </div>
              </div>
            ) : (
              <>
                <div className="metrics-grid">
                  <div className="metric-card good">
                    <div className="metric-card-top">
                      <span className="metric-card-icon"><FaCheckDouble /></span>
                      <span className="metric-card-label">Taxa de comparecimento</span>
                    </div>
                    <h2 className="metric-card-value">{pct(metrics.realization_rate)}</h2>
                    <p className="metric-card-foot">
                      {metrics.completed} de {metrics.expected} previstos
                    </p>
                  </div>

                  <div className="metric-card warn">
                    <div className="metric-card-top">
                      <span className="metric-card-icon"><FaUserSlash /></span>
                      <span className="metric-card-label">Taxa de falta</span>
                    </div>
                    <h2 className="metric-card-value">{pct(metrics.no_show_rate)}</h2>
                    <p className="metric-card-foot">
                      {metrics.no_show} {metrics.no_show === 1 ? "falta" : "faltas"}
                    </p>
                  </div>

                  <div className="metric-card warn">
                    <div className="metric-card-top">
                      <span className="metric-card-icon"><FaBan /></span>
                      <span className="metric-card-label">Taxa de cancelamento</span>
                    </div>
                    <h2 className="metric-card-value">{pct(metrics.cancellation_rate)}</h2>
                    <p className="metric-card-foot">
                      {metrics.cancelled} cancelados · {metrics.cancelled_by_client} cliente
                      {" / "}{metrics.cancelled_by_reception} recepção
                    </p>
                  </div>

                  <div className="metric-card">
                    <div className="metric-card-top">
                      <span className="metric-card-icon"><FaMoneyBillWave /></span>
                      <span className="metric-card-label">Receita realizada</span>
                    </div>
                    <h2 className="metric-card-value">{brl(metrics.realized_revenue)}</h2>
                    <p className="metric-card-foot">
                      de {brl(metrics.expected_revenue)} previstos
                    </p>
                  </div>
                </div>

                <div className="dashboard-charts-grid two-col">
                  <div className="dashboard-chart-card">
                    <h3 className="dashboard-chart-title">Realizado vs. previsto</h3>
                    <p className="dashboard-chart-subtitle">faturamento no período</p>

                    <div className="rvp-row">
                      <span className="rvp-label">Realizado</span>
                      <div className="rvp-bar">
                        <div
                          className="rvp-fill realized"
                          style={{
                            width: `${metrics.expected_revenue
                              ? (metrics.realized_revenue / metrics.expected_revenue) * 100
                              : 0}%`,
                          }}
                        />
                      </div>
                      <span className="rvp-value">{brl(metrics.realized_revenue)}</span>
                    </div>

                    <div className="rvp-row">
                      <span className="rvp-label">Previsto</span>
                      <div className="rvp-bar">
                        <div className="rvp-fill expected" style={{ width: "100%" }} />
                      </div>
                      <span className="rvp-value">{brl(metrics.expected_revenue)}</span>
                    </div>
                  </div>

                  <div className="dashboard-chart-card">
                    <h3 className="dashboard-chart-title">Receita por serviço</h3>
                    <p className="dashboard-chart-subtitle">atendimentos concluídos</p>
                    {metrics.revenue_by_service.length === 0 ? (
                      <div className="empty-state">Nenhuma receita realizada no período</div>
                    ) : (
                      <ResponsiveContainer width="100%" height={280}>
                        <BarChart
                          layout="vertical"
                          data={metrics.revenue_by_service}
                          margin={{ left: 8, right: 16 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                          <XAxis type="number" tickFormatter={(v) => `R$ ${v}`} />
                          <YAxis
                            type="category"
                            dataKey="service_name"
                            width={120}
                            tick={{ fontSize: 13 }}
                          />
                          <Tooltip formatter={(value) => brl(value)} />
                          <Bar dataKey="revenue" fill="#6d28d9" radius={[0, 8, 8, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* KPIs DO MÊS / TEMPO REAL */}
        <div className="dashboard-grid">

          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">Mês</p>
                <h2 className="dashboard-card-value">{brl(kpis.month_revenue)}</h2>
              </div>
              <div className="dashboard-icon"><FaMoneyBillWave /></div>
            </div>
            <div className="dashboard-card-footer">Receita do mês atual</div>
          </div>

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

          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">Crescimento</p>
                <h2 className={`dashboard-card-value ${kpis.monthly_growth >= 0 ? "positive" : "negative"}`}>
                  {kpis.monthly_growth >= 0 ? "↑" : "↓"}{" "}
                  {Math.abs(kpis.monthly_growth).toFixed(1)}%
                </h2>
              </div>
              <div className="dashboard-icon"><FaChartLine /></div>
            </div>
            <div className="dashboard-card-footer">Comparado ao mês anterior</div>
          </div>

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

          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">Agendamentos Hoje</p>
                <h2 className="dashboard-card-value">{kpis.today_appointments}</h2>
              </div>
              <div className="dashboard-icon"><FaCalendarCheck /></div>
            </div>
            <div className="dashboard-card-footer">{brl(kpis.today_revenue)} previstos hoje</div>
          </div>

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

          <div className="dashboard-card">
            <div className="dashboard-card-top">
              <div>
                <p className="dashboard-card-title">{term.plural}</p>
                <h2 className="dashboard-card-value">{kpis.total_clients}</h2>
              </div>
              <div className="dashboard-icon"><FaUsers /></div>
            </div>
            <div className="dashboard-card-footer">
              +{kpis.new_clients_month} novos este mês
            </div>
          </div>

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

        </div>

        {/* GRÁFICOS */}
        <div className="dashboard-charts-grid two-col">
          <div className="dashboard-chart-card">
            <h3 className="dashboard-chart-title">Agendamentos por Dia da Semana</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.weekly_appointments}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="day" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="agendamentos" fill="#6d28d9" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="dashboard-chart-card">
            <h3 className="dashboard-chart-title">Faturamento Últimos 6 Meses</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={stats.monthly_revenue_chart}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => brl(value)} />
                <Line
                  type="monotone"
                  dataKey="revenue"
                  stroke="#6d28d9"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* LISTAS */}
        <div className="dashboard-charts-grid two-col">

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
                    <span>{appointment.service} · {appointment.professional}</span>
                  </div>
                </div>
              ))
            )}
          </div>

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
                    <span>{appointment.service} · {appointment.professional}</span>
                  </div>
                </div>
              ))
            )}
          </div>

        </div>

        <div className="dashboard-charts-grid">

          <div className="dashboard-chart-card">
            <h3 className="dashboard-chart-title">Serviços Mais Realizados</h3>
            <p className="dashboard-chart-subtitle">no período selecionado</p>
            {stats.top_services.length === 0 ? (
              <div className="empty-state">Nenhum serviço no período</div>
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

          <div className="dashboard-chart-card">
            <h3 className="dashboard-chart-title">{term.plural} Sem Retorno</h3>
            <p className="dashboard-chart-subtitle">há mais de 90 dias</p>
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
