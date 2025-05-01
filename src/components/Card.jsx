import React, { useContext } from 'react'
import { ItemContext } from './ItemContext';

const Card = ({ item, onOpenOverlay }) => {
  const { itemList } = useContext(ItemContext);

  return (
    <>
      <div className={`card ${itemList.includes(item.Name) ? 'unlocked' : ''}`} >
        <button className="overlay-trigger"
          onClick={onOpenOverlay}
        ></button>
        <img src={typeof item.Image == "string" ? item.Image : item.Image[0]} alt="Item image" />
        <h4>{item.Name}</h4>
      </div>
    </>
  )
}

export default Card
