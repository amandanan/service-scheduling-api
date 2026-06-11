import { useEffect, useState } from "react";

import {
  getProfessionals,
  createProfessional,
  updateProfessional,
  deleteProfessional,
} from "../services/api";

import Navbar from "../components/Navbar";

import { toast } from "react-toastify";

import {
  FaUserTie,
  FaEdit,
  FaTrash,
  FaPlus,
} from "react-icons/fa";

import "../styles/services.css";

export default function Professionals() {

  const [professionals, setProfessionals] = useState([]);

  const [name, setName] = useState("");

  const [editingId, setEditingId] = useState(null);


  async function loadProfessionals() {

    try {

      const data = await getProfessionals();

      setProfessionals(data);

    } catch (error) {

      console.error(error);

      toast.error("Erro ao carregar profissionais");
    }
  }


  useEffect(() => {
    loadProfessionals();
  }, []);


  function clearForm() {
    setEditingId(null);
    setName("");
  }


  async function handleSubmit(e) {

    e.preventDefault();

    if (!name.trim()) {
      toast.error("Informe o nome do profissional");
      return;
    }

    try {

      if (editingId) {

        const current = professionals.find((p) => p.id === editingId);

        await updateProfessional(editingId, {
          name: name.trim(),
          is_active: current ? current.is_active : true,
        });

        toast.success("Profissional atualizado");

      } else {

        await createProfessional({ name: name.trim() });

        toast.success("Profissional cadastrado");
      }

      clearForm();

      loadProfessionals();

    } catch (error) {

      console.error(error);

      toast.error("Erro ao salvar profissional");
    }
  }


  function handleEdit(professional) {
    setEditingId(professional.id);
    setName(professional.name);
  }


  async function handleToggleActive(professional) {

    try {

      await updateProfessional(professional.id, {
        name: professional.name,
        is_active: !professional.is_active,
      });

      loadProfessionals();

    } catch (error) {

      console.error(error);

      toast.error("Erro ao atualizar profissional");
    }
  }


  async function handleDelete(id) {

    const confirmDelete = window.confirm(
      "Deseja realmente excluir este profissional?"
    );

    if (!confirmDelete) return;

    try {

      await deleteProfessional(id);

      toast.success("Profissional removido");

      loadProfessionals();

    } catch (error) {

      console.error(error);

      toast.error(
        "Erro ao excluir profissional. Verifique se há agendamentos vinculados."
      );
    }
  }


  return (

    <div className="services-page">

      <Navbar />

      <div className="services-container">

        <div className="services-card">

          <h1 className="services-title">

            <FaUserTie />

            Profissionais

          </h1>


          <form
            onSubmit={handleSubmit}
            className="services-form"
          >

            <input
              type="text"
              placeholder="Nome do profissional"
              value={name}
              onChange={(e) => setName(e.target.value)}
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

            {editingId && (
              <button
                type="button"
                className="secondary-btn"
                onClick={clearForm}
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
                <th>Status</th>
                <th>Ações</th>
              </tr>

            </thead>


            <tbody>

              {professionals.length > 0 ? (

                professionals.map((professional) => (

                  <tr key={professional.id}>

                    <td>{professional.id}</td>

                    <td>{professional.name}</td>

                    <td>

                      <button
                        type="button"
                        className={
                          professional.is_active
                            ? "edit-btn"
                            : "secondary-btn"
                        }
                        onClick={() =>
                          handleToggleActive(professional)
                        }
                      >
                        {professional.is_active ? "Ativo" : "Inativo"}
                      </button>

                    </td>

                    <td>

                      <div className="actions">

                        <button
                          className="edit-btn"
                          onClick={() => handleEdit(professional)}
                        >
                          <FaEdit />
                          Editar
                        </button>

                        <button
                          className="delete-btn"
                          onClick={() => handleDelete(professional.id)}
                        >
                          <FaTrash />
                          Excluir
                        </button>

                      </div>

                    </td>

                  </tr>

                ))

              ) : (

                <tr>
                  <td
                    colSpan="4"
                    style={{ textAlign: "center", padding: "20px" }}
                  >
                    Nenhum profissional cadastrado
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
