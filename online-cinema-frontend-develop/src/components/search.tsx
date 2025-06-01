import { useState, useRef, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { MovieService } from '../api/movie-api'
import { Film } from '../interfaces'
import { useDebounce } from '../hooks/useDebounce'

interface SearchCache {
  [key: string]: {
    results: Film[]
    timestamp: number
  }
}

const CACHE_DURATION = 5 * 60 * 1000 // 5 минут
const SEARCH_DEBOUNCE_DELAY = 300 // 300мс

export const Search = () => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Film[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const searchRef = useRef<HTMLFormElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()
  const searchCache = useRef<SearchCache>({})
  const previousQuery = useRef<string>('')
  const searchTimeout = useRef<NodeJS.Timeout>()

  const debouncedQuery = useDebounce(query, SEARCH_DEBOUNCE_DELAY)

  const getCachedResults = (searchQuery: string): Film[] | null => {
    const cached = searchCache.current[searchQuery.toLowerCase()]
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      return cached.results
    }
    return null
  }

  const cacheResults = (searchQuery: string, results: Film[]) => {
    searchCache.current[searchQuery.toLowerCase()] = {
      results,
      timestamp: Date.now(),
    }
  }

  const searchMovies = useCallback(async (searchQuery: string) => {
    // Очищаем предыдущий таймаут
    if (searchTimeout.current) {
      clearTimeout(searchTimeout.current)
    }

    // Проверяем минимальную длину запроса
    if (!searchQuery || searchQuery.trim().length < 2) {
      setResults([])
      setShowResults(false)
      return
    }

    // Проверяем, не повторяется ли запрос
    const trimmedQuery = searchQuery.trim().toLowerCase()
    if (trimmedQuery === previousQuery.current) {
      return
    }
    previousQuery.current = trimmedQuery

    // Проверяем кеш
    const cachedResults = getCachedResults(trimmedQuery)
    if (cachedResults) {
      console.log('Using cached results for:', trimmedQuery)
      setResults(cachedResults)
      setShowResults(true)
      return
    }

    setIsSearching(true)

    try {
      // Устанавливаем таймаут для ожидания результатов
      searchTimeout.current = setTimeout(async () => {
        const data = await MovieService.searchMovies(trimmedQuery)
        console.log('Search results for:', trimmedQuery, data)

        if (data.length > 0) {
          setResults(data)
          setShowResults(true)
          cacheResults(trimmedQuery, data)
        } else {
          // Если результатов нет, пробуем искать по частям запроса
          const words = trimmedQuery.split(/\s+/)
          if (words.length > 1) {
            const partialResults = await MovieService.searchMovies(words[0])
            setResults(partialResults)
            setShowResults(true)
            if (partialResults.length > 0) {
              cacheResults(trimmedQuery, partialResults)
            }
          }
        }
        setIsSearching(false)
      }, 300) // Добавляем небольшую задержку для накопления результатов
    } catch (error) {
      console.error('Ошибка при поиске:', error)
      setResults([])
      setIsSearching(false)
    }
  }, [])

  // Используем useEffect для отслеживания изменений в debouncedQuery
  useEffect(() => {
    if (debouncedQuery !== query) {
      searchMovies(debouncedQuery)
    }
  }, [debouncedQuery, searchMovies])

  // Очищаем таймаут при размонтировании
  useEffect(() => {
    return () => {
      if (searchTimeout.current) {
        clearTimeout(searchTimeout.current)
      }
    }
  }, [])

  const handleKeyDown = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      setShowResults(false)
      setResults([])
      setQuery('')
    } else if (e.key === 'Enter' && query.trim()) {
      e.preventDefault()
      navigate(`/search?q=${encodeURIComponent(query.trim())}`)
      setShowResults(false)
    } else if (e.key === 'ArrowDown' && results.length > 0) {
      e.preventDefault()
      const firstResult = document.querySelector(
        '[data-result-item]',
      ) as HTMLElement
      firstResult?.focus()
    }
  }

  const handleResultClick = (movieId: number) => {
    navigate(`/movie/${movieId}`)
    setShowResults(false)
    setQuery('')
    setResults([])
  }

  const handleClickOutside = useCallback((event: MouseEvent) => {
    if (
      searchRef.current &&
      !searchRef.current.contains(event.target as Node)
    ) {
      setShowResults(false)
    }
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`)
      setShowResults(false)
    }
  }

  return (
    <form
      ref={searchRef}
      className="relative w-full max-w-xl"
      onSubmit={handleSubmit}
      role="search"
      aria-label="Поиск фильмов"
    >
      <div className="relative">
        <input
          ref={inputRef}
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Поиск фильмов..."
          aria-label="Поиск фильмов"
          className="w-full rounded-lg bg-gray-800 px-4 py-3 text-white placeholder-gray-400 shadow-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary hover:bg-gray-700"
        />
        {isSearching ? (
          <div
            className="absolute right-3 top-1/2 -translate-y-1/2"
            aria-hidden="true"
          >
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
          </div>
        ) : (
          <button
            type="submit"
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
            aria-label="Искать"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </button>
        )}
      </div>

      {showResults && query.trim() && results.length > 0 && (
        <div className="absolute left-0 right-0 top-full z-50 mt-2 max-h-[70vh] overflow-y-auto rounded-lg bg-gray-800 shadow-xl">
          <div className="p-2">
            {results.slice(0, 5).map((movie, index) => (
              <button
                key={movie.movie_id}
                data-result-item
                data-result-index={index}
                onClick={() => handleResultClick(movie.movie_id)}
                className="flex w-full items-center gap-4 rounded-lg p-3 transition-all duration-200 hover:bg-gray-700 focus:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-primary"
                role="option"
                aria-selected={false}
                tabIndex={0}
              >
                <div className="relative h-16 w-12 flex-shrink-0 overflow-hidden rounded-md">
                  <img
                    src={movie.poster_url || '/placeholder-poster.jpg'}
                    alt={`Постер фильма ${movie.title}`}
                    className="h-full w-full object-cover"
                    loading="lazy"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement
                      target.src = '/placeholder-poster.jpg'
                    }}
                  />
                </div>
                <div className="flex flex-col items-start overflow-hidden">
                  <span className="text-lg font-medium text-white line-clamp-1">
                    {movie.title}
                  </span>
                  <p className="text-sm text-gray-400 line-clamp-1">
                    {movie.description}
                  </p>
                </div>
              </button>
            ))}
            {results.length > 5 && (
              <button
                onClick={() => {
                  navigate(`/search?q=${encodeURIComponent(query.trim())}`)
                  setShowResults(false)
                }}
                className="mt-2 w-full rounded-lg bg-gray-700 p-3 text-center text-sm text-gray-300 transition-colors hover:bg-gray-600"
              >
                Показать все результаты ({results.length})
              </button>
            )}
          </div>
        </div>
      )}
    </form>
  )
}
