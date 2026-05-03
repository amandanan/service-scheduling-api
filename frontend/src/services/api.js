const API_URL = "http://127.0.0.1:8000";

export async function register(data) {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.detail || "Erro ao cadastrar");
  }

  return result;
}

export async function login(data) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      username: data.email,
      password: data.password,
    }),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(result.detail || "E-mail ou senha inválidos");
  }

  return result;
} 
