import React from 'react'
import ReactDOM from 'react-dom/client'
import { AppContainer } from './components/app-container'
import { App } from './App'
import './index.css'

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement)

root.render(
  <React.StrictMode>
    <AppContainer>
      <App />
    </AppContainer>
  </React.StrictMode>,
)
