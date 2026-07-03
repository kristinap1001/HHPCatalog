import { useState, useEffect } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import Catalog from './components/Catalog'
import { ItemContext } from './components/ItemContext'
import villagers from './villagers.json'
import items from './items.json'
import Cookies from 'js-cookie'

function App() {
  const start = villagers.find(villager => villager.Name == "Start");
  const [itemList, setItemList] = useState(start.Items);
  const [sourceList, setSourceList] = useState([start]);
  const [villagerCount, setVillagerCount] = useState(0);
  const catalogSource = villagers.find(villager => villager.Name == "From player catalog after 27th home")
  const school = villagers.find(villager => villager.Name == "School")
  const afterSchool = villagers.find(villager => villager.Name == "6 Homes and School")
  const [overrideItems, setOverrideItems] = useState([]);


  useEffect(() => {
    const cookieVal = Cookies.get("sourceList");
    const newItems = new Set();
    if (cookieVal !== undefined) {
      const cookieNameList = cookieVal.split(',');
      const loadedSources = cookieNameList
        .map(name => villagers.find(v => v.Name === name))
        .filter(Boolean);
  
      let newVillagerCount = 0;
      let extendedSources = [...loadedSources];
  
      // Count villagers and gather items
      loadedSources.forEach(src => {
        if (src.Filename !== null) {
          newVillagerCount++;
        }
        src.Items.forEach(item => newItems.add(item));
      });
  
      // Add special cases
      if (newVillagerCount >= 27 && !extendedSources.includes(catalogSource)) {
        extendedSources.push(catalogSource);
        catalogSource.Items.forEach(item => newItems.add(item));
      }
  
      if (newVillagerCount >= 6 && extendedSources.includes(school) && !sourceList.includes(afterSchool)) {
        extendedSources.push(afterSchool);
        afterSchool.Items.forEach(item => newItems.add(item));
      }
  
      setSourceList(extendedSources);
      setVillagerCount(newVillagerCount);
    }

    // Add manually-overriden items from cookie
    const cookieOverride = Cookies.get("overrideItems");
    if (cookieOverride !== undefined) {
      const cookieItemList = cookieOverride.split(',');
      const loadedItemList = cookieItemList
        .map(name => items.find(item => item.Name === name))
        .filter(Boolean);
  
      loadedItemList.forEach(item => {
        if (!newItems.has(item.Name)) {
          newItems.add(item.Name);
        }
      });

      setItemList(Array.from(newItems))
    }
  }, []);

  const addItem = (source) => {
    if (sourceList.includes(source)) return;

    const newItems = new Set(itemList);

    let newVillagerCount = villagerCount;
    // Count villagers only
    if (source.Filename !== null) {
      newVillagerCount = villagerCount+1;
      setVillagerCount(newVillagerCount);
    }

    let newSources = [...sourceList, source];

    if (newVillagerCount >= 27 && !sourceList.includes(catalogSource)) {
      newSources = [...newSources, catalogSource];
      catalogSource.Items.forEach(item => newItems.add(item));
    }

    if (newVillagerCount >= 6 && newSources.includes(school) && !newSources.includes(afterSchool)) {
      newSources = [...newSources, afterSchool];
      afterSchool.Items.forEach(item => newItems.add(item));
    }
    
    source.Items.forEach(item => newItems.add(item));

    Cookies.set('sourceList', [...newSources.map(src => src.Name)], { expires: 7 });
    setSourceList(newSources);
    setItemList(Array.from(newItems));
    console.log(sourceList);
    }

  const deleteItem = (source) => {
    if (!sourceList.includes(source)) return;

    let newVillagerCount = villagerCount;
    if (source.Filename !== null) {
      newVillagerCount = villagerCount-1;
      setVillagerCount(newVillagerCount);
    }

    // Check if <27 and <6+School requirements are still fulfilled
    let newSources = sourceList.filter(s => s != source);
    if (newVillagerCount < 27) {
      newSources = newSources.filter(s => s != catalogSource);
    }

    if (newVillagerCount < 6 | !newSources.includes(school)) {
      newSources = newSources.filter(s => s != afterSchool)
    }

    // Rebuild itemlist
    const remainingItems = new Set();
    newSources.forEach(src => {
      src.Items.forEach(item => remainingItems.add(item));
    });

    overrideItems.forEach(i => {
      if (!remainingItems.has(i)) {
        remainingItems.add(i);
      }
    })

    Cookies.set('sourceList', [...newSources.map(src => src.Name)], { expires: 7 });
    setSourceList(newSources);
    setItemList(Array.from(remainingItems));
  }

  const overrideItem = (item) => {
    if (itemList.includes(item.Name)) return;

    let newItemList = [...itemList, item.Name]
    let newOverrideItems = [...overrideItems, item.Name]

    setItemList(newItemList);
    setOverrideItems(newOverrideItems);
    Cookies.set('overrideItems', newOverrideItems, { expires: 7 });
  }

  const deleteOverrideItem = (item) => {
    if (!itemList.includes(item.Name)) return;
    let refresh = true;
    let newOverrideItems = overrideItems.filter(i => i != item.Name)

    const remainingItems = new Set();
    sourceList.forEach(src => {
      src.Items.forEach(i => {
        if(i == item.Name) {
          refresh = false; // skip refreshing of itemlist if item is already in a source's item list
        }
        remainingItems.add(i)
      });
    });

    if (refresh) {
      newOverrideItems.forEach(item => {
        if (!remainingItems.has(item)) {
          remainingItems.add(item);
        }
      });

    setItemList(Array.from(remainingItems));
    }
    console.log(remainingItems)

    setOverrideItems(newOverrideItems);
    Cookies.set('overrideItems', newOverrideItems, { expires: 7 });
    
  }

  return (
    <ItemContext.Provider value={{sourceList, itemList, villagerCount, addItem, deleteItem, overrideItem, deleteOverrideItem}}>
      <div className='app'>
        <Sidebar />
        <Catalog />
      </div>
    </ItemContext.Provider>
  )
}

export default App