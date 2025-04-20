import React from 'react'
import Cards from './Cards'

const Catalog = () => {
  return (
    <div className="catalog">
      <h2>Catalog</h2>
      <button>
        <p>Filter</p>
      </button>

      <input type="text" />

      <Cards />
    </div>
  )
}

export default Catalog
