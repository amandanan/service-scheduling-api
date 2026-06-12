import { useEffect, useState } from "react";

import api from "../services/api";

import Navbar from "../components/Navbar";

import { formatCpf } from "../utils/format";

import "../styles/clients.css";

import {
  FaUser,
  FaEdit,
  FaTrash,
  FaPlus,
  FaPhone,
  FaEnvelope,
} from "react-icons/fa";

import { toast } from "react-toastify";

import { IMaskInput } from "react-imask";

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

      const response = await api.get("/clients/");

      setClients(response.data);

    } catch (error) {

      console.error(error);

      toast.error("Erro ao carregar clientes");
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

        toast.success("Cliente atualizado");

      } else {

        await api.post(
          "/clients/",
          clientData
        );

        toast.success("Cliente cadastrado");
      }

      clearForm();

      await loadClients();

    } catch (error) {

      console.error(error);

      const status = error.response?.status;

      if (status === 422) {
        toast.error("CPF inválido");
      } else if (status === 400) {
        toast.error(
          error.response?.data?.detail || "Não foi possível salvar o cliente"
        );
      } else {
        toast.error("Erro ao salvar cliente");
      }
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

      toast.success("Cliente removido");

      await loadClients();

    } catch (error) {

      console.error(error);

      toast.error("Erro ao excluir cliente");
    }
  }


  function clearForm() {

    setFullName("");
    setBirthDate("");
    setCpf("");
    setPhone("");
    setEmail("");
    setEditingId(null);
  }


  return (

    <div className="clients-page">

      <Navbar />

      <div className="clients-container">

        <div className="clients-card">

          <h1 className="clients-title">
            <FaUser />
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

          <IMaskInput
              mask="000.000.000-00"
              value={cpf}
              onAccept={(value) =>
                setCpf(value)
              }
              placeholder="CPF (opcional)"
              className="masked-input"
            />

           <IMaskInput
              mask="(00) 00000-0000"
              value={phone}
              onAccept={(value) =>
                setPhone(value)
              }
              placeholder="Telefone"
              className="masked-input"
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

              {editingId ? (
                <>
                  <FaEdit />
                  Atualizar
                </>
              ) : (
                <>
                  <FaPlus />
                  Cadastrar
                </>
              )}

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
                <th>Ações</th>
              </tr>

            </thead>


            <tbody>

              {clients.map((client) => (

                <tr key={client.id}>

                  <td>{client.id}</td>

                  <td>{client.full_name}</td>

                  <td>{formatCpf(client.cpf)}</td>

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

                    <div className="actions">

                      <button
                        onClick={() =>
                          handleEdit(client)
                        }
                        className="edit-btn"
                      >

                        <FaEdit />
                        Editar

                      </button>


                      <button
                        onClick={() =>
                          handleDelete(client.id)
                        }
                        className="delete-btn"
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