import { ReactNode } from 'react'

interface Props {
  children: ReactNode
  className?: string
}

export const Container = ({ children, className = '' }: Props) => {
  return (
    <div
      className={`mx-auto max-w-screen-md lg:max-w-screen-lg xl:max-w-screen-xl 2xl:max-w-screen-2xl px-4 md:px-6 lg:px-8 xl:px-12 2xl:px-16 py-2 md:py-3 lg:py-4 xl:py-6 ${className}`}
    >
      {children}
    </div>
  )
}
