import { useState } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import Catalog from './components/Catalog'
import { ItemContext } from './components/ItemContext'
import villagers from './villagers.json'

function App() {
  const start = villagers.find(villager => villager.Name == "Start");
  const [itemList, setItemList] = useState(start.Items);
  const [sourceList, setSourceList] = useState([start]);
  const [sourceCount, setSourceCount] = useState(0);
  const catalogSource = villagers.find(villager => villager.Name == "From player catalog after 27th home")
  const school = villagers.find(villager => villager.Name == "School")
  const afterSchool = villagers.find(villager => villager.Name == "6 Homes and School")

  const addItem = (source) => {
    if (sourceList.includes(source)) return;

    let newSourceCount = sourceCount;
    // Count villagers only
    if (source.Filename !== null) {
      newSourceCount = sourceCount+1;
      setSourceCount(newSourceCount);
    }

    let newSources = [...sourceList, source];
    if (newSourceCount >= 27 && !sourceList.includes(catalogSource)) {
      newSources = [...newSources, catalogSource]
    }

    if (newSourceCount >= 6 && sourceList.includes(school)) {
      newSources = [...newSources, afterSchool]
    }

    const newItems = new Set(itemList);
    source.Items.forEach(item => newItems.add(item));

    setSourceList(newSources);
    setItemList(Array.from(newItems));
    }

  const deleteItem = (source) => {
    if (!sourceList.includes(source)) return;

    let newSourceCount = sourceCount;
    if (source.Filename !== null) {
      newSourceCount = sourceCount-1;
      setSourceCount(newSourceCount);
    }

    let newSources = sourceList.filter(s => s != source);
    if (newSourceCount < 27) {
      newSources = newSources.filter(s => s != catalogSource);
    }

    if (newSourceCount < 6 | !sourceList.includes(school)) {
      newSources = newSources.filter(s => s != afterSchool)
    }

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
