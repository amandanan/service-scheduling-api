import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
});

/* =========================
   INTERCEPTOR JWT
========================= */

api.interceptors.request.use((config) => {

  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization =
      `Bearer ${token}`;
  }

  return config;
});

/* =========================
   REGISTER
========================= */

export async function register(data) {

  const response = await api.post(
    "/auth/register",
    {
      full_name: data.full_name,
      birth_date: data.birth_date,
      cpf: data.cpf,
      phone: data.phone,
      email: data.email,
      password: data.password,
    }
  );

  return response.data;
}

/* =========================
   LOGIN
========================= */

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

/* =========================
   CLIENTS
========================= */

export async function getClients() {

  const response = await api.get("/clients");

  return response.data;
}

export async function createClient(data) {

  const response = await api.post(
    "/clients",
    {
      full_name: data.full_name,
      birth_date: data.birth_date,
      cpf: data.cpf,
      phone: data.phone,
      email: data.email,
    }
  );

  return response.data;
}

export async function updateClient(id, data) {

  const response = await api.put(
    `/clients/${id}`,
    {
      full_name: data.full_name,
      birth_date: data.birth_date,
      cpf: data.cpf,
      phone: data.phone,
      email: data.email,
    }
  );

  return response.data;
}

export async function deleteClient(id) {

  await api.delete(`/clients/${id}`);
}

export default api;