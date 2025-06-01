import { Film } from '../../interfaces'
import { Image } from '../image'

interface MovieCardProps {
  movie: Film
  onClick?: () => void
}

export const MovieCard = ({ movie, onClick }: MovieCardProps) => {
  return (
    <div
      className="group relative cursor-pointer overflow-hidden rounded-lg transition-all hover:scale-105"
      onClick={onClick}
      role="button"
      tabIndex={0}
      aria-label={`Открыть фильм ${movie.title}`}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onClick?.()
        }
      }}
    >
      <Image
        src={movie.poster_url || '/placeholder-poster.jpg'}
        alt={movie.title}
        className="aspect-[2/3] w-full object-cover"
      />

      <div className="absolute inset-0 flex flex-col justify-end bg-gradient-to-t from-black/80 to-transparent p-4 opacity-0 transition-opacity group-hover:opacity-100">
        <h3 className="text-lg font-bold text-white">{movie.title}</h3>
        <p className="line-clamp-2 text-sm text-gray-300">
          {movie.description}
        </p>
      </div>
    </div>
  )
}
