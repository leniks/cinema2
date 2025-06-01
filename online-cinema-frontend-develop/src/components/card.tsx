import { Film } from '../interfaces'
import { Image } from './image'

interface Props {
  movie?: Film
  imageSrc?: string
  title?: string
  className?: string
  onClick?: () => void
}

export const Card = (props: Props) => {
  if (!props.movie && !props.imageSrc) {
    return null
  }

  return (
    <div
      className={`group relative cursor-pointer overflow-hidden rounded-lg transition-all hover:scale-105 ${
        props.className || ''
      }`}
      onClick={props.onClick}
      role="button"
      tabIndex={0}
      aria-label={`Открыть ${props.title || props.movie?.title}`}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          props.onClick?.()
        }
      }}
    >
      <Image
        src={props.imageSrc || props.movie?.poster_url || ''}
        alt={props.title || props.movie?.title || ''}
        className="aspect-[2/3] w-full object-cover"
      />

      <div className="absolute inset-0 flex flex-col justify-end bg-gradient-to-t from-black/80 to-transparent p-4 opacity-0 transition-opacity group-hover:opacity-100">
        <h3 className="text-lg font-bold text-white">
          {props.title || props.movie?.title}
        </h3>
        {props.movie && (
          <p className="line-clamp-2 text-sm text-gray-300">
            {props.movie.description}
          </p>
        )}
      </div>
    </div>
  )
}
