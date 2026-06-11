export default function StarRating({ value, onChange, readOnly = false, light = false }) {

  const stars = [1, 2, 3, 4, 5];

  let className = "star-rating";
  if (readOnly) className += " readonly";
  if (light) className += " light";

  return (
    <div className={className}>
      {stars.map((star) => (
        <span
          key={star}
          className={star <= value ? "star filled" : "star"}
          onClick={readOnly ? undefined : () => onChange(star)}
        >
          ★
        </span>
      ))}
    </div>
  );
}
