import React from 'react'
import styles from './Loading.module.css'

export const Loading: React.FC = () => {
  return (
    <div className={styles.loadingContainer}>
      <div className={styles.spinner} />
    </div>
  )
}
