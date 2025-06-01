import { useState, useEffect } from 'react'
import { Image } from './image'

interface Actor {
  id: number
  name: string
  photo_url: string | null
  birth_date: string | null
  biography: string | null
  character: string | null
}

interface ActorsCastProps {
  movieId: number
}

export const ActorsCast = ({ movieId }: ActorsCastProps) => {
  const [actors, setActors] = useState<Actor[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    const fetchActors = async () => {
      try {
        setIsLoading(true)
        setError('')

        const response = await fetch(`http://localhost:8001/actors/${movieId}`)

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const actorsData = await response.json()
        setActors(actorsData)
      } catch (error) {
        console.error('Error fetching actors:', error)
        setError('Ошибка при загрузке актеров')
      } finally {
        setIsLoading(false)
      }
    }

    fetchActors()
  }, [movieId])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-500">{error}</p>
      </div>
    )
  }

  if (actors.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-400">Информация о актерах недоступна</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl md:text-2xl lg:text-3xl font-bold">
        В главных ролях
      </h2>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 md:gap-6">
        {actors.map((actor) => (
          <div key={actor.id} className="group cursor-pointer">
            <div className="aspect-[3/4] relative overflow-hidden rounded-lg bg-gray-800">
              <Image
                src={actor.photo_url || '/placeholder-actor.jpg'}
                alt={actor.name}
                className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-110"
              />

              {/* Gradient overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

              {/* Actor info on hover */}
              <div className="absolute bottom-0 left-0 right-0 p-3 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-sm font-medium truncate">{actor.name}</p>
                {actor.character && (
                  <p className="text-xs text-gray-300 truncate">
                    {actor.character}
                  </p>
                )}
              </div>
            </div>

            {/* Actor info always visible on mobile */}
            <div className="mt-2 md:hidden">
              <p className="text-sm font-medium text-white truncate">
                {actor.name}
              </p>
              {actor.character && (
                <p className="text-xs text-gray-400 truncate">
                  {actor.character}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
