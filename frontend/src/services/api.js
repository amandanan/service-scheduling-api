import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
});

export async function register(data) {
  const response = await api.post("/auth/register", data);

  return response.data;
}

export async function login(data) {
  const body = new URLSearchParams({
    username: data.email,
    password: data.password,
  });

  const response = await api.post("/auth/login", body, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  return response.data;
}

export async function getClients() {
  const response = await api.get("/clients");
  return response.data;
}

export async function createClient(data) {
  const response = await api.post("/clients", data);
  return response.data;
}

export async function deleteClient(id) {
  await api.delete(`/clients/${id}`);
}

export default api;
