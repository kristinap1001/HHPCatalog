import pandas as pd
import json

villagers = pd.read_csv('preprocessing/hhp_data/paradiseplanning.csv',dtype=object)
villagers = villagers.filter(['Name','Filename','Request','Thought bubble'])
villagers['Image'] = "https://acnhcdn.com/latest/NpcIcon/" + villagers['Filename'] + ".png"

villagers.to_json("src/villagers.json",orient='records',force_ascii=False)