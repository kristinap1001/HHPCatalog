import React, { useState, useEffect } from 'react'
import ItemOverlay from './ItemOverlay';
import Card from './Card';

const Cards = ({ itemList }) => {

  {/* ---------- Card Overlay ---------- */}

  const [activeItem, setActiveItem] = useState(null);

  const handleOutsideClick = (event) => {
    if (!event.target.closest('.overlay')) {
      setActiveItem(null);
    }
  }

  useEffect(() => {
    if(activeItem) {
      document.addEventListener('mousedown', handleOutsideClick);
      return () => document.removeEventListener('mousedown',handleOutsideClick);
    }
  }, [activeItem]);

  {/* ---------- Pagination ---------- */}
  
  const numItems = itemList.length;
  const [numCards, setNumCards] = useState(0);
  const [pageNumber, setPageNumber] = useState(1);
  const [page, setPage] = useState(itemList.slice(0,numCards));
  const [pageInput, setPageInput] = useState("");
  const numPages = Math.ceil(numItems/numCards);
 
  useEffect(() => {
    // Renders max. 16 rows of cards based on number of columns that can fit on screen
    const grid = window.getComputedStyle(document.querySelector('.cards'),null);
    const cols = grid.getPropertyValue("grid-template-columns").split(" ").length;
    setNumCards(numCards => cols*16);
    setPageNumber(pageNumber => 1);
    setPage(page => itemList.slice(0,numCards))
  }, [])

  useEffect(() => {
    // Re-render page & number of pages when itemList is updated
    if (numItems == 0) {
      setPageNumber(1)
      setPage(itemList.slice(0, numCards))

    } else if (pageNumber > numPages) {
      setPageNumber(numPages);
      setPage(itemList.slice((numPages-1)*numCards, numPages*numCards));

    } else {
      setPage(itemList.slice((pageNumber-1)*numCards, pageNumber*numCards))
    }
    
  }, [itemList])

  const changePage = (newNum) => {
    const newInt = parseInt(newNum,10);
    if (newInt <= numPages && 1 <= newInt) {
      setPageNumber(pageNumber => newInt);
      setPage(page => itemList.slice((newNum-1)*numCards, newNum*numCards))
    }
  }

  return (
    <>
      {/* ---------- Cards Grid ---------- */}

      <div className='cards'>
        {page.map((item) => (
          <Card key={item.Name} item={item} onOpenOverlay={() => setActiveItem(item)}/>
        ))}
      </div>
      
      {/* ---------- Card Overlay ---------- */}

      {activeItem && (
        <div className='overlay-background'>
          <ItemOverlay item={activeItem}/>
        </div>
      )}
      
      {/* ---------- Pagination ---------- */}

      <div className={`pagination ${numPages>1 ? 'active' : ''}`}>

        <button onClick={() => changePage(pageNumber-1)}>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path fillRule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0"/>
          </svg>
        </button>

        <input 
          type="number" 
          name="Page Number"
          min="1"
          max={numPages}
          value={pageInput}
          placeholder={pageNumber}
          onChange={(e) => setPageInput(e.target.value)}
          onKeyDown = {(e) => {
              if (e.key === "Enter") {
                changePage(e.target.value);
                setPageInput('');
              }
            }
          }
        />
        <p>/{numPages}</p>

        <button onClick={() => changePage(pageNumber+1)}>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path fillRule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708"/>
          </svg>
        </button>

      </div>
    </>
  )
}

export default Cards
