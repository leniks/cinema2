declare module 'react-slick' {
  import { ComponentType, ReactNode } from 'react'

  export interface Settings {
    accessibility?: boolean
    adaptiveHeight?: boolean
    afterChange?(currentSlide: number): void
    appendDots?(dots: ReactNode): ReactNode
    arrows?: boolean
    asNavFor?: Slider
    autoplay?: boolean
    autoplaySpeed?: number
    beforeChange?(currentSlide: number, nextSlide: number): void
    centerMode?: boolean
    centerPadding?: string
    className?: string
    cssEase?: string
    customPaging?(i: number): ReactNode
    dots?: boolean
    dotsClass?: string
    draggable?: boolean
    easing?: string
    edgeFriction?: number
    fade?: boolean
    focusOnSelect?: boolean
    infinite?: boolean
    initialSlide?: number
    lazyLoad?: 'ondemand' | 'progressive'
    nextArrow?: ReactNode
    onEdge?(swipeDirection: string): void
    onInit?(): void
    onLazyLoad?(slidesToLoad: number[]): void
    onReInit?(): void
    onSwipe?(swipeDirection: string): void
    pauseOnDotsHover?: boolean
    pauseOnFocus?: boolean
    pauseOnHover?: boolean
    prevArrow?: ReactNode
    responsive?: ResponsiveObject[]
    rows?: number
    rtl?: boolean
    slide?: string
    slidesPerRow?: number
    slidesToScroll?: number
    slidesToShow?: number
    speed?: number
    swipe?: boolean
    swipeEvent?(swipeDirection: string): void
    swipeToSlide?: boolean
    touchMove?: boolean
    touchThreshold?: number
    useCSS?: boolean
    useTransform?: boolean
    variableWidth?: boolean
    vertical?: boolean
    verticalSwiping?: boolean
    waitForAnimate?: boolean
    children?: ReactNode
  }

  export interface ResponsiveObject {
    breakpoint: number
    settings: 'unslick' | Settings
  }

  export default class Slider extends React.Component<Settings> {
    slickNext(): void
    slickPrev(): void
    slickGoTo(slideNumber: number, dontAnimate?: boolean): void
    slickPause(): void
    slickPlay(): void
    unslick(): void
  }
}
