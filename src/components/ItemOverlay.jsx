import React, { useContext } from 'react'
import villagers from '../villagers.json'
import { ItemContext } from './ItemContext';

const ItemOverlay = ({ item }) => {
  const { sourceList } = useContext(ItemContext);
  const sourceStrings = item["HHP Source"].join(', ');
  const itemSources = villagers.filter((villager) => sourceStrings.includes(villager.Name));

  return (
    <div className="overlay">

      <div className="top-half">
        
        <img src={typeof item.Image == "string" ? item.Image : item.Image[0]} alt="Item image" />
        
        <div className="header-info">
          <h2>{item.Name}</h2>
          <h3>{item.Tab} | {item.Tag}</h3>

          <div className='info-grid'>
            <h4 className={`${item.Customize ? 'true' : 'false'}`}><em>Customize:</em> {String(item.Customize)}</h4>
            <h4 className={`${item.DIY ? 'true' : 'false'}`}><em>DIY:</em> {String(item.DIY)}</h4>
            <h4 className={`${item.Cyrus ? 'true' : 'false'}`}><em>Cyrus:</em> {String(item.Cyrus)}</h4>
            <h4><em>Catalog:</em> {item.Catalog}</h4>
            <h4><em>Buy Price:</em> {item.Buy === null ? "N/A" : item.Buy}</h4>
            <h4><em>Sell Price:</em> {item.Sell === null ? "N/A" : item.Sell}</h4>
          </div>
        </div>
      </div>

      <h4><em>HHP Unlocks</em></h4>

      <div className="source-list">
        {itemSources.map((src) => (
          <div className={`source ${sourceList.includes(src) ? 'owned' : ''}`} key={src.Name}>
            <img src={src.Image} alt="Villager image" />
            <p>{src.Name}</p>
          </div>
        ))}
      </div>

      <h4><em>Source:</em> {item.Source}</h4>
      <p>{item["Source Notes"]}</p>
    </div>
  )
}

export default ItemOverlay
