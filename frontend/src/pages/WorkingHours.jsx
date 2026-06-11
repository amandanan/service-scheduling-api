import { useEffect, useState } from "react";

import {
  getWorkingHours,
  updateWorkingHours,
} from "../services/api";

import Navbar from "../components/Navbar";

import { toast } from "react-toastify";

import { FaClock, FaSave } from "react-icons/fa";

import "../styles/services.css";

const WEEKDAY_LABELS = [
  "Segunda-feira",
  "Terça-feira",
  "Quarta-feira",
  "Quinta-feira",
  "Sexta-feira",
  "Sábado",
  "Domingo",
];

export default function WorkingHours() {

  const [days, setDays] = useState([]);


  async function loadWorkingHours() {

    try {

      const response = await getWorkingHours();

      const sorted = [...response].sort(
        (a, b) => a.weekday - b.weekday
      );

      setDays(sorted);

    } catch (error) {

      console.error(error);

      toast.error(
        "Erro ao carregar horário de funcionamento"
      );
    }
  }


  useEffect(() => {
    loadWorkingHours();
  }, []);


  function handleChange(weekday, field, value) {

    setDays((current) =>
      current.map((day) =>
        day.weekday === weekday
          ? { ...day, [field]: value }
          : day
      )
    );
  }


  async function handleSubmit(e) {

    e.preventDefault();

    try {

      const payload = days.map((day) => ({
        weekday: day.weekday,
        start_time: day.start_time,
        end_time: day.end_time,
        is_closed: day.is_closed,
      }));

      const response = await updateWorkingHours(payload);

      const sorted = [...response].sort(
        (a, b) => a.weekday - b.weekday
      );

      setDays(sorted);

      toast.success("Horário de funcionamento atualizado");

    } catch (error) {

      console.error(error);

      toast.error(
        "Erro ao salvar horário de funcionamento"
      );
    }
  }


  return (

    <div className="services-page">

      <Navbar />

      <div className="services-container">

        <div className="services-card">

          <h1 className="services-title">

            <FaClock />

            Horário de Funcionamento

          </h1>


          <form onSubmit={handleSubmit}>

            <table className="services-table">

              <thead>

                <tr>

                  <th>Dia</th>

                  <th>Abre</th>

                  <th>Fecha</th>

                  <th>Fechado</th>

                </tr>

              </thead>


              <tbody>

                {days.map((day) => (

                  <tr key={day.weekday}>

                    <td>
                      {WEEKDAY_LABELS[day.weekday]}
                    </td>

                    <td>

                      <input
                        type="time"
                        value={day.start_time?.slice(0, 5) || ""}
                        disabled={day.is_closed}
                        onChange={(e) =>
                          handleChange(
                            day.weekday,
                            "start_time",
                            e.target.value
                          )
                        }
                      />

                    </td>

                    <td>

                      <input
                        type="time"
                        value={day.end_time?.slice(0, 5) || ""}
                        disabled={day.is_closed}
                        onChange={(e) =>
                          handleChange(
                            day.weekday,
                            "end_time",
                            e.target.value
                          )
                        }
                      />

                    </td>

                    <td>

                      <input
                        type="checkbox"
                        checked={day.is_closed}
                        onChange={(e) =>
                          handleChange(
                            day.weekday,
                            "is_closed",
                            e.target.checked
                          )
                        }
                      />

                    </td>

                  </tr>

                ))}

              </tbody>

            </table>


            <button
              type="submit"
              className="primary-btn"
              style={{ marginTop: "20px" }}
            >

              <FaSave />

              Salvar

            </button>

          </form>

        </div>

      </div>

    </div>
  );
}
