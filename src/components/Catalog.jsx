import React, { useState } from 'react'
import items from '../items.json'
import Cards from './Cards'

const Catalog = () => {
  const [itemList, setItemList] = useState(items);
  const [searchItem, setSearchItem] = useState('')

  const handleInputChange = (event) => {
    const searchTerm = event.target.value;
    setSearchItem(searchTerm);
  }

  const handleSubmit = (event) => {
    event.preventDefault();
    console.log({searchItem});
    if (searchItem === '') { setItemList(items); return; }
    const filterBySearch = items.filter((item) => {
      if (item.Name.toLowerCase().includes(searchItem.toLowerCase())) {
        return item;
      }
    })
    console.log(filterBySearch);
    setItemList(filterBySearch);
  }

  return (
    <div className="catalog">
      <div className="header">
        <h2>Catalog</h2>

        <div className="filter-search">
          <button className="filter-button">
            <svg width="30" height="28" viewBox="0 0 30 28" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M28.3333 2H1.66663L12.3333 14.6133V23.3333L17.6666 26V14.6133L28.3333 2Z" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>

          <div className="search">
            <input onChange={event => setSearchItem(event.target.value)}
              type="text" 
              name="search" 
              placeholder="Search"
            />

            <button onClick={handleSubmit} className="search-button">
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 20L15.65 15.65M18 10C18 14.4183 14.4183 18 10 18C5.58172 18 2 14.4183 2 10C2 5.58172 5.58172 2 10 2C14.4183 2 18 5.58172 18 10Z"  stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
          
        </div>
      </div>

      <Cards itemList={itemList}/>
    </div>
  )
}

export default Catalog
