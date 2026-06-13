import { useEffect, useState } from "react";
import { toast } from "react-toastify";
import { IMaskInput } from "react-imask";

import { getStaff, createStaff, deleteStaff } from "../services/api";

import Navbar from "../components/Navbar";

import { FaUserShield, FaPlus, FaTrash } from "react-icons/fa";

import "../styles/services.css";

export default function Staff() {

  const [staff, setStaff] = useState([]);

  const [fullName, setFullName] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [cpf, setCpf] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [saving, setSaving] = useState(false);


  async function loadStaff() {
    try {
      const data = await getStaff();
      setStaff(data);
    } catch (error) {
      console.error(error);
      toast.error("Erro ao carregar a equipe");
    }
  }


  useEffect(() => {
    loadStaff();
  }, []);


  function clearForm() {
    setFullName("");
    setBirthDate("");
    setCpf("");
    setPhone("");
    setEmail("");
    setPassword("");
  }


  async function handleSubmit(e) {
    e.preventDefault();

    if (password.length < 6) {
      toast.error("A senha deve ter ao menos 6 caracteres");
      return;
    }

    setSaving(true);

    try {
      await createStaff({
        full_name: fullName,
        birth_date: birthDate,
        cpf,
        phone,
        email,
        password,
      });

      toast.success("Membro da equipe adicionado");
      clearForm();
      loadStaff();

    } catch (error) {
      const status = error.response?.status;
      if (status === 422) {
        toast.error("CPF inválido");
      } else if (status === 400) {
        toast.error(error.response?.data?.detail || "Não foi possível adicionar");
      } else {
        toast.error("Erro ao adicionar membro");
      }
    } finally {
      setSaving(false);
    }
  }


  async function handleDelete(id) {
    if (!window.confirm("Remover este membro da equipe?")) return;

    try {
      await deleteStaff(id);
      toast.success("Membro removido");
      loadStaff();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao remover membro");
    }
  }


  return (
    <div className="services-page">

      <Navbar />

      <div className="services-container">

        <div className="services-card">

          <h1 className="services-title">
            <FaUserShield />
            Equipe
          </h1>

          <p className="settings-hint" style={{ marginBottom: "18px" }}>
            Adicione recepcionistas ou colaboradores. Eles acessam a agenda,
            clientes e serviços do seu negócio, mas não gerenciam a equipe nem
            as configurações.
          </p>

          <form onSubmit={handleSubmit} className="services-form">

            <input
              type="text"
              placeholder="Nome completo"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />

            <input
              type="date"
              value={birthDate}
              onChange={(e) => setBirthDate(e.target.value)}
              required
            />

            <IMaskInput
              mask="000.000.000-00"
              value={cpf}
              onAccept={(value) => setCpf(value)}
              placeholder="CPF"
              className="masked-input"
            />

            <IMaskInput
              mask="(00) 00000-0000"
              value={phone}
              onAccept={(value) => setPhone(value)}
              placeholder="Telefone"
              className="masked-input"
            />

            <input
              type="email"
              placeholder="E-mail (login)"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <input
              type="password"
              placeholder="Senha"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <button type="submit" className="primary-btn" disabled={saving}>
              <FaPlus />
              {saving ? "Adicionando..." : "Adicionar"}
            </button>

          </form>

          <table className="services-table">

            <thead>
              <tr>
                <th>Nome</th>
                <th>E-mail</th>
                <th>Telefone</th>
                <th>Ações</th>
              </tr>
            </thead>

            <tbody>

              {staff.length > 0 ? (

                staff.map((member) => (
                  <tr key={member.id}>
                    <td>{member.full_name}</td>
                    <td>{member.email}</td>
                    <td>{member.phone}</td>
                    <td>
                      <button
                        className="delete-btn"
                        onClick={() => handleDelete(member.id)}
                      >
                        <FaTrash />
                        Remover
                      </button>
                    </td>
                  </tr>
                ))

              ) : (

                <tr>
                  <td colSpan="4" style={{ textAlign: "center", padding: "20px" }}>
                    Nenhum membro na equipe
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
