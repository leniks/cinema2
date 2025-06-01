import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { MovieService } from '../api/movie-api'
import { Image } from '../components/image'
import { Loading } from '../components/loading'
import { Section } from '../components/section'
import { CustomSlider } from '../components/slider'
import { VideoPlayer } from '../components/video-player'
import { ActorsCast } from '../components/actors-cast'
import { Film } from '../interfaces'

export const FilmPage = () => {
  const [film, setFilm] = useState<Film>()
  const [similarMovies, setSimilarMovies] = useState<Film[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [showPlayer, setShowPlayer] = useState(false)

  const navigate = useNavigate()
  const { id } = useParams()

  useEffect(() => {
    const fetchData = async () => {
      if (!id) {
        setError('ID фильма не указан')
        return
      }

      try {
        setIsLoading(true)
        setError('')
        const movieId = parseInt(id, 10)

        if (isNaN(movieId)) {
          setError('Некорректный ID фильма')
          return
        }

        // Получаем информацию о фильме и похожие фильмы параллельно
        const [movie, similar] = await Promise.all([
          MovieService.getMovie(movieId),
          MovieService.getSimilarMovies(movieId),
        ])

        if (movie) {
          setFilm(movie)
          setSimilarMovies(similar.filter((m) => m.movie_id !== movieId))
        } else {
          setError('Фильм не найден')
        }
      } catch (error) {
        console.error('Error fetching movie data:', error)
        setError('Ошибка при загрузке данных')
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [id])

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loading />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4">
        <div className="text-xl text-red-500">{error}</div>
        <button
          onClick={() => navigate('/')}
          className="rounded-lg bg-primary px-4 py-2 text-white hover:bg-primary/80"
        >
          Вернуться на главную
        </button>
      </div>
    )
  }

  if (!film) {
    return null
  }

  return (
    <>
      {/* Hero Section */}
      <div className="relative h-[400px] md:h-[500px] lg:h-[600px] xl:h-[700px] 2xl:h-[800px] overflow-hidden">
        {/* Backdrop Image */}
        <Image
          src={
            film.backdrop_url ||
            `http://localhost:9000/cinema-files/movies/${film.movie_id}/backdrop.jpg` ||
            film.poster_url ||
            '/placeholder-poster.svg'
          }
          alt={film.title}
          className="h-full w-full object-cover scale-105 transition-transform duration-700 hover:scale-110"
          style={{ objectPosition: '50% 25%' }}
        />

        {/* Multi-layer gradients for better readability */}
        <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/40 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-transparent to-black/30" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/80" />
      </div>

      {/* Movie Details */}
      <Section className="-mt-[120px] md:-mt-[150px] lg:-mt-[180px] xl:-mt-[200px] relative z-10">
        <div className="flex gap-6 md:gap-8 lg:gap-12 xl:gap-16 mobile:flex-col">
          <Image
            src={film.poster_url || '/placeholder-poster.svg'}
            alt={film.title}
            className="h-[250px] md:h-[300px] lg:h-[350px] xl:h-[400px] w-[167px] md:w-[200px] lg:w-[233px] xl:w-[267px] shrink-0 rounded-lg mobile:mx-auto"
          />

          <div className="flex flex-col gap-3 md:gap-4 lg:gap-6">
            <h1 className="text-2xl md:text-3xl lg:text-4xl xl:text-5xl font-bold">
              {film.title}
            </h1>
            <p className="text-sm md:text-base lg:text-lg xl:text-xl text-gray-300 leading-relaxed">
              {film.description}
            </p>
            <div className="flex gap-4 flex-wrap">
              <button
                onClick={() => setShowPlayer(!showPlayer)}
                className="w-fit rounded-lg bg-primary px-4 md:px-6 lg:px-8 xl:px-10 py-2 md:py-3 lg:py-4 text-sm md:text-base lg:text-lg text-white hover:bg-primary/80 transition-colors"
              >
                {showPlayer ? 'Скрыть плеер' : 'Смотреть фильм'}
              </button>
            </div>
          </div>
        </div>

        {/* Video Player */}
        {showPlayer && (
          <div className="mt-8">
            <VideoPlayer
              src={`http://localhost:8001/streaming/${film.movie_id}`}
              poster={film.poster_url || '/placeholder-poster.svg'}
              className="aspect-video w-full"
            />
          </div>
        )}
      </Section>

      {/* Actors Cast */}
      <Section>
        <ActorsCast movieId={film.movie_id} />
      </Section>

      {/* Similar Movies */}
      {similarMovies.length > 0 && (
        <Section title="Похожие фильмы">
          <CustomSlider movies={similarMovies} />
        </Section>
      )}
    </>
  )
}
