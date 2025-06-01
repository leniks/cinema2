import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

import { MovieService } from '../api/movie-api'
import { Container } from '../components/container'
import { Search } from '../components/search'
import { Film } from '../interfaces'

const PAGE_SIZE = 20

export const CatalogPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [movies, setMovies] = useState<Film[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [totalPages, setTotalPages] = useState(1)

  const currentPage = Number(searchParams.get('page')) || 1

  useEffect(() => {
    const fetchMovies = async () => {
      setIsLoading(true)
      const data = await MovieService.getMovies(currentPage, PAGE_SIZE)
      setMovies(data)
      // Предполагаем, что всего 1000 фильмов
      setTotalPages(Math.ceil(1000 / PAGE_SIZE))
      setIsLoading(false)
    }

    fetchMovies()
  }, [currentPage])

  const handlePageChange = (page: number) => {
    setSearchParams({ page: page.toString() })
  }

  return (
    <Container>
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Каталог фильмов</h1>
        <div className="w-96">
          <Search />
        </div>
      </div>

      {isLoading ? (
        <div className="flex h-[200px] items-center justify-center">
          <div className="text-xl text-gray-400">Загрузка...</div>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {movies.map((movie) => (
              <div
                key={movie.movie_id}
                className="flex flex-col overflow-hidden rounded-lg bg-card"
              >
                <img
                  src={movie.poster_url || '/placeholder-poster.jpg'}
                  alt={movie.title}
                  className="aspect-[2/3] w-full object-cover"
                />
                <div className="p-4">
                  <h3 className="line-clamp-1 font-medium">{movie.title}</h3>
                  <p className="line-clamp-2 text-sm text-gray-400">
                    {movie.description}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Пагинация */}
          <div className="mt-8 flex justify-center gap-2">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="rounded-lg bg-card px-4 py-2 text-white disabled:opacity-50"
            >
              Назад
            </button>
            <div className="flex items-center gap-2">
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(
                  (page) =>
                    page === 1 ||
                    page === totalPages ||
                    Math.abs(page - currentPage) <= 2,
                )
                .map((page, index, array) => (
                  <>
                    {index > 0 && array[index - 1] !== page - 1 && (
                      <span className="px-2">...</span>
                    )}
                    <button
                      key={page}
                      onClick={() => handlePageChange(page)}
                      className={`rounded-lg px-4 py-2 ${
                        currentPage === page
                          ? 'bg-primary text-white'
                          : 'bg-card text-white hover:bg-gray-700'
                      }`}
                    >
                      {page}
                    </button>
                  </>
                ))}
            </div>
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="rounded-lg bg-card px-4 py-2 text-white disabled:opacity-50"
            >
              Вперед
            </button>
          </div>
        </>
      )}
    </Container>
  )
}
