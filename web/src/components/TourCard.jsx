import { useNavigate } from 'react-router-dom'
import styles from './TourCard.module.css'

const CATEGORY_COLOURS = {
  DAY: '#C8611A',
  WEEKEND: '#2C5530',
  THREE_DAY: '#1a6bc8',
  SIX_DAY: '#8B1AC8',
}

export default function TourCard({ tour, isFavorite, isCompleted, onToggleFavorite, onToggleCompleted }) {
  const navigate = useNavigate()

  return (
    <div className={styles.card} onClick={() => navigate(`/tour/${tour.slug}`)}>
      <div className={styles.header}>
        <span
          className={styles.badge}
          style={{ background: CATEGORY_COLOURS[tour.category] ?? '#555' }}
        >
          {tour.categoryLabel}
        </span>
        <div className={styles.actions} onClick={(e) => e.stopPropagation()}>
          <button
            className={`${styles.iconBtn} ${isFavorite ? styles.active : ''}`}
            title={isFavorite ? 'Remove from favourites' : 'Add to favourites'}
            onClick={() => onToggleFavorite(tour.slug)}
            aria-label="Toggle favourite"
          >
            ★
          </button>
          <button
            className={`${styles.iconBtn} ${isCompleted ? styles.done : ''}`}
            title={isCompleted ? 'Mark as not completed' : 'Mark as completed'}
            onClick={() => onToggleCompleted(tour.slug)}
            aria-label="Toggle completed"
          >
            ✓
          </button>
        </div>
      </div>

      <h2 className={styles.name}>{tour.name}</h2>
      <p className={styles.region}>{tour.region}</p>

      <div className={styles.meta}>
        <span>{tour.totalDistanceKm} km</span>
        {tour.dayCount > 1 && <span>{tour.dayCount} days</span>}
      </div>
    </div>
  )
}
