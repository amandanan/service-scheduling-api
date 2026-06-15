import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
});


// INTERCEPTOR REQUEST
api.interceptors.request.use(
  (config) => {

    const token = localStorage.getItem("token");

    if (token) {
      config.headers.Authorization =
        `Bearer ${token}`;
    }

    return config;
  },

  (error) => {
    return Promise.reject(error);
  }
);


// INTERCEPTOR RESPONSE
// On a 401 we try to silently refresh the access token once before giving up,
// so a short-lived access token doesn't log the user out mid-session.

let refreshPromise = null;

async function refreshAccessToken() {
  const refreshToken = localStorage.getItem("refresh_token");

  if (!refreshToken) {
    return null;
  }

  try {
    const response = await axios.post(`${API_URL}/auth/refresh`, {
      refresh_token: refreshToken,
    });

    const newToken = response.data.access_token;
    localStorage.setItem("token", newToken);
    return newToken;

  } catch {
    return null;
  }
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("role");
  window.location.href = "/login";
}

api.interceptors.response.use(

  (response) => response,

  async (error) => {

    const original = error.config;
    const status = error.response?.status;

    const canRetry =
      status === 401 &&
      original &&
      !original._retry &&
      !original.url?.includes("/auth/refresh");

    if (canRetry) {
      original._retry = true;

      // de-duplicate concurrent refreshes
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
      }

      const newToken = await refreshPromise;

      if (newToken) {
        original.headers.Authorization = `Bearer ${newToken}`;
        return api(original);
      }

      logout();
    }

    return Promise.reject(error);
  }
);


// AUTH

export async function register(data) {

  const response = await api.post(
    "/auth/register",
    data
  );

  return response.data;
}


export async function login(data) {

  const body = new URLSearchParams({
    username: data.email,
    password: data.password,
  });

  const response = await api.post(
    "/auth/login",
    body,
    {
      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
    }
  );

  return response.data;
}


export async function getMe() {

  const response = await api.get(
    "/auth/me"
  );

  return response.data;
}


export async function forgotPassword(email) {

  const response = await api.post(
    "/auth/forgot-password",
    { email }
  );

  return response.data;
}


export async function resetPassword(token, newPassword) {

  const response = await api.post(
    "/auth/reset-password",
    { token, new_password: newPassword }
  );

  return response.data;
}


// CLIENTS

export async function getClients() {

  const response = await api.get(
    "/clients/"
  );

  return response.data;
}


export async function createClient(data) {

  const response = await api.post(
    "/clients/",
    data
  );

  return response.data;
}


export async function deleteClient(id) {

  await api.delete(`/clients/${id}`);
}


// SERVICES

export async function getServices() {

  const response = await api.get(
    "/services/"
  );

  return response.data;
}


export async function createService(data) {

  const response = await api.post(
    "/services/",
    data
  );

  return response.data;
}


// APPOINTMENTS

export async function getAppointments() {

  const response = await api.get(
    "/appointments/"
  );

  return response.data;
}


export async function createAppointment(data) {

  const response = await api.post(
    "/appointments/",
    data
  );

  return response.data;
}


// PROFESSIONALS

export async function getProfessionals() {

  const response = await api.get(
    "/professionals/"
  );

  return response.data;
}


export async function createProfessional(data) {

  const response = await api.post(
    "/professionals/",
    data
  );

  return response.data;
}


export async function updateProfessional(id, data) {

  const response = await api.put(
    `/professionals/${id}`,
    data
  );

  return response.data;
}


export async function deleteProfessional(id) {

  await api.delete(`/professionals/${id}`);
}


// WORKING HOURS (per professional)

export async function getWorkingHours(professionalId) {

  const response = await api.get(
    `/professionals/${professionalId}/working-hours`
  );

  return response.data;
}


export async function updateWorkingHours(professionalId, days) {

  const response = await api.put(
    `/professionals/${professionalId}/working-hours`,
    { days }
  );

  return response.data;
}


// TIME BLOCKS (folgas e bloqueios)

export async function getTimeBlocks(professionalId) {

  const response = await api.get(
    "/blocks/",
    { params: { professional_id: professionalId } }
  );

  return response.data;
}


export async function createTimeBlock(data) {

  const response = await api.post(
    "/blocks/",
    data
  );

  return response.data;
}


export async function deleteTimeBlock(id) {

  await api.delete(`/blocks/${id}`);
}


// PUBLIC BOOKING

export async function getPublicBusiness(slug) {

  const response = await api.get(
    `/public/${slug}/`
  );

  return response.data;
}


export async function getPublicServices(slug) {

  const response = await api.get(
    `/public/${slug}/services`
  );

  return response.data;
}


export async function getPublicProfessionals(slug) {

  const response = await api.get(
    `/public/${slug}/professionals`
  );

  return response.data;
}


export async function getPublicReviews(slug) {

  const response = await api.get(
    `/public/${slug}/reviews`
  );

  return response.data;
}


export async function getPublicAvailableSlots(slug, date, serviceId, professionalId) {

  const response = await api.get(
    `/public/${slug}/available-slots`,
    { params: { date, service_id: serviceId, professional_id: professionalId } }
  );

  return response.data;
}


export async function createPublicBooking(slug, data) {

  const response = await api.post(
    `/public/${slug}/appointments`,
    data
  );

  return response.data;
}


// MANAGE BOOKING (by public token, no auth)

export async function getManagedAppointment(token) {

  const response = await api.get(
    `/manage/${token}`
  );

  return response.data;
}


export async function getManageAvailableSlots(token, date) {

  const response = await api.get(
    `/manage/${token}/available-slots`,
    { params: { date } }
  );

  return response.data;
}


export async function cancelManagedAppointment(token) {

  const response = await api.post(
    `/manage/${token}/cancel`
  );

  return response.data;
}


export async function rescheduleManagedAppointment(token, scheduledAt) {

  const response = await api.post(
    `/manage/${token}/reschedule`,
    { scheduled_at: scheduledAt }
  );

  return response.data;
}


export async function confirmManagedAppointment(token) {

  const response = await api.post(
    `/manage/${token}/confirm`
  );

  return response.data;
}


export async function submitReview(token, rating, comment) {

  const response = await api.post(
    `/manage/${token}/review`,
    { rating, comment }
  );

  return response.data;
}


// APPOINTMENT STATUS (owner)

export async function updateAppointmentStatus(id, status) {

  const response = await api.patch(
    `/appointments/${id}/status`,
    { status }
  );

  return response.data;
}


// PROFESSIONAL SELF-SERVICE (role="professional")

export async function getMyAppointments() {
  const response = await api.get("/professionals/me/appointments");
  return response.data;
}

export async function getMyWorkingHours() {
  const response = await api.get("/professionals/me/working-hours");
  return response.data;
}

export async function updateMyWorkingHours(days) {
  const response = await api.put("/professionals/me/working-hours", { days });
  return response.data;
}

export async function getMyBlocks() {
  const response = await api.get("/professionals/me/blocks");
  return response.data;
}

export async function createMyBlock(data) {
  const response = await api.post("/professionals/me/blocks", data);
  return response.data;
}

export async function deleteMyBlock(id) {
  await api.delete(`/professionals/me/blocks/${id}`);
}

export async function updateService(id, data) {
  const response = await api.put(`/services/${id}`, data);
  return response.data;
}

export async function deleteService(id) {
  await api.delete(`/services/${id}`);
}


// REVIEWS

export async function getReviews() {

  const response = await api.get(
    "/reviews/"
  );

  return response.data;
}


// DASHBOARD

export async function getDashboardStats(filters = {}) {

  const params = {};

  if (filters.professionalId) {
    params.professional_id = filters.professionalId;
  }

  if (filters.startDate) {
    params.start_date = filters.startDate;
  }

  if (filters.endDate) {
    params.end_date = filters.endDate;
  }

  const response = await api.get("/dashboard/stats", { params });

  return response.data;
}


export async function getDashboardMetrics(filters = {}) {

  const params = {};

  if (filters.startDate) {
    params.start_date = filters.startDate;
  }

  if (filters.endDate) {
    params.end_date = filters.endDate;
  }

  const response = await api.get("/dashboard/metrics", { params });

  return response.data;
}


function _downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export async function downloadReport(filters = {}) {
  const params = {};
  if (filters.startDate) params.start_date = filters.startDate;
  if (filters.endDate) params.end_date = filters.endDate;

  const response = await api.get("/dashboard/report.pdf", {
    params,
    responseType: "blob",
  });
  _downloadBlob(response.data, "relatorio.pdf");
}

export async function downloadCsv(filters = {}) {
  const params = {};
  if (filters.startDate) params.start_date = filters.startDate;
  if (filters.endDate) params.end_date = filters.endDate;

  const response = await api.get("/dashboard/export.csv", {
    params,
    responseType: "blob",
  });
  _downloadBlob(response.data, "dados.csv");
}


// SETTINGS

export async function getSettings() {

  const response = await api.get("/settings/");

  return response.data;
}


export async function updateSettings(data) {

  const response = await api.put("/settings/", data);

  return response.data;
}


// STAFF (team members) — owner only

export async function getStaff() {

  const response = await api.get("/staff/");

  return response.data;
}


export async function createStaff(data) {

  const response = await api.post("/staff/", data);

  return response.data;
}


export async function deleteStaff(id) {

  await api.delete(`/staff/${id}`);
}


export default api;