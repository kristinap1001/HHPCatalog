import React from 'react'

const Card = ({ item }) => {
  return (
    <div className="card">
      <img src={typeof item.Image == "string" ? item.Image : item.Image[0]} alt="Item image" />
      <h3>{item.Name}</h3>
    </div>
  )
}

export default Card
