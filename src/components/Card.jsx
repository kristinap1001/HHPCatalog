import React, { useState, useEffect, useRef, useContext } from 'react'
import { ItemContext } from './ItemContext';
import ItemOverlay from './ItemOverlay'

const Card = ({ item }) => {
  const [overlayOpen, setOverlayOpen] = useState(false);
  const { itemList } = useContext(ItemContext);

  let cardRef = useRef();

  useEffect(() => {
    try {
      let handler = (event) => {
        if (!cardRef.current.contains(event.target)) {
          setOverlayOpen(false);
        }
      };
      document.addEventListener("mousedown",handler);
    } catch (error) {
      console.log(error);
    };
  });

  return (
    <>
      <div className={`card ${itemList.includes(item.Name) ? 'unlocked' : ''}`} >
        <button className="overlay-trigger"
          onClick={() => setOverlayOpen(true)}
        ></button>
        <img src={typeof item.Image == "string" ? item.Image : item.Image[0]} alt="Item image" />
        <h4>{item.Name}</h4>
      </div>

      <div className={`overlay-background ${overlayOpen ? 'open' : ''}`}>
        <div ref={cardRef} className="overlay-container">
          <ItemOverlay item={item} open={overlayOpen}/>
        </div>
      </div>
    </>
  )
}

export default Card
