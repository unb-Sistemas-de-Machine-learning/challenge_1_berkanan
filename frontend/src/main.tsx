import { createHead, UnheadProvider } from '@unhead/react/client'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import './index.css'

const head = createHead()

createRoot(document.getElementById('root')!).render(
  <UnheadProvider head={head}>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </UnheadProvider>
)
