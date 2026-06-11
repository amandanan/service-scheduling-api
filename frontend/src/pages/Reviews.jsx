import { useEffect, useState } from "react";
import { toast } from "react-toastify";

import { getReviews } from "../services/api";

import Navbar from "../components/Navbar";
import StarRating from "../components/StarRating";

import { FaStar } from "react-icons/fa";

import "../styles/services.css";
import "../styles/reviews.css";

export default function Reviews() {

  const [reviews, setReviews] = useState([]);


  async function loadData() {

    try {

      const data = await getReviews();

      setReviews(data);

    } catch (error) {

      console.error(error);

      toast.error("Erro ao carregar avaliações");
    }
  }


  useEffect(() => {
    loadData();
  }, []);


  const totalReviews = reviews.length;

  const averageRating = totalReviews > 0
    ? reviews.reduce((sum, r) => sum + r.rating, 0) / totalReviews
    : null;


  return (

    <div className="services-page">

      <Navbar />

      <div className="services-container">

        <div className="services-card">

          <h1 className="services-title">
            <FaStar />
            Avaliações
          </h1>

          {totalReviews > 0 && (
            <div className="reviews-summary-card">
              <span className="reviews-summary-score">
                {averageRating.toFixed(1)}
              </span>

              <div>
                <StarRating value={Math.round(averageRating)} readOnly light />
                <div className="reviews-summary-count">
                  {totalReviews} {totalReviews === 1 ? "avaliação" : "avaliações"}
                </div>
              </div>
            </div>
          )}

          {reviews.length > 0 ? (

            reviews.map((review) => (

              <div key={review.id} className="owner-review-card">

                <div className="owner-review-header">
                  <StarRating value={review.rating} readOnly light />

                  <span className="owner-review-meta">
                    {review.client_name} • {review.service_name} •{" "}
                    {new Date(review.scheduled_at).toLocaleDateString("pt-BR")}
                  </span>
                </div>

                {review.comment && (
                  <p className="owner-review-comment">{review.comment}</p>
                )}

              </div>
            ))

          ) : (

            <p style={{ textAlign: "center", padding: "20px", color: "#6b7280" }}>
              Nenhuma avaliação recebida ainda
            </p>

          )}

        </div>

      </div>

    </div>
  );
}
