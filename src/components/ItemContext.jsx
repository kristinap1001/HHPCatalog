import { createContext } from 'react';
export const ItemContext = createContext({
  sourceList: [],
  itemList: [],
  addItem: (source) => {},
  deleteItem: (source) => {}
});