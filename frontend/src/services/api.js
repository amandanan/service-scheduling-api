import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

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


export default api;