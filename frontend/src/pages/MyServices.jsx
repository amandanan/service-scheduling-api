import { useEffect, useState } from "react";
import { toast } from "react-toastify";

import {
  getServices,
  createService,
  updateService,
  deleteService,
} from "../services/api";

import Navbar from "../components/Navbar";

import { FaTools, FaPlus, FaEdit, FaBan } from "react-icons/fa";

import "../styles/services.css";


export default function MyServices() {

  const [services, setServices] = useState([]);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [durationMinutes, setDurationMinutes] = useState("");
  const [price, setPrice] = useState("");
  const [editingId, setEditingId] = useState(null);


  async function loadServices() {
    try {
      setServices(await getServices());
    } catch (error) {
      console.error(error);
      toast.error("Erro ao carregar serviços");
    }
  }


  useEffect(() => {
    loadServices();
  }, []);


  function clearForm() {
    setEditingId(null);
    setName("");
    setDescription("");
    setDurationMinutes("");
    setPrice("");
  }


  async function handleSubmit(e) {
    e.preventDefault();

    if (!name.trim()) {
      toast.error("Informe o nome do serviço");
      return;
    }
    if (!durationMinutes || Number(durationMinutes) <= 0) {
      toast.error("Informe a duração em minutos");
      return;
    }
    if (price === "" || Number(price) < 0) {
      toast.error("Informe um preço válido");
      return;
    }

    const data = {
      name: name.trim(),
      description: description.trim() || null,
      duration_minutes: Number(durationMinutes),
      price: Number(price),
    };

    try {
      if (editingId) {
        await updateService(editingId, { ...data, is_active: true });
        toast.success("Serviço atualizado");
      } else {
        await createService(data);
        toast.success("Serviço criado");
      }
      clearForm();
      loadServices();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao salvar serviço");
    }
  }


  function handleEdit(service) {
    setEditingId(service.id);
    setName(service.name);
    setDescription(service.description || "");
    setDurationMinutes(service.duration_minutes);
    setPrice(service.price);
  }


  async function handleDeactivate(id) {
    if (!window.confirm("Inativar este serviço? Ele deixará de aparecer no agendamento.")) return;
    try {
      await deleteService(id);
      toast.success("Serviço inativado");
      loadServices();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao inativar serviço");
    }
  }


  return (
    <div className="services-page">

      <Navbar />

      <div className="services-container">

        <div className="services-card">

          <h1 className="services-title">
            <FaTools />
            Meus Serviços
          </h1>

          <form onSubmit={handleSubmit} className="services-form">
            <input
              type="text"
              placeholder="Nome do serviço"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
            <input
              type="text"
              placeholder="Descrição (opcional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            <input
              type="number"
              min="1"
              placeholder="Duração (min)"
              value={durationMinutes}
              onChange={(e) => setDurationMinutes(e.target.value)}
              required
            />
            <input
              type="number"
              step="0.01"
              min="0"
              placeholder="Preço"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              required
            />
            <button type="submit" className="primary-btn">
              {editingId ? <><FaEdit /> Atualizar</> : <><FaPlus /> Adicionar</>}
            </button>
            {editingId && (
              <button type="button" className="secondary-btn" onClick={clearForm}>
                Cancelar
              </button>
            )}
          </form>

          <table className="services-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Duração</th>
                <th>Preço</th>
                <th>Status</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {services.length > 0 ? (
                services.map((s) => (
                  <tr key={s.id}>
                    <td>{s.name}</td>
                    <td>{s.duration_minutes} min</td>
                    <td>R$ {Number(s.price).toFixed(2)}</td>
                    <td>
                      <span className={`agenda-status ${s.is_active ? "confirmed" : "no_show"}`}>
                        {s.is_active ? "Ativo" : "Inativo"}
                      </span>
                    </td>
                    <td>
                      <div className="actions">
                        <button className="edit-btn" onClick={() => handleEdit(s)}>
                          <FaEdit />
                          Editar
                        </button>
                        {s.is_active && (
                          <button className="delete-btn" onClick={() => handleDeactivate(s.id)}>
                            <FaBan />
                            Inativar
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" style={{ textAlign: "center", padding: "20px" }}>
                    Nenhum serviço cadastrado
                  </td>
                </tr>
              )}
            </tbody>
          </table>

        </div>

      </div>

    </div>
  );
}
