import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useUserState } from '../hooks/useUserState.js'
import MapView from './MapView.jsx'
import styles from './TourDetail.module.css'

export default function TourDetail() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const [tour, setTour] = useState(null)
  const [loading, setLoading] = useState(true)
  const { favorites, completed, toggleFavorite, toggleCompleted } = useUserState()

  useEffect(() => {
    fetch('data/tours.json')
      .then((r) => r.json())
      .then((tours) => {
        const found = tours.find((t) => t.slug === slug)
        setTour(found ?? null)
      })
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) return <div className={styles.status}>Loading…</div>
  if (!tour) return <div className={styles.status}>Tour not found.</div>

  const isFav = favorites.has(tour.slug)
  const isDone = !!completed[tour.slug]

  return (
    <div className={styles.page}>
      <header className={styles.appBar}>
        <button className={styles.back} onClick={() => navigate('/')} aria-label="Back">
          ← Back
        </button>
        <div className={styles.headerActions}>
          <button
            className={`${styles.iconBtn} ${isFav ? styles.active : ''}`}
            onClick={() => toggleFavorite(tour.slug)}
            title={isFav ? 'Remove from favourites' : 'Favourite'}
          >
            ★
          </button>
          <button
            className={`${styles.iconBtn} ${isDone ? styles.done : ''}`}
            onClick={() => toggleCompleted(tour.slug)}
            title={isDone ? 'Mark as not completed' : 'Mark as completed'}
          >
            ✓
          </button>
          {tour.hasPdf && (
            <Link className={styles.pdfBtn} to={`/tour/${tour.slug}/pdf`}>
              PDF Guide
            </Link>
          )}
        </div>
      </header>

      <div className={styles.hero}>
        <span className={styles.region}>{tour.region}</span>
        <h1 className={styles.name}>{tour.name}</h1>
        <div className={styles.meta}>
          <span>{tour.categoryLabel}</span>
          <span>·</span>
          <span>{tour.totalDistanceKm} km</span>
          {tour.dayCount > 1 && (
            <>
              <span>·</span>
              <span>{tour.dayCount} days</span>
            </>
          )}
        </div>
      </div>

      {/* Inline map for all days */}
      {tour.gpxFiles && tour.gpxFiles.length > 0 && (
        <div className={styles.mapSection}>
          <MapView inline gpxFiles={tour.gpxFiles} />
        </div>
      )}

      <div className={styles.content}>
        {tour.overview && (
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Overview</h2>
            <p>{tour.overview}</p>
          </section>
        )}
        {tour.highlights && (
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Highlights</h2>
            <p>{tour.highlights}</p>
          </section>
        )}
        {tour.roadCharacter && (
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Road Character</h2>
            <p>{tour.roadCharacter}</p>
          </section>
        )}

        {tour.days && tour.days.length > 0 && (
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>Days</h2>
            <div className={styles.dayList}>
              {tour.days.map((day, i) => {
                const dayNum = i + 1
                const gpxEntry = tour.gpxFiles?.find((g) => g.dayNumber === dayNum)
                return (
                  <div key={i} className={styles.dayItem}>
                    <div className={styles.dayHeader}>
                      <div>
                        <span className={styles.dayLabel}>Day {dayNum}</span>
                        <span className={styles.dayName}>{day.name}</span>
                      </div>
                      <div className={styles.dayRight}>
                        <span className={styles.dayDist}>{day.distance_km} km</span>
                        {gpxEntry && (
                          <Link
                            className={styles.mapLink}
                            to={`/tour/${tour.slug}/day/${dayNum}/map`}
                          >
                            Map →
                          </Link>
                        )}
                      </div>
                    </div>
                    {day.description && (
                      <p className={styles.dayDesc}>{day.description}</p>
                    )}
                  </div>
                )
              })}
            </div>
          </section>
        )}
      </div>
    </div>
  )
}
