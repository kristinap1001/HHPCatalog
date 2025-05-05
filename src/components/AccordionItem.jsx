import React, { useState, useContext, useEffect } from 'react';
import { ItemContext } from './ItemContext';

const AccordionItem = ({ source }) => {
  const { sourceList, itemList, addItem, deleteItem } = useContext(ItemContext);
  const [selected, setSelected] = useState(false);

  const handleClick = () => {
    const status = !selected;
    setSelected(status);
    
    if (status) {
      addItem(source);
    } else if (!status) {
      deleteItem(source);
    }
  }

  useEffect(() => {
    if (sourceList.includes(source)) {
      setSelected(true);
    }
  }, [sourceList])

  return (
    <button 
      onClick={() => handleClick()}
      className={`accordion-item ${selected ? 'selected' : ''}`}
    >
      <img src={source.Image} alt="Villager image" />
      <h4>{source.Name}</h4>
    </button>
  )
}

export default AccordionItem
