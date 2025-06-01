import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { MovieService } from '../api/movie-api'
import { Film } from '../interfaces'
import { useGlobalContext } from './app-container'
import { Image } from './image'

interface Props {
  keyword: string
  goToSearchPage: Function
}

export const SearchResult = (props: Props) => {
  const [items, setItems] = useState<Film[]>([])
  const [totalItem, setTotalItem] = useState(0)
  const searchTimeout = useRef<any>('')
  const globalContext = useGlobalContext()
  const navigate = useNavigate()

  const fetch = useCallback(async () => {
    if (!props.keyword) return

    clearTimeout(searchTimeout.current)
    searchTimeout.current = setTimeout(async () => {
      try {
        const results = await MovieService.searchMovies(props.keyword)
        setItems(results)
        setTotalItem(results.length)
      } catch (error) {
        console.error('Error searching movies:', error)
        setItems([])
        setTotalItem(0)
      }
    }, 120)
  }, [props.keyword])

  useEffect(() => {
    fetch()
  }, [fetch])

  return (
    <div className="absolute top-[48px] left-0 right-0 rounded-md bg-header shadow-lg">
      {items.length > 0 && (
        <div className="max-h-[480px] overflow-y-auto">
          {items.map((item) => (
            <div
              key={item.movie_id}
              className="flex cursor-pointer gap-4 p-1.5 hover:bg-primary"
              onClick={() => {
                navigate('/movie/' + item.movie_id)
                globalContext.setSearchResult(false)
              }}
            >
              <Image
                src={item.poster_url || '/placeholder-poster.jpg'}
                className="h-[72px] min-w-[102px] rounded-md"
                alt={item.title}
              />
              <div className="flex flex-col gap-1 py-1">
                <p className="text-sm font-bold text-white">{item.title}</p>
                <p className="line-clamp-2 text-xs text-gray-400">
                  {item.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {totalItem > 0 && (
        <button
          onClick={() => props.goToSearchPage()}
          className="w-full p-3 text-center text-sm hover:text-primary"
        >
          More results
        </button>
      )}
    </div>
  )
}
