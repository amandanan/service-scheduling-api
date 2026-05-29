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
  FaClock,
} from "react-icons/fa";

import "../styles/services.css";

export default function Services() {

  const [services, setServices] = useState([]);

  const [name, setName] = useState("");

  const [price, setPrice] = useState("");

  const [durationMinutes, setDurationMinutes] =
    useState("");

  const [editingId, setEditingId] =
    useState(null);


  async function loadServices() {

    try {

      const response =
        await api.get("/services/");

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

    if (!name.trim()) {

      toast.error(
        "Informe o nome do serviço"
      );

      return;
    }

    if (!price || Number(price) <= 0) {

      toast.error(
        "Informe um preço válido"
      );

      return;
    }

    if (
      !durationMinutes ||
      Number(durationMinutes) <= 0
    ) {

      toast.error(
        "Informe uma duração válida"
      );

      return;
    }


    const serviceData = {

      name: name.trim(),

      price: Number(price),

      duration_minutes:
        Number(durationMinutes),
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

      } else {

        await api.post(
          "/services/",
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

    setDurationMinutes(
      service.duration_minutes
    );
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

    setEditingId(null);

    setName("");

    setPrice("");

    setDurationMinutes("");
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
              onChange={(e) =>
                setName(e.target.value)
              }
              required
            />


            <input
              type="number"
              step="0.01"
              min="0"
              placeholder="Preço"
              value={price}
              onChange={(e) =>
                setPrice(e.target.value)
              }
              required
            />


            <input
              type="number"
              min="1"
              placeholder="Duração (min)"
              value={durationMinutes}
              onChange={(e) =>
                setDurationMinutes(
                  e.target.value
                )
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

                <th>Preço</th>

                <th>Duração</th>

                <th>Ações</th>

              </tr>

            </thead>


            <tbody>

              {services.length > 0 ? (

                services.map((service) => (

                  <tr key={service.id}>

                    <td>
                      {service.id}
                    </td>

                    <td>
                      {service.name}
                    </td>

                    <td>

                      <div className="price-cell">

                        <FaDollarSign />

                        R$ {" "}
                        {Number(
                          service.price
                        ).toFixed(2)}

                      </div>

                    </td>

                    <td>

                      <div className="duration-cell">

                        <FaClock />

                        {service.duration_minutes} min

                      </div>

                    </td>

                    <td>

                      <div className="actions">

                        <button
                          className="edit-btn"
                          onClick={() =>
                            handleEdit(service)
                          }
                        >

                          <FaEdit />

                          Editar

                        </button>


                        <button
                          className="delete-btn"
                          onClick={() =>
                            handleDelete(
                              service.id
                            )
                          }
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
                    colSpan="5"
                    style={{
                      textAlign: "center",
                      padding: "20px",
                    }}
                  >

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
