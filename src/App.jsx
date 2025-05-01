import { useState } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import Catalog from './components/Catalog'
import { ItemContext } from './components/ItemContext'
import villagers from './villagers.json'

function App() {
  const start = villagers.find(villager => villager.Name == "Start");
  const [itemList, setItemList] = useState(start.Items);
  const [sourceList, setSourceList] = useState([start])

  const addItem = (source) => {
    if (sourceList.includes(source)) return;

    const newSources = [...sourceList, source];

    const newItems = new Set(itemList);
    source.Items.forEach(item => newItems.add(item));

    setSourceList(newSources);
    setItemList(Array.from(newItems));
    }

  const deleteItem = (source) => {
    const newSources = sourceList.filter(s => s != source);

    const remainingItems = new Set();
    newSources.forEach(src => {
      src.Items.forEach(item => remainingItems.add(item));
    });

    setSourceList(newSources);
    setItemList(Array.from(remainingItems));
  }

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
