import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { Film } from '../interfaces'

interface Props {
  movies: Film[]
}

export const HeroSlider = ({ movies }: Props) => {
  const [currentIndex, setCurrentIndex] = useState(0)
  const navigate = useNavigate()

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % movies.length)
    }, 5000)

    return () => clearInterval(interval)
  }, [movies.length])

  const handlePrevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + movies.length) % movies.length)
  }

  const handleNextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % movies.length)
  }

  if (!movies.length) return null

  const currentMovie = movies[currentIndex]

  return (
    <div className="relative h-[60vh] md:h-[70vh] lg:h-[80vh] xl:h-[85vh] 2xl:h-[90vh] w-full overflow-hidden">
      {/* Фоновое изображение */}
      <div
        className="absolute inset-0 bg-cover transition-all duration-1000 scale-105 hover:scale-110"
        style={{
          backgroundImage: `url(${
            currentMovie.backdrop_url ||
            `http://localhost:9000/cinema-files/movies/${currentMovie.movie_id}/backdrop.jpg`
          })`,
          backgroundPosition: '50% 25%',
        }}
      >
        {/* Улучшенные градиентные оверлеи */}
        <div className="absolute inset-0 bg-gradient-to-r from-black/90 via-black/50 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/70" />
      </div>

      {/* Контент */}
      <div className="relative flex h-full items-center">
        <div className="container mx-auto px-4 md:px-6 lg:px-8 xl:px-12 2xl:px-16">
          <div className="max-w-2xl lg:max-w-3xl xl:max-w-4xl 2xl:max-w-5xl">
            <h1 className="mb-4 text-3xl md:text-4xl lg:text-5xl xl:text-6xl 2xl:text-7xl font-bold text-white leading-tight">
              {currentMovie.title}
            </h1>
            <p className="mb-6 md:mb-8 lg:mb-10 text-base md:text-lg lg:text-xl xl:text-2xl text-gray-300 leading-relaxed">
              {currentMovie.description}
            </p>
            <div className="flex gap-3 md:gap-4 lg:gap-6">
              <button
                onClick={() => navigate(`/movie/${currentMovie.movie_id}`)}
                className="rounded-lg bg-primary px-6 md:px-8 lg:px-10 xl:px-12 py-2 md:py-3 lg:py-4 text-sm md:text-base lg:text-lg font-medium text-white transition-colors hover:bg-primary/80"
              >
                Смотреть
              </button>
              <button
                onClick={() => navigate(`/movie/${currentMovie.movie_id}`)}
                className="rounded-lg bg-white/20 px-6 md:px-8 lg:px-10 xl:px-12 py-2 md:py-3 lg:py-4 text-sm md:text-base lg:text-lg font-medium text-white backdrop-blur-sm transition-colors hover:bg-white/30"
              >
                Подробнее
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Кнопки навигации */}
      <button
        onClick={handlePrevSlide}
        className="absolute left-2 md:left-4 lg:left-6 xl:left-8 top-1/2 -translate-y-1/2 rounded-full bg-black/50 p-2 md:p-3 lg:p-4 text-white backdrop-blur-sm transition-colors hover:bg-black/70"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-4 w-4 md:h-6 md:w-6 lg:h-8 lg:w-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 19l-7-7 7-7"
          />
        </svg>
      </button>
      <button
        onClick={handleNextSlide}
        className="absolute right-2 md:right-4 lg:right-6 xl:right-8 top-1/2 -translate-y-1/2 rounded-full bg-black/50 p-2 md:p-3 lg:p-4 text-white backdrop-blur-sm transition-colors hover:bg-black/70"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-4 w-4 md:h-6 md:w-6 lg:h-8 lg:w-8"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5l7 7-7 7"
          />
        </svg>
      </button>

      {/* Индикаторы */}
      <div className="absolute bottom-3 md:bottom-4 lg:bottom-6 xl:bottom-8 left-1/2 flex -translate-x-1/2 gap-1 md:gap-2 lg:gap-3">
        {movies.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentIndex(index)}
            className={`h-1.5 md:h-2 lg:h-3 rounded-full transition-all ${
              index === currentIndex
                ? 'w-6 md:w-8 lg:w-12 bg-primary'
                : 'w-1.5 md:w-2 lg:w-3 bg-white/50 hover:bg-white/80'
            }`}
          />
        ))}
      </div>
    </div>
  )
}
