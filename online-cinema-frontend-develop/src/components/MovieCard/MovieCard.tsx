import React from 'react'
import { Movie } from '../../types/api.types'
import styles from './MovieCard.module.css'

interface MovieCardProps {
  movie: Movie
  onClick?: (movie: Movie) => void
}

export const MovieCard: React.FC<MovieCardProps> = ({ movie, onClick }) => {
  const handleClick = () => {
    if (onClick) {
      onClick(movie)
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  return (
    <div className={styles.card} onClick={handleClick}>
      <div className={styles.posterContainer}>
        {movie.poster_url ? (
          <img
            src={movie.poster_url}
            alt={movie.title}
            className={styles.poster}
          />
        ) : (
          <div className={styles.noPoster}>Нет постера</div>
        )}
        {movie.rating && (
          <div className={styles.rating}>{movie.rating.toFixed(1)}</div>
        )}
      </div>
      <div className={styles.content}>
        <h3 className={styles.title}>{movie.title}</h3>
        {movie.release_date && (
          <p className={styles.date}>{formatDate(movie.release_date)}</p>
        )}
        <p className={styles.description}>
          {movie.description.length > 150
            ? `${movie.description.slice(0, 150)}...`
            : movie.description}
        </p>
      </div>
    </div>
  )
}
