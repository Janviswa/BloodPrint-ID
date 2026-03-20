import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: '#111124',
            border: '1px solid #252544',
            color: '#dde2f0',
            fontFamily: 'Outfit, sans-serif',
            fontSize: '13.5px',
          },
          success: { iconTheme: { primary: '#7bed9f', secondary: '#111124' } },
          error:   { iconTheme: { primary: '#e63946', secondary: '#111124' } },
        }}
      />
    </BrowserRouter>
  </React.StrictMode>
)
