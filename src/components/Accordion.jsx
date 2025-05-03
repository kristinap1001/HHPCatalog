import React, { useState, useContext } from 'react'
import { ItemContext } from './ItemContext';

const Accordion = ({ title, data }) => {
  const [accordionOpen, setAccordionOpen] = useState(false);
  const [searchResults, setSearchResults] = useState(data);
  const [searchItem, setSearchItem] = useState('');
  const { villagerCount } = useContext(ItemContext);

  const handleSearch = (event) => {
    console.log(villagerCount)
    event.preventDefault();
    const currentSearch = event.target.value;
    setSearchItem(currentSearch);
    if (searchItem === '') { setSearchResults(data); return; }
    const filterBySearch = data.filter((item) => {
      if (item.key.toLowerCase().includes(currentSearch.toLowerCase())) {
        return item;
      }
    })
    setSearchResults(filterBySearch);
  }

  return (
    <div className={`accordion ${accordionOpen ? 'expanded' : ''}`}>
      <button className='accordion-button'
        onClick={() => setAccordionOpen(!accordionOpen)}
      >
        <div className="plus-minus">
          {accordionOpen ? <h3>-</h3> : <h3>+</h3>}
        </div>
        <h3>{title}</h3>
        <h3 className='count'>({villagerCount})</h3>
      </button>
      <div className='accordion-list'>
        <input 
          onChange={event => handleSearch(event)}
          type="text" 
          name="search" 
          placeholder="Search"
        />
        {searchResults}
      </div>
    </div>
  )
}

export default Accordion