import React, { useState } from 'react'

const ItemOverlay = ({ item, open }) => {
  return (
    <div className={`overlay ${open ? 'open' : ''}`}>

      <div className="top-half">
        
        <img src={typeof item.Image == "string" ? item.Image : item.Image[0]} alt="Item image" />
        
        <div className="header-info">
          <h2>{item.Name}</h2>
          <h3>{item.Tab} | {item.Tag}</h3>

          <div className='info-grid'>
            <h4><em>Customize:</em> {String(item.Customize)}</h4>
            <h4><em>DIY:</em> {String(item.DIY)}</h4>
            <h4><em>Cyrus:</em> {String(item.Cyrus)}</h4>
            <h4><em>Catalog:</em> {item.Catalog}</h4>
            <h4><em>Buy Price:</em> {item.Buy}</h4>
            <h4><em>Sell Price:</em> {item.Sell}</h4>
          </div>
        </div>
      </div>

      <h4><em>HHP Unlocks</em></h4>
      <p>{typeof item["HHP Source"] == "string" ? 
        item["HHP Source"] : item["HHP Source"].join(', ')}
      </p>

      <h4><em>Source:</em> {item.Source}</h4>
      <p>{item["Source Notes"]}</p>
    </div>
  )
}

export default ItemOverlay
