import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { ThemeProvider } from './contexts/ThemeContext'
import { registerServiceWorker } from './registerSW'
import './index.css'

// Register service worker for PWA functionality
registerServiceWorker().catch((error) => {
  console.error('Failed to register service worker:', error)
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>,
)
