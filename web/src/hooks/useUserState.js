import { useState, useCallback } from 'react'

const FAV_KEY = 'mototours_favorites'
const DONE_KEY = 'mototours_completed'

function readFavorites() {
  try {
    return new Set(JSON.parse(localStorage.getItem(FAV_KEY) || '[]'))
  } catch {
    return new Set()
  }
}

function readCompleted() {
  try {
    return JSON.parse(localStorage.getItem(DONE_KEY) || '{}')
  } catch {
    return {}
  }
}

export function useUserState() {
  const [favorites, setFavorites] = useState(() => readFavorites())
  const [completed, setCompleted] = useState(() => readCompleted())

  const toggleFavorite = useCallback((slug) => {
    setFavorites((prev) => {
      const next = new Set(prev)
      if (next.has(slug)) {
        next.delete(slug)
      } else {
        next.add(slug)
      }
      localStorage.setItem(FAV_KEY, JSON.stringify([...next]))
      return next
    })
  }, [])

  const toggleCompleted = useCallback((slug) => {
    setCompleted((prev) => {
      const next = { ...prev }
      if (next[slug]) {
        delete next[slug]
      } else {
        next[slug] = Date.now()
      }
      localStorage.setItem(DONE_KEY, JSON.stringify(next))
      return next
    })
  }, [])

  return { favorites, completed, toggleFavorite, toggleCompleted }
}
