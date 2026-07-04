import { useState, useEffect } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import Catalog from './components/Catalog'
import { ItemContext } from './components/ItemContext'
import villagers from './villagers.json'
//import items from './items.json'
import Cookies from 'js-cookie'

/* TODO:
- Favorites list
- Override/favorite buttons on card
- Villager tooltips
- Set cover algorithm
- Furniture color variant photos
*/

function App() {
  const start = villagers.find(villager => villager.Name == "Start");
  const [itemList, setItemList] = useState(start.Items);
  const [sourceList, setSourceList] = useState([start]);
  const [villagerCount, setVillagerCount] = useState(0);
  const school = villagers.find(villager => villager.Name == "School")
  const afterSchool = villagers.find(villager => villager.Name == "6 Homes and School")
  const [overrideItems, setOverrideItems] = useState([]);
  const [catalogSource, setCatalogSource] = useState(false); // Whether player has completed 27 homes -> can access personal catalog items


  // -------------------------------------- Initialize Source + Item Lists --------------------------------------


  useEffect(() => {
    const cookieVal = Cookies.get("sourceList");
    const newItems = new Set();
    let newVillagerCount = 0;
    let extendedSources = [start]; // Fallback if cookie doesn't exist

    if (cookieVal !== undefined) {
      const cookieNameList = cookieVal.split(',');
      const loadedSources = cookieNameList
        .map(name => villagers.find(v => v.Name === name))
        .filter(Boolean);
  
      extendedSources = [...loadedSources];
  
      // Count villagers and gather items
      loadedSources.forEach(src => {
        if (src.Filename !== null) {
          newVillagerCount++;
        }
        src.Items.forEach(item => newItems.add(item));
      });
  
      if (newVillagerCount >= 6 && extendedSources.includes(school) && !sourceList.includes(afterSchool)) {
        extendedSources.push(afterSchool);
        afterSchool.Items.forEach(item => newItems.add(item));
      }

      if (newVillagerCount >= 27) {
        setCatalogSource(true)
      }
  
      setSourceList(extendedSources);
      setVillagerCount(newVillagerCount);
    }

    // Add manually-overridden items from cookie
    let overrideCookieItems = [];
    const cookieOverride = Cookies.get("overrideItems");
    if (cookieOverride !== undefined) {
      overrideCookieItems = cookieOverride.split(',');
    }

    const isCatalogActive = newVillagerCount >= 27; 
    if (isCatalogActive) {
      overrideCookieItems.forEach(item => newItems.add(item));
    }
    setOverrideItems(overrideCookieItems);
    setItemList(Array.from(newItems));

  }, []);


  // -------------------------------------- Add Items from Source --------------------------------------


  const addItem = (source) => {
    if (sourceList.includes(source)) return;

    const newItems = new Set(itemList);
    let newVillagerCount = villagerCount;

    if (source.Filename !== null) {
      newVillagerCount = villagerCount + 1;
      setVillagerCount(newVillagerCount);
    }

    let newSources = [...sourceList, source];

    if (newVillagerCount >= 6 && newSources.includes(school) && !newSources.includes(afterSchool)) {
      newSources = [...newSources, afterSchool];
      afterSchool.Items.forEach(item => newItems.add(item));
    }
    
    source.Items.forEach(item => newItems.add(item));

    const isCatalogActive = newVillagerCount >= 27;
    setCatalogSource(isCatalogActive);

    if (isCatalogActive) {
      overrideItems.forEach(item => {
        if (!newItems.has(item)) {
          newItems.add(item)
        }
      });
    }

    Cookies.set('sourceList', [...newSources.map(src => src.Name)], { expires: 7 });
    setSourceList(newSources);
    setItemList(Array.from(newItems));
  }


    // -------------------------------------- Delete Items from Source --------------------------------------


    const deleteItem = (source) => {
    if (!sourceList.includes(source)) return;

    let newVillagerCount = villagerCount;
    if (source.Filename !== null) {
      newVillagerCount = villagerCount - 1;
      setVillagerCount(newVillagerCount);
    }

    let newSources = sourceList.filter(s => s != source);
    
    // Explicitly set instead of toggling blindly
    const isCatalogActive = newVillagerCount >= 27;
    setCatalogSource(isCatalogActive);

    if (newVillagerCount < 6 || !newSources.includes(school)) {
      newSources = newSources.filter(s => s != afterSchool)
    }

    const remainingItems = new Set();
    newSources.forEach(src => {
      src.Items.forEach(item => remainingItems.add(item));
    });

    if (isCatalogActive) {
      overrideItems.forEach(i => {
        if (!remainingItems.has(i)) {
          remainingItems.add(i);
        }
      })
    }
    
    Cookies.set('sourceList', [...newSources.map(src => src.Name)], { expires: 7 });
    setSourceList(newSources);
    setItemList(Array.from(remainingItems));
  }


  // -------------------------------------- Manual Override Item (Not From Source) --------------------------------------


  const overrideItem = (item) => {
    console.log(catalogSource)
    if (itemList.includes(item.Name)) return;
    if (overrideItems.includes(item.Name)) return;

    let newOverrideItems = [...overrideItems, item.Name]
    setOverrideItems(newOverrideItems);

    if (catalogSource) {
      let newItemList = [...itemList, item.Name]
      setItemList(newItemList);
    }

    Cookies.set('overrideItems', newOverrideItems, { expires: 7 });
    console.log(catalogSource)
    console.log(newOverrideItems)
  }


  // -------------------------------------- Delete Overridden Item --------------------------------------


  const deleteOverrideItem = (item) => {
    if (!overrideItems.includes(item.Name)) return;
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

    if (refresh && catalogSource) {
      newOverrideItems.forEach(item => {
        if (!remainingItems.has(item)) {
          remainingItems.add(item);
        }
      });

    setItemList(Array.from(remainingItems));
    }

    setOverrideItems(newOverrideItems);
    Cookies.set('overrideItems', newOverrideItems, { expires: 7 });
    console.log(catalogSource)
  }

  return (
    <ItemContext.Provider value={{sourceList, itemList, villagerCount, overrideItems, addItem, deleteItem, overrideItem, deleteOverrideItem}}>
      <div className='app'>
        <Sidebar />
        <Catalog />
      </div>
    </ItemContext.Provider>
  )
}

export default App
