import { useEffect, useState } from "react";
import api from "../services/api";
import Navbar from "../components/Navbar";

export default function Services() {
  const [services, setServices] = useState([]);

  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [duration, setDuration] = useState("");

  async function loadServices() {
    try {
      const response = await api.get("/services");
      setServices(response.data);
    } catch (error) {
      console.error("Erro ao carregar serviços");
    }
  }

  useEffect(() => {
    loadServices();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();

    try {
      await api.post("/services", {
        name,
        price: Number(price),
        duration_minutes: Number(duration),
      });

      setName("");
      setPrice("");
      setDuration("");

      loadServices();
    } catch (error) {
      console.error("Erro ao cadastrar serviço");
    }
  }

  async function handleDelete(id) {
    try {
      await api.delete(`/services/${id}`);
      loadServices();
    } catch (error) {
      console.error("Erro ao excluir serviço");
    }
  }

  return (
    <div style={{ padding: "20px" }}>
      <Navbar />

      <h1>Serviços</h1>

      <form
        onSubmit={handleSubmit}
        style={{
          display: "flex",
          gap: "10px",
          marginBottom: "20px",
          flexWrap: "wrap",
        }}
      >
        <input
          type="text"
          placeholder="Nome do serviço"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

        <input
          type="number"
          placeholder="Preço"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          required
        />

        <input
          type="number"
          placeholder="Duração (min)"
          value={duration}
          onChange={(e) => setDuration(e.target.value)}
          required
        />

        <button type="submit">Cadastrar</button>
      </form>

      <table
        border="1"
        cellPadding="10"
        style={{
          width: "100%",
          borderCollapse: "collapse",
        }}
      >
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome</th>
            <th>Preço</th>
            <th>Duração</th>
            <th>Ações</th>
          </tr>
        </thead>

        <tbody>
          {services.map((service) => (
            <tr key={service.id}>
              <td>{service.id}</td>

              <td>{service.name}</td>

              <td>R$ {service.price}</td>

              <td>{service.duration_minutes} min</td>

              <td>
                <button
                  onClick={() => handleDelete(service.id)}
                >
                  Excluir
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}