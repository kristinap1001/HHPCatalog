import { useState } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import Catalog from './components/Catalog'

function App() {
  return (
    <div className='app'>
      <Sidebar />
      <Catalog />
    </div>
  )
}

export default App
