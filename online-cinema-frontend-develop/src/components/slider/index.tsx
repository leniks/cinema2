import React, { useRef } from 'react'
import Slider, { Settings } from 'react-slick'
import 'slick-carousel/slick/slick-theme.css'
import 'slick-carousel/slick/slick.css'
import { useNavigate } from 'react-router-dom'

import { Film } from '../../interfaces'
import { Card } from '../card'
import { Loading } from '../loading'

interface Props extends Omit<Settings, 'children'> {
  movies?: Film[]
  isLoading?: boolean
  renderItem?: (item: Film) => React.ReactNode
}

export const CustomSlider = ({
  movies = [],
  isLoading = false,
  renderItem,
  ...settings
}: Props) => {
  const sliderRef = useRef<Slider>(null)
  const navigate = useNavigate()

  const defaultSettings: Settings = {
    dots: false,
    infinite: true,
    speed: 500,
    slidesToShow: 8,
    slidesToScroll: 4,
    responsive: [
      {
        breakpoint: 2560,
        settings: {
          slidesToShow: 10,
          slidesToScroll: 5,
        },
      },
      {
        breakpoint: 1920,
        settings: {
          slidesToShow: 8,
          slidesToScroll: 4,
        },
      },
      {
        breakpoint: 1600,
        settings: {
          slidesToShow: 7,
          slidesToScroll: 3,
        },
      },
      {
        breakpoint: 1440,
        settings: {
          slidesToShow: 6,
          slidesToScroll: 3,
        },
      },
      {
        breakpoint: 1280,
        settings: {
          slidesToShow: 5,
          slidesToScroll: 2,
        },
      },
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 4,
          slidesToScroll: 2,
        },
      },
    ],
    ...settings,
  }

  if (isLoading) {
    return (
      <div className="flex h-[200px] items-center justify-center">
        <Loading />
      </div>
    )
  }

  if (!movies || movies.length === 0) {
    return null
  }

  const handleMovieClick = (movie: Film) => {
    navigate(`/movie/${movie.movie_id}`)
  }

  return (
    <Slider ref={sliderRef} {...defaultSettings}>
      {movies.map((movie, index) => (
        <div
          key={movie.movie_id || index}
          className="px-1 md:px-1.5 lg:px-2 xl:px-3"
        >
          {renderItem ? (
            renderItem(movie)
          ) : (
            <Card movie={movie} onClick={() => handleMovieClick(movie)} />
          )}
        </div>
      ))}
    </Slider>
  )
}
