import React from 'react'
import items from '../items.json'
import Card from './Card';

const Cards = () => {
  //todo: infinite scroll/load additional items
  const page = items.slice(0,64);
  return (
    <div className='cards'>
      {page.map((item) => (
        <Card key={item.Name} item={item} />
      ))}
    </div>
  )
}

export default Cards
