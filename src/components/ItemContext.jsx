import { createContext } from 'react';
export const ItemContext = createContext({
  sourceList: [],
  itemList: [],
  villagerCount: 0,
  addItem: (source) => {},
  deleteItem: (source) => {}
});