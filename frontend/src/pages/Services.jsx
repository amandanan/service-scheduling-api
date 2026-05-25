import { useEffect, useState } from "react";
import api from "../services/api";
import Navbar from "../components/Navbar";
import { toast } from "react-toastify";

import {
  FaTools,
  FaEdit,
  FaTrash,
  FaPlus,
  FaDollarSign,
} from "react-icons/fa";

import "../styles/services.css";

export default function Services() {
  const [services, setServices] = useState([]);

  const [name, setName] = useState("");
  const [price, setPrice] = useState("");

  const [editingId, setEditingId] = useState(null);

 async function loadServices() {

  try {

    const response = await api.get("/services");

    setServices(response.data);

  } catch (error) {

    console.error(error);

    toast.error(
      "Erro ao carregar serviços"
    );
  }
}

  useEffect(() => {
    loadServices();
  }, []);

  async function handleSubmit(e) {

  e.preventDefault();

  const serviceData = {
    name,
    price: Number(price),
  };

  try {

    if (editingId) {

      await api.put(
        `/services/${editingId}`,
        serviceData
      );

      toast.success(
        "Serviço atualizado"
      );

      setEditingId(null);

    } else {

      await api.post(
        "/services",
        serviceData
      );

      toast.success(
        "Serviço cadastrado"
      );
    }

    clearForm();

    loadServices();

  } catch (error) {

    console.error(error);

    toast.error(
      "Erro ao salvar serviço"
    );
  }
  }

  function handleEdit(service) {
    setEditingId(service.id);

    setName(service.name);
    setPrice(service.price);
  }

  async function handleDelete(id) {

  const confirmDelete = window.confirm(
    "Deseja realmente excluir este serviço?"
  );

  if (!confirmDelete) return;

  try {

    await api.delete(
      `/services/${id}`
    );

    toast.success(
      "Serviço removido"
    );

    loadServices();

  } catch (error) {

    console.error(error);

    toast.error(
      "Erro ao excluir serviço"
    );
  }
  }
  function clearForm() {
    setName("");
    setPrice("");
  }

  return (

    <div className="services-page">
      <Navbar />

      <div className="services-container">

        <div className="services-card">

          <h1 className="services-title">
            <FaTools />
            Serviços
          </h1>

          <form
            onSubmit={handleSubmit}
            className="services-form"
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

            <button
              type="submit"
              className="primary-btn"
            >
              {editingId ? <FaEdit /> : <FaPlus />}
              {editingId ? "Atualizar" : "Cadastrar"}
            </button>

            {editingId && (
              <button
                type="button"
                className="secondary-btn"
                onClick={() => {
                  setEditingId(null);
                  clearForm();
                }}
              >
                Cancelar
              </button>
            )}
          </form>

          <table className="services-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nome</th>
                <th>Preço</th>
                <th>Ações</th>
              </tr>
            </thead>

            <tbody>
              {services.map((service) => (
                <tr key={service.id}>
                  <td>{service.id}</td>

                  <td>{service.name}</td>

                  <td>
                    <div className="price-cell">
                      <FaDollarSign />
                      R$ {service.price}
                    </div>
                  </td>

                  <td>
                    <div className="actions">
                      <button
                        className="edit-btn"
                        onClick={() => handleEdit(service)}
                      >
                        <FaEdit />
                        Editar
                      </button>

                      <button
                        className="delete-btn"
                        onClick={() => handleDelete(service.id)}
                      >
                        <FaTrash />
                        Excluir
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>

          </table>
        </div>
      </div>
    </div>
  );
}