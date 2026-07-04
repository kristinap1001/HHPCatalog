import { createContext } from 'react';
export const ItemContext = createContext({
  sourceList: [],
  itemList: [],
  overrideItems: [],
  villagerCount: 0,
  addItem: (source) => {},
  deleteItem: (source) => {},
  overrideItem: (item) => {},
  deleteOverrideItem: (item) => {}
});