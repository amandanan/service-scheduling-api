import { useEffect, useState } from "react";
import api from "../services/api";
import Navbar from "../components/Navbar";

import {
  FaUsers,
  FaEdit,
  FaTrash,
  FaPlus,
  FaIdCard,
  FaEnvelope,
  FaBirthdayCake,
  FaPhone,
} from "react-icons/fa";

import "../styles/clients.css";

export default function Clients() {
  const [clients, setClients] = useState([]);

  const [fullName, setFullName] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [cpf, setCpf] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");

  const [editingId, setEditingId] = useState(null);

  async function loadClients() {
    try {
      const response = await api.get("/clients");
      setClients(response.data);

    } catch (error) {
      console.error("Erro ao carregar clientes");
    }
  }

  useEffect(() => {
    loadClients();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();

    const clientData = {
      full_name: fullName,
      birth_date: birthDate,
      cpf,
      phone,
      email,
    };

    try {

      if (editingId) {
        await api.put(
          `/clients/${editingId}`,
          clientData
        );

        setEditingId(null);

      } else {
        await api.post("/clients", clientData);
      }

      clearForm();
      loadClients();

    } catch (error) {
      console.error("Erro ao salvar cliente");
    }
  }

  function handleEdit(client) {
    setEditingId(client.id);

    setFullName(client.full_name);
    setBirthDate(client.birth_date);
    setCpf(client.cpf);
    setPhone(client.phone);
    setEmail(client.email);
  }

  async function handleDelete(id) {
    const confirmDelete = window.confirm(
      "Deseja realmente excluir este cliente?"
    );

    if (!confirmDelete) return;

    try {
      await api.delete(`/clients/${id}`);
      loadClients();

    } catch (error) {
      console.error("Erro ao excluir cliente");
    }
  }

  function clearForm() {
    setFullName("");
    setBirthDate("");
    setCpf("");
    setPhone("");
    setEmail("");
  }

  return (
    <div className="clients-page">
      <Navbar />

      <div className="clients-container">

        <div className="clients-card">

          <h1 className="clients-title">
            <FaUsers />
            Clientes
          </h1>

          <form
            onSubmit={handleSubmit}
            className="clients-form"
          >

            <input
              type="text"
              placeholder="Nome completo"
              value={fullName}
              onChange={(e) =>
                setFullName(e.target.value)
              }
              required
            />

            <input
              type="date"
              value={birthDate}
              onChange={(e) =>
                setBirthDate(e.target.value)
              }
              required
            />

            <input
              type="text"
              placeholder="CPF"
              value={cpf}
              onChange={(e) =>
                setCpf(e.target.value)
              }
              required
            />

            <input
              type="text"
              placeholder="Telefone"
              value={phone}
              onChange={(e) =>
                setPhone(e.target.value)
              }
              required
            />

            <input
              type="email"
              placeholder="E-mail"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              required
            />

            <button
              type="submit"
              className="primary-btn"
            >
              {editingId
                ? <FaEdit />
                : <FaPlus />
              }

              {editingId
                ? "Atualizar"
                : "Cadastrar"}
            </button>

          </form>

          <table className="clients-table">

            <thead>
              <tr>
                <th>ID</th>
                <th>Nome</th>
                <th>CPF</th>
                <th>Telefone</th>
                <th>E-mail</th>
                <th>Nascimento</th>
                <th>Ações</th>
              </tr>
            </thead>

            <tbody>

              {clients.map((client) => (

                <tr key={client.id}>

                  <td>{client.id}</td>

                  <td>
                    <div className="info-cell">
                      <FaUsers />
                      {client.full_name}
                    </div>
                  </td>

                  <td>
                    <div className="info-cell">
                      <FaIdCard />
                      {client.cpf}
                    </div>
                  </td>

                  <td>
                    <div className="info-cell">
                      <FaPhone />
                      {client.phone}
                    </div>
                  </td>

                  <td>
                    <div className="info-cell">
                      <FaEnvelope />
                      {client.email}
                    </div>
                  </td>

                  <td>
                    <div className="info-cell">
                      <FaBirthdayCake />
                      {client.birth_date}
                    </div>
                  </td>

                  <td>

                    <div className="actions">

                      <button
                        className="edit-btn"
                        onClick={() =>
                          handleEdit(client)
                        }
                      >
                        <FaEdit />
                        Editar
                      </button>

                      <button
                        className="delete-btn"
                        onClick={() =>
                          handleDelete(client.id)
                        }
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