import { useEffect, useState } from "react";

import {
  getServices,
  getClients,
  getPackages,
  createPackage,
  updatePackage,
  deletePackage,
  purchasePackage,
  getClientPackages,
} from "../services/api";

import Navbar from "../components/Navbar";

import { toast } from "react-toastify";

import {
  FaBoxOpen,
  FaEdit,
  FaTrash,
  FaPlus,
  FaDollarSign,
  FaShoppingCart,
} from "react-icons/fa";

import "../styles/services.css";

export default function Packages() {

  const [packages, setPackages] = useState([]);

  const [services, setServices] = useState([]);

  const [clients, setClients] = useState([]);

  const [name, setName] = useState("");

  const [serviceId, setServiceId] = useState("");

  const [totalSessions, setTotalSessions] = useState("");

  const [price, setPrice] = useState("");

  const [editingId, setEditingId] = useState(null);

  const [purchaseClientId, setPurchaseClientId] = useState("");

  const [purchasePackageId, setPurchasePackageId] = useState("");

  const [clientPackages, setClientPackages] = useState([]);


  async function loadData() {

    try {

      const [packagesData, servicesData, clientsData] = await Promise.all([
        getPackages(),
        getServices(),
        getClients(),
      ]);

      setPackages(packagesData);

      setServices(servicesData);

      setClients(clientsData);

    } catch (error) {

      console.error(error);

      toast.error("Erro ao carregar pacotes");
    }
  }


  useEffect(() => {
    loadData();
  }, []);


  function serviceName(id) {

    const service = services.find((s) => s.id === id);

    return service ? service.name : "—";
  }


  function clientName(id) {

    const found = clients.find((c) => c.id === id);

    return found ? found.full_name : "—";
  }


  function clearForm() {

    setEditingId(null);

    setName("");

    setServiceId("");

    setTotalSessions("");

    setPrice("");
  }


  async function handleSubmit(e) {

    e.preventDefault();

    if (!name.trim()) {
      toast.error("Informe o nome do pacote");
      return;
    }

    if (!serviceId) {
      toast.error("Selecione o serviço do pacote");
      return;
    }

    if (!totalSessions || Number(totalSessions) <= 0) {
      toast.error("Informe a quantidade de sessões");
      return;
    }

    if (!price || Number(price) <= 0) {
      toast.error("Informe um preço válido");
      return;
    }

    const packageData = {
      name: name.trim(),
      service_id: Number(serviceId),
      total_sessions: Number(totalSessions),
      price: Number(price),
    };

    try {

      if (editingId) {

        await updatePackage(editingId, packageData);

        toast.success("Pacote atualizado");

      } else {

        await createPackage(packageData);

        toast.success("Pacote cadastrado");
      }

      clearForm();

      loadData();

    } catch (error) {

      console.error(error);

      toast.error("Erro ao salvar pacote");
    }
  }


  function handleEdit(pkg) {

    setEditingId(pkg.id);

    setName(pkg.name);

    setServiceId(pkg.service_id);

    setTotalSessions(pkg.total_sessions);

    setPrice(pkg.price);
  }


  async function handleDelete(id) {

    const confirmDelete = window.confirm(
      "Deseja realmente excluir este pacote?"
    );

    if (!confirmDelete) return;

    try {

      await deletePackage(id);

      toast.success("Pacote removido");

      loadData();

    } catch (error) {

      console.error(error);

      toast.error(
        "Erro ao excluir pacote. Verifique se já foi vendido a algum cliente."
      );
    }
  }


  async function loadClientPackages(clientId) {

    if (!clientId) {
      setClientPackages([]);
      return;
    }

    try {

      const data = await getClientPackages(clientId);

      setClientPackages(data);

    } catch (error) {

      console.error(error);

      toast.error("Erro ao carregar saldo de pacotes do cliente");
    }
  }


  async function handlePurchase(e) {

    e.preventDefault();

    if (!purchaseClientId) {
      toast.error("Selecione um cliente");
      return;
    }

    if (!purchasePackageId) {
      toast.error("Selecione um pacote");
      return;
    }

    try {

      await purchasePackage({
        client_id: Number(purchaseClientId),
        package_id: Number(purchasePackageId),
      });

      toast.success("Pacote vendido ao cliente");

      setPurchasePackageId("");

      loadClientPackages(purchaseClientId);

    } catch (error) {

      console.error(error);

      toast.error("Erro ao vender pacote");
    }
  }


  return (

    <div className="services-page">

      <Navbar />

      <div className="services-container">

        <div className="services-card">

          <h1 className="services-title">

            <FaBoxOpen />

            Pacotes

          </h1>


          <form
            onSubmit={handleSubmit}
            className="services-form"
          >

            <input
              type="text"
              placeholder="Nome do pacote"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />

            <select
              value={serviceId}
              onChange={(e) => setServiceId(e.target.value)}
              required
            >
              <option value="">Serviço...</option>

              {services.map((service) => (
                <option key={service.id} value={service.id}>
                  {service.name}
                </option>
              ))}
            </select>

            <input
              type="number"
              min="1"
              placeholder="Qtd. sessões"
              value={totalSessions}
              onChange={(e) => setTotalSessions(e.target.value)}
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
                <th>Serviço</th>
                <th>Sessões</th>
                <th>Preço</th>
                <th>Ações</th>
              </tr>
            </thead>

            <tbody>

              {packages.length > 0 ? (

                packages.map((pkg) => (

                  <tr key={pkg.id}>

                    <td>{pkg.id}</td>

                    <td>{pkg.name}</td>

                    <td>{serviceName(pkg.service_id)}</td>

                    <td>{pkg.total_sessions}</td>

                    <td>
                      <div className="price-cell">
                        <FaDollarSign />
                        R$ {Number(pkg.price).toFixed(2)}
                      </div>
                    </td>

                    <td>
                      <div className="actions">

                        <button
                          className="edit-btn"
                          onClick={() => handleEdit(pkg)}
                        >
                          <FaEdit />
                          Editar
                        </button>

                        <button
                          className="delete-btn"
                          onClick={() => handleDelete(pkg.id)}
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
                  <td colSpan="6" style={{ textAlign: "center", padding: "20px" }}>
                    Nenhum pacote cadastrado
                  </td>
                </tr>

              )}

            </tbody>

          </table>


          <h1 className="services-title" style={{ marginTop: "40px" }}>

            <FaShoppingCart />

            Vender pacote / Saldo do cliente

          </h1>

          <form
            onSubmit={handlePurchase}
            className="services-form"
          >

            <select
              value={purchaseClientId}
              onChange={(e) => {
                setPurchaseClientId(e.target.value);
                loadClientPackages(e.target.value);
              }}
              required
            >
              <option value="">Cliente...</option>

              {clients.map((client) => (
                <option key={client.id} value={client.id}>
                  {client.full_name}
                </option>
              ))}
            </select>

            <select
              value={purchasePackageId}
              onChange={(e) => setPurchasePackageId(e.target.value)}
              required
            >
              <option value="">Pacote...</option>

              {packages.map((pkg) => (
                <option key={pkg.id} value={pkg.id}>
                  {pkg.name} ({pkg.total_sessions}x {serviceName(pkg.service_id)})
                </option>
              ))}
            </select>

            <button type="submit" className="primary-btn">
              <FaShoppingCart />
              Vender
            </button>

          </form>

          {purchaseClientId && (

            <table className="services-table">

              <thead>
                <tr>
                  <th>Pacote</th>
                  <th>Serviço</th>
                  <th>Sessões restantes</th>
                  <th>Total de sessões</th>
                </tr>
              </thead>

              <tbody>

                {clientPackages.length > 0 ? (

                  clientPackages.map((cp) => (

                    <tr key={cp.id}>
                      <td>{cp.package_name}</td>
                      <td>{serviceName(cp.service_id)}</td>
                      <td>{cp.remaining_sessions}</td>
                      <td>{cp.total_sessions}</td>
                    </tr>
                  ))

                ) : (

                  <tr>
                    <td colSpan="4" style={{ textAlign: "center", padding: "20px" }}>
                      {clientName(Number(purchaseClientId))} ainda não possui pacotes
                    </td>
                  </tr>

                )}

              </tbody>

            </table>

          )}

        </div>

      </div>

    </div>
  );
}
