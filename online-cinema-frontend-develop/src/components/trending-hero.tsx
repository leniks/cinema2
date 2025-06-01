import { Film } from '../interfaces'
import { Image } from './image'

interface Props {
  film: Film
  onPlayTrailer?: () => void
  onClick?: () => void
}

export const TrendingHero = (props: Props) => {
  return (
    <div
      className="group relative h-[250px] md:h-[300px] lg:h-[350px] xl:h-[400px] 2xl:h-[450px] w-full cursor-pointer overflow-hidden rounded-lg"
      onClick={props.onClick}
    >
      <Image
        src={
          props.film.backdrop_url ||
          `http://localhost:9000/cinema-files/movies/${props.film.movie_id}/backdrop.jpg` ||
          props.film.poster_url ||
          '/placeholder-poster.svg'
        }
        alt={props.film.title}
        className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
        style={{ objectPosition: '50% 25%' }}
      />

      {/* Улучшенные градиенты */}
      <div className="absolute inset-0 bg-gradient-to-r from-black/70 via-transparent to-black/30" />
      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-transparent to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 p-3 md:p-4 lg:p-6 xl:p-8">
        <h1 className="text-lg md:text-xl lg:text-2xl xl:text-3xl font-bold text-white">
          {props.film.title}
        </h1>
        <p className="mt-1 md:mt-2 lg:mt-3 line-clamp-2 text-xs md:text-sm lg:text-base xl:text-lg text-gray-300 leading-relaxed">
          {props.film.description}
        </p>
        {props.onPlayTrailer && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              props.onPlayTrailer?.()
            }}
            className="mt-2 md:mt-3 lg:mt-4 rounded-lg bg-primary px-3 md:px-4 lg:px-6 py-1.5 md:py-2 lg:py-3 text-xs md:text-sm lg:text-base font-semibold text-white transition-colors hover:bg-primary/80"
          >
            Play Trailer
          </button>
        )}
      </div>
    </div>
  )
}
