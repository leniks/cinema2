import { CustomComponentProps } from '../interfaces'
import { mergeClassName } from '../utils'
import { Container } from './container'

interface Props extends CustomComponentProps {
  title?: string
  onTitleClick?: () => void
  hidden?: boolean
}

export const Section = (props: Props) => {
  if (props.hidden) return <></>

  return (
    <Container className={props.className}>
      {props.title ? (
        <h1
          onClick={props.onTitleClick}
          className={mergeClassName(
            'text-lg md:text-xl lg:text-2xl xl:text-3xl px-2 md:px-3 lg:px-4 py-1 md:py-2 lg:py-3 font-semibold',
            props.onTitleClick
              ? 'cursor-pointer hover:text-primary transition-colors'
              : '',
          )}
          dangerouslySetInnerHTML={{
            __html: props.title,
          }}
        ></h1>
      ) : (
        ''
      )}
      {props.children}
    </Container>
  )
}
