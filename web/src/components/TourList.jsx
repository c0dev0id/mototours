import { useState, useEffect, useMemo } from 'react'
import TourCard from './TourCard.jsx'
import { useUserState } from '../hooks/useUserState.js'
import styles from './TourList.module.css'

const CATEGORIES = [
  { key: 'ALL', label: 'All' },
  { key: 'DAY', label: 'Day' },
  { key: 'WEEKEND', label: 'Weekend' },
  { key: 'THREE_DAY', label: '3-Day' },
  { key: 'SIX_DAY', label: '6-Day' },
]

export default function TourList() {
  const [tours, setTours] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [category, setCategory] = useState('ALL')
  const [filter, setFilter] = useState('ALL') // ALL | FAVORITES | COMPLETED

  const { favorites, completed, toggleFavorite, toggleCompleted } = useUserState()

  useEffect(() => {
    fetch('data/tours.json')
      .then((r) => {
        if (!r.ok) throw new Error(`Failed to load tours: ${r.status}`)
        return r.json()
      })
      .then(setTours)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const visible = useMemo(() => {
    let list = tours
    if (category !== 'ALL') list = list.filter((t) => t.category === category)
    if (filter === 'FAVORITES') list = list.filter((t) => favorites.has(t.slug))
    if (filter === 'COMPLETED') list = list.filter((t) => completed[t.slug])
    return list
  }, [tours, category, filter, favorites, completed])

  return (
    <div className={styles.page}>
      <header className={styles.appBar}>
        <span className={styles.logo}>🏍 MotoTours</span>
      </header>

      <div className={styles.filters}>
        <div className={styles.tabs}>
          {CATEGORIES.map((c) => (
            <button
              key={c.key}
              className={`${styles.tab} ${category === c.key ? styles.activeTab : ''}`}
              onClick={() => setCategory(c.key)}
            >
              {c.label}
            </button>
          ))}
        </div>
        <div className={styles.pills}>
          {['ALL', 'FAVORITES', 'COMPLETED'].map((f) => (
            <button
              key={f}
              className={`${styles.pill} ${filter === f ? styles.activePill : ''}`}
              onClick={() => setFilter(f)}
            >
              {f === 'ALL' ? 'All' : f === 'FAVORITES' ? '★ Favourites' : '✓ Completed'}
            </button>
          ))}
        </div>
      </div>

      <main className={styles.main}>
        {loading && <p className={styles.status}>Loading tours…</p>}
        {error && <p className={styles.status + ' ' + styles.error}>{error}</p>}
        {!loading && !error && visible.length === 0 && (
          <p className={styles.status}>No tours match this filter.</p>
        )}
        <div className={styles.grid}>
          {visible.map((tour) => (
            <TourCard
              key={tour.slug}
              tour={tour}
              isFavorite={favorites.has(tour.slug)}
              isCompleted={!!completed[tour.slug]}
              onToggleFavorite={toggleFavorite}
              onToggleCompleted={toggleCompleted}
            />
          ))}
        </div>
      </main>
    </div>
  )
}
