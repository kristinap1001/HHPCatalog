import pandas as pd
import json
from ast import literal_eval

villagers = pd.read_csv('preprocessing/hhp_data/paradiseplanning.csv',dtype=object)
villagers = villagers.filter(['Name','Filename','Request','Thought bubble'])
villagers['Image'] = "https://acnhcdn.com/latest/NpcIcon/" + villagers['Filename'] + ".png"
villagers.rename(columns={"Name":"Villager Name"}, inplace=True)

megaDf = pd.read_csv('preprocessing/output/allitems.csv', dtype=object)[["Name", "HHP Source"]]
megaDf.rename(columns={"Name":"Item Name"}, inplace=True)
megaDf['HHP Source'] = megaDf['HHP Source'].apply(literal_eval)
exploded = megaDf.explode('HHP Source')
reversed = exploded.groupby('HHP Source')['Item Name'].apply(list).reset_index()

villagers = pd.merge(villagers, reversed, how='outer', left_on='Villager Name', right_on='HHP Source')
villagers.drop('Villager Name', axis=1, inplace=True)
villagers.rename(columns={"HHP Source":"Name", "Item Name":"Items"}, inplace=True)

villagers.loc[(villagers['Name'] == 'School'), 'Image'] = 'https://dodo.ac/np/images/thumb/5/58/School_HHP_Icon.png/35px-School_HHP_Icon.png'
villagers.loc[(villagers['Name'] == 'Cafe'), 'Image'] = 'https://dodo.ac/np/images/thumb/5/5c/Caf%C3%A9_HHP_Icon.png/35px-Caf%C3%A9_HHP_Icon.png'
villagers.loc[(villagers['Name'] == 'Restaurant'), 'Image'] = 'https://dodo.ac/np/images/thumb/4/43/Restaurant_HHP_Icon.png/35px-Restaurant_HHP_Icon.png'
villagers.loc[(villagers['Name'] == 'Hospital'), 'Image'] = 'https://dodo.ac/np/images/thumb/0/09/Hospital_HHP_Icon.png/35px-Hospital_HHP_Icon.png'
villagers.loc[(villagers['Name'] == 'Apparel Shop'), 'Image'] = 'https://dodo.ac/np/images/thumb/4/44/Apparel_Shop_HHP_Icon.png/35px-Apparel_Shop_HHP_Icon.png'
villagers.loc[(villagers['Name'] == 'Leif Lesson'), 'Image'] = 'https://acnhcdn.com/latest/NpcIcon/slo.png'

villagers.to_json("src/villagers.json",orient='records',force_ascii=False)