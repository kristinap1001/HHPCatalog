import React, { useState, useContext, useEffect } from 'react'
import items from '../items.json'
import Cards from './Cards'
import { ItemContext } from './ItemContext'

const Catalog = () => {

  {/* ---------- Searching ---------- */}

  const [searchResults, setSearchResults] = useState(items);
  const [searchItem, setSearchItem] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (searchItem === '') { setSearchResults(items); return; }
    const filterBySearch = items.filter((item) => {
      if (item.Name.toLowerCase().includes(searchItem.toLowerCase())) {
        return item;
      }
    })
    setSearchResults(filterBySearch);
  }

  {/* ---------- Filtering ---------- */}

  const { sourceList, itemList } = useContext(ItemContext);
  const unlockedItems = itemList;

  const [filterOpen, setFilterOpen] = useState(false);
  const [unlockedOnly, setUnlockedOnly] = useState(false);

  const filterCategories = ['Housewares','Miscellaneous','Wall-mounted','Ceiling Decor','Wallpaper','Floors','Rugs','Fashion Items','Other']
  const [filterList, setFilterList] = useState(filterCategories);

  const [finalItemList, setFinalItemList] = useState(searchResults);

  const handleOutsideClick = (event) => {
    if (!event.target.closest('.filter-menu') && !event.target.closest('.filter-button')) {
      setFilterOpen(false);
    }
  }

  useEffect(() => {
    if(filterOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
      return () => document.removeEventListener('mousedown',handleOutsideClick);
    }
  }, [filterOpen]);

  const selectAll = () => {
    if (filterList.length == filterCategories.length) {
      setFilterList([]);
    } else {
      setFilterList(filterCategories);
    }
  }

  const toggleCategory = (category) => {
    if (filterList.includes(category)) {
      setFilterList(prev => prev.filter(cat => cat !== category))
    } else {
      setFilterList(prev => [...prev, category])
    }
  }

  {/* ---------- Final List ---------- */}

  useEffect(() => {
    const lowerCaseFilters = filterList.map(str => str.toLowerCase());
    const filteredItems = searchResults.filter((item) => lowerCaseFilters.includes(item.Tab));
    let finalItems = filteredItems;
    if (unlockedOnly) {
      finalItems = filteredItems.filter((item) => unlockedItems.includes(item.Name));
    }
    setFinalItemList(prev => finalItems);
  }, [sourceList, filterList, searchResults, unlockedOnly])

  return (
    <div className="catalog">
      <div className="header">
        <h2>Catalog</h2>

        <div className="filter-search">
          <button className="filter-button"
            onClick={() => setFilterOpen(!filterOpen)}
          >
            <svg width="30" height="28" viewBox="0 0 30 28" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M28.3333 2H1.66663L12.3333 14.6133V23.3333L17.6666 26V14.6133L28.3333 2Z" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>

          <div className={`filter-menu ${filterOpen ? 'open' : ''}`}>

            {/* ---------- Unlocked Only ---------- */}

            <button
              onClick={() => setUnlockedOnly(!unlockedOnly)}
              className={`filter-item ${unlockedOnly ? 'selected' : ''}`}
            >
              <svg width="16" height="12" viewBox="0 0 16 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M13.3334 2.5L6.00002 9.83333L2.66669 6.5" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <h4>Show Unlocked Only</h4>
            </button>

            {/* ---------- Select All Categories ---------- */}
            <button
              className="filter-item"
              onClick={() => selectAll()}
            >
              <h4>Select All</h4>
            </button>


            {/* ---------- Categories ---------- */}

            {filterCategories.map((category) => (
              <button key={category}
              onClick={() => toggleCategory(category)}
              className={`filter-item ${filterList.includes(category) ? 'selected' : ''}`}
            >
              <svg width="16" height="12" viewBox="0 0 16 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M13.3334 2.5L6.00002 9.83333L2.66669 6.5" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <h4>{category}</h4>
            </button>
            ))}
          </div>

          <div className="search">
            <input 
              onChange={event => setSearchItem(event.target.value)}
              onKeyDown = {(e) => {
                if (e.key === "Enter") {handleSubmit(e);}
              }}
              type="text" 
              name="search" 
              placeholder="Search"
            />

            <button onClick={handleSubmit} className="search-button">
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 20L15.65 15.65M18 10C18 14.4183 14.4183 18 10 18C5.58172 18 2 14.4183 2 10C2 5.58172 5.58172 2 10 2C14.4183 2 18 5.58172 18 10Z"  stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
          
        </div>
      </div>

      <Cards itemList={finalItemList}/>
    </div>
  )
}

export default Catalog
