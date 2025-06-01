import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { MovieService } from '../api/movie-api'
import { Film } from '../interfaces'

const MOVIES_PER_PAGE = 24

export const AllMoviesPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [movies, setMovies] = useState<Film[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [totalPages, setTotalPages] = useState(1)

  const currentPage = Number(searchParams.get('page')) || 1

  useEffect(() => {
    const fetchMovies = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const data = await MovieService.getMovies(currentPage, MOVIES_PER_PAGE)
        setMovies(data)
        // Предполагаем, что всего 1000 фильмов (можно будет заменить на реальное количество)
        setTotalPages(Math.ceil(1000 / MOVIES_PER_PAGE))
      } catch (err) {
        console.error('Error fetching movies:', err)
        setError('Произошла ошибка при загрузке фильмов')
      } finally {
        setIsLoading(false)
      }
    }

    fetchMovies()
  }, [currentPage])

  const handlePageChange = (page: number) => {
    setSearchParams({ page: page.toString() })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="mb-6 text-3xl font-bold text-white">Все фильмы</h1>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : error ? (
        <div className="rounded-lg bg-red-500/10 p-4 text-red-400" role="alert">
          <p>{error}</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
            {movies.map((movie) => (
              <div
                key={movie.movie_id}
                className="group relative overflow-hidden rounded-lg bg-gray-800 shadow-lg transition-transform duration-200 hover:-translate-y-1"
              >
                <div className="relative aspect-[2/3] w-full">
                  <img
                    src={movie.poster_url || '/placeholder-poster.jpg'}
                    alt={`Постер фильма ${movie.title}`}
                    className="h-full w-full object-cover transition-transform duration-200 group-hover:scale-105"
                    loading="lazy"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement
                      target.src = '/placeholder-poster.jpg'
                    }}
                  />
                  {movie.rating > 0 && (
                    <div className="absolute bottom-2 right-2 flex items-center gap-1 rounded-full bg-black/60 px-2 py-1 text-xs text-yellow-400">
                      <svg
                        className="h-3 w-3"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                      <span>{movie.rating.toFixed(1)}</span>
                    </div>
                  )}
                </div>
                <div className="p-2">
                  <h2 className="text-sm font-medium text-white line-clamp-2">
                    {movie.title}
                  </h2>
                </div>
                <a
                  href={`/movie/${movie.movie_id}`}
                  className="absolute inset-0"
                  aria-label={`Подробнее о фильме ${movie.title}`}
                />
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="mt-8 flex justify-center gap-2">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="rounded-lg bg-gray-800 px-4 py-2 text-white transition-colors disabled:opacity-50 hover:enabled:bg-gray-700"
              >
                Назад
              </button>
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(
                  (page) =>
                    page === 1 ||
                    page === totalPages ||
                    Math.abs(page - currentPage) <= 2,
                )
                .map((page, index, array) => (
                  <div key={page} className="flex items-center">
                    {index > 0 && array[index - 1] !== page - 1 && (
                      <span className="mx-2 text-gray-400">...</span>
                    )}
                    <button
                      onClick={() => handlePageChange(page)}
                      className={`rounded-lg px-4 py-2 transition-colors ${
                        currentPage === page
                          ? 'bg-primary text-white'
                          : 'bg-gray-800 text-white hover:bg-gray-700'
                      }`}
                    >
                      {page}
                    </button>
                  </div>
                ))}
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="rounded-lg bg-gray-800 px-4 py-2 text-white transition-colors disabled:opacity-50 hover:enabled:bg-gray-700"
              >
                Вперед
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
