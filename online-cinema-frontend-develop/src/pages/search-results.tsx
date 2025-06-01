import { useEffect, useState, useCallback, useRef } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { MovieService } from '../api/movie-api'
import { Film } from '../interfaces'

export const SearchResultsPage = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const query = searchParams.get('q') || ''
  const [results, setResults] = useState<Film[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const searchTimeout = useRef<NodeJS.Timeout>()

  const fetchResults = useCallback(async (searchQuery: string) => {
    if (!searchQuery || searchQuery.trim().length < 2) {
      setResults([])
      setIsLoading(false)
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      if (searchTimeout.current) {
        clearTimeout(searchTimeout.current)
      }

      searchTimeout.current = setTimeout(async () => {
        const data = await MovieService.searchMovies(searchQuery)
        console.log('Search results page data:', data)

        if (data.length > 0) {
          setResults(data)
        } else {
          const words = searchQuery.trim().toLowerCase().split(/\s+/)
          if (words.length > 1) {
            const searchPromises = words.map((word) =>
              MovieService.searchMovies(word),
            )

            const allResults = await Promise.all(searchPromises)

            const combinedResults = Array.from(
              new Set(allResults.flat().map((movie) => movie.movie_id)),
            )
              .map((id) =>
                allResults.flat().find((movie) => movie.movie_id === id),
              )
              .filter((movie): movie is Film => movie !== undefined)

            if (combinedResults.length > 0) {
              setResults(combinedResults)
            } else {
              setError('По вашему запросу ничего не найдено')
            }
          } else {
            setError('По вашему запросу ничего не найдено')
          }
        }
      }, 500)
    } catch (err) {
      console.error('Error fetching search results:', err)
      setError('Произошла ошибка при поиске фильмов')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchResults(query)
    return () => {
      if (searchTimeout.current) {
        clearTimeout(searchTimeout.current)
      }
    }
  }, [query, fetchResults])

  const handleNewSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const newQuery = formData.get('search') as string

    if (newQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(newQuery.trim())}`)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="mb-4 text-2xl font-bold">
          {query ? `Результаты поиска для "${query}"` : 'Поиск фильмов'}
        </h1>

        <form onSubmit={handleNewSearch} className="flex gap-4">
          <input
            type="search"
            name="search"
            defaultValue={query}
            placeholder="Поиск фильмов..."
            className="flex-1 rounded-lg bg-gray-800 px-4 py-3 text-white placeholder-gray-400 shadow-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary hover:bg-gray-700"
          />
          <button
            type="submit"
            className="rounded-lg bg-primary px-6 py-3 font-medium text-white transition-colors hover:bg-primary/90"
          >
            Искать
          </button>
        </form>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      ) : error ? (
        <div className="rounded-lg bg-red-500/10 p-4 text-red-400" role="alert">
          <p className="font-medium">{error}</p>
          <p className="mt-2 text-sm">
            Попробуйте изменить поисковый запрос или проверить правильность
            написания
          </p>
        </div>
      ) : results.length > 0 ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
          {results.map((movie) => (
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
      ) : query ? (
        <div className="flex flex-col items-center justify-center py-20 text-gray-400">
          <svg
            className="mb-4 h-16 w-16"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <p className="text-lg">Ничего не найдено</p>
          <p className="mt-2 text-sm">
            Попробуйте изменить поисковый запрос или проверить правильность
            написания
          </p>
        </div>
      ) : null}
    </div>
  )
}
