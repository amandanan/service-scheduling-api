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
api.interceptors.response.use(

  (response) => response,

  (error) => {

    // token expirado / inválido
    if (
      error.response &&
      error.response.status === 401
    ) {

      localStorage.removeItem("token");

      window.location.href = "/login";
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


// PACKAGES

export async function getPackages() {

  const response = await api.get(
    "/packages/"
  );

  return response.data;
}


export async function createPackage(data) {

  const response = await api.post(
    "/packages/",
    data
  );

  return response.data;
}


export async function updatePackage(id, data) {

  const response = await api.put(
    `/packages/${id}`,
    data
  );

  return response.data;
}


export async function deletePackage(id) {

  await api.delete(`/packages/${id}`);
}


export async function purchasePackage(data) {

  const response = await api.post(
    "/packages/purchases",
    data
  );

  return response.data;
}


export async function getClientPackages(clientId) {

  const response = await api.get(
    "/packages/purchases",
    { params: { client_id: clientId } }
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


export async function submitReview(token, rating, comment) {

  const response = await api.post(
    `/manage/${token}/review`,
    { rating, comment }
  );

  return response.data;
}


// REVIEWS

export async function getReviews() {

  const response = await api.get(
    "/reviews/"
  );

  return response.data;
}


export default api;