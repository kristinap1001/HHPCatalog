import { useState, useContext, useEffect } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import Catalog from './components/Catalog'
import { ItemContext } from './components/ItemContext'
import villagers from './villagers.json'

function App() {
  const start = villagers.filter(villager => villager.Name == "Start")[0];
  const [itemList, setItemList] = useState(start.Items);
  const [sourceList, setSourceList] = useState([start])

  const addItem = (source) => {
    // Add source to sourceList
    if (!sourceList.includes(source)) {
      setSourceList(prev => [...prev, source]);
    }
    // Add items unlocked by source to itemList
    let newList = [];
    for (let i=0; i<source.Items.length; i++) {
      if (!itemList.includes(source.Items[i])) {
        newList.push(source.Items[i]);
      }
    }
    setItemList((prev) => [...prev, ...newList]);
  }

  const deleteItem = (source) => {
    // Remove source from sourceList
    setSourceList(prev => prev.filter(item => item !== source))

    // Remove items unlocked by source from itemList
    for (let i=0; i<source.Items.length; i++) {
      const index = itemList.indexOf(source.Items[i])
      if (index !== -1) {
        setItemList(prev => prev.filter(item => item !== source.Items[i]));
      }
    }
  }

  // Ensure itemList is up to date with sourceList
  const refreshItemList = () => {
    for (let i=0; i<sourceList.length; i++) {
      addItem(sourceList[i]);
    }
  }
  useEffect(() => refreshItemList(), [sourceList])

  return (
    <ItemContext.Provider value={{sourceList, itemList, addItem, deleteItem}}>
      <div className='app'>
        <Sidebar />
        <Catalog />
      </div>
    </ItemContext.Provider>
  )
}

export default App
