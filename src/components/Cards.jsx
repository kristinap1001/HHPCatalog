import React from 'react'
import items from '../items.json'
import Card from './Card';

const Cards = ({ itemList }) => {
  //todo: infinite scroll/load additional items
  const page = itemList.slice(0,128);
  return (
    <div className='cards'>
      {page.map((item) => (
        <Card key={item.Name} item={item} />
      ))}
    </div>
  )
}

export default Cards
