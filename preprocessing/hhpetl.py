# type: ignore[reportUndefinedVariable] (pylance doesn't recognize variables declared via globals()[varName])

"""
Script for extracting data from the ACNH Spreadsheet project, chibisnorlax, and Stoney9215; cleaning up erroneous data & filling in 
missing data; and formatting it for use in the web app
"""

import warnings
import os, os.path
import pandas as pd
import re
import json

# ignore pandas FutureWarning for now (will fix CoW issues for pandas 3.0 later)
warnings.simplefilter(action='ignore', category=FutureWarning)

# Pandas print options
pd.set_option('display.max_rows', 0)
pd.set_option('display.max_columns', 5)
pd.set_option('display.width', 0)

# Function to print dictionaries w/ lists as values in a more concise and readable way
def printDict(dic):
	for key,value in dic.items():
		print(key + ": " + ", ".join(value))

# To convert string values in column to list containing string
def listConvert(val):
  if isinstance(val,list):
    return val
  return [val]

# ================================================== Import and fix villager & facility unlocks ==================================================

# Import HHP furniture lists
villagerUnlocks = pd.read_csv('preprocessing/hhp_data/furniture-per-villager.csv',dtype=object)
facilityUnlocks = pd.read_csv('preprocessing/hhp_data/furniture-per-facility.csv',dtype=object)

# typo in facilities csv
facilityUnlocks['English Name (added)'].replace('tee with silicon bib', 'tee with silicone bib', inplace=True)

# Dict mapping villagers to their furniture lists
villToFurn = {
	row["Villager"]: [i for i in row.drop(["ID","Label","Villager"]).tolist() if not pd.isna(i)]
	for _, row in villagerUnlocks.iterrows()
}

# wrangling the messy facilities csv
facilities = ["School", "Cafe", "Restaurant", "Hospital", "Apparel Shop", "Start", "Leif Lesson", "6 Homes and School"]
for facility in facilities:
    villToFurn[facility] = []

for _, row in facilityUnlocks.iterrows():
	if str(row["Variation Name (added)"]) not in ["nan","No Variations"]:
		itemName = row['English Name (added)'] + " (" + row['Variation Name (added)'] + ")"
	else:
		itemName = row["English Name (added)"]
	for facility in facilities:
		if row[facility] == '1' and itemName not in villToFurn[facility]:
			villToFurn[facility].append(itemName)

# Fixing required furniture items that don't include colors
villToFurn['Peck'].remove('sporty shades')
villToFurn['Peck'] = villToFurn['Peck'] + ['sporty shades (White)']

villToFurn['Beau'].remove('basket bag')
villToFurn['Beau'] = villToFurn['Beau'] + ['basket bag (Light brown)']

villToFurn['Lucky'].remove('King Tut mask')

villToFurn['Elmer'].remove('no-show socks')
villToFurn['Elmer'] = villToFurn['Elmer'] + ['no-show socks (Light blue)']

villToFurn['Elise'].remove('oval glasses')

villToFurn['Quinn'].remove('acid-washed jacket')
villToFurn['Quinn'] = villToFurn['Quinn'] + ['acid-washed jacket (Black)']

villToFurn['Bangle'].remove('leopard tee')

# Dict mapping furniture to villagers that unlock it
furnToVill = {}
for vill,furnList in villToFurn.items():
	for furn in furnList:
		if furn not in furnToVill:
			furnToVill[furn] = [vill]
		else:
			furnToVill[furn].append(vill)

# ================================================== Importing ACNH data ==================================================

# Rename csvs (only need to do once)
for filename in os.listdir('preprocessing/acnh_data'):
	if filename.startswith('Data Spreadsheet'):
		newName = filename[52:] # "Data Spreadsheet..." prefix is 52 characters long
	else:
		newName = filename
	newName = newName.lower().replace(" ","")
	os.rename('preprocessing/acnh_data/'+filename, 'preprocessing/acnh_data/'+newName)

# Create dataframes
varList = []
dfList = []
for filename in os.listdir('preprocessing/acnh_data'):
	varName = os.path.splitext(filename)[0] # removes '.csv'
	data = pd.read_csv('preprocessing/acnh_data/'+filename,dtype=object)
	globals()[varName] = data

	# Add column with the category/"tab" name
	globals()[varName]["Tab"] = varName

	# Lists of dfs and their names
	varList.append(varName)
	dfList.append(globals()[varName])

# ================================================== Removing items that can't be used in HHP ==================================================

# 'Other' table has different filename columns
other.rename({"Storage Filename": "Filename"}, axis=1, inplace=True)
# Storage image file does not exist for plants, use inventory image instead
other.loc[(other['Tag'] == 'Plants') & (other['Name'].str.contains(r"\b(?:bush|plant|tree)\b")), 'Filename'] = other['Inventory Filename']
# 'Unnecessary' items (permits, recipe sets, tent kits, etc) are not in HHP building catalog
other.drop(other[other['Tag'] == 'Unnecessary'].index, inplace=True)

# Set-up kits, Jingle bag, & May Day worn axe (excluding Kiki & Lala wand and timer)
toolsgoods.loc[toolsgoods['Name'] == 'Kiki & Lala wand', 'Catalog'] = 'Promotion'
toolsgoods.drop(toolsgoods[(toolsgoods['Catalog'] == 'Not in catalog') & ~(toolsgoods['Name'] == 'timer')].index, inplace=True)

# Non-Sanrio posters
# villager photos/posters can be used in HHP, but unnecessary for this project as they're unlocked by their respective villagers and thus pretty self-explanatory
posters.drop(posters[~posters['Name'].str.contains(r"\b(?:Pompompurin|My Melody|Cinnamoroll|Hello Kitty|Kerokerokeroppi|Kiki & Lala)\b")].index, inplace=True)

# Hazure songs
music.drop(music[music['Catalog'] == 'Not in catalog'].index, inplace=True)

# ================================================== Combining everything into one table & fixing columns ==================================================

# Create dataframe with all items
megaDf = pd.concat(dfList,ignore_index=True)
# megaDf.to_csv("output/mega.csv")

# Change customize, Cyrus, and DIY columns to bools
megaDf['Customize'] = megaDf['Kit Cost'].notnull()
megaDf['Cyrus'] = megaDf['Cyrus Customize Price'].notnull()
megaDf['DIY'] = megaDf['DIY'].map({'Yes':True,'No':False}).astype(bool)

# Remove unnecessary columns (most of them)
megaDf = megaDf.filter(['Filename','Name','Variation','Pattern','DIY','Buy','Sell','Source','Source Notes','Catalog','Tab','Tag','Customize','Cyrus'])

# Create image link from filename
megaDf['Image'] = "https://acnhcdn.com/latest/FtrIcon/" + megaDf['Filename'] + ".png"
# Use menu icon instead for plants that don't have an inventory image
megaDf.loc[(megaDf['Tag'] == 'Plants') & 
		   (megaDf['Name'].str.contains(r"\b(?:bush|plant|tree)\b")), 'Image'] = "https://acnhcdn.com/latest/MenuIcon/" + megaDf['Filename'] + ".png"

megaDf.drop('Filename',axis=1,inplace=True) # Don't need filename anymore

# Move posters to wallmounted tab
megaDf.loc[megaDf['Tab'] == 'posters' 'Tag'] = 'Posters'
megaDf.loc[megaDf['Tab'] == 'posters' 'Tab'] = 'wallmounted'

megaDf.loc[megaDf['Catalog'] == 'Not in catalog', 'Catalog'] = 'Promotion' # for some reason Sanrio, Mario, & Pocket Camp items say "not in catalog"
megaDf['Catalog'].fillna("Not in catalog", inplace=True)

# Remove 'NFS' in buy column to change data type to int
megaDf.loc[megaDf['Buy'] == 'NFS', 'Buy'] = None
megaDf['Buy'] = megaDf['Buy'].astype('Int64')
megaDf['Sell'] = megaDf['Sell'].astype('Int64')

# ================================================== Adding variations to clothing names to match dictionary ==================================================

# Fix incorrect naming for multi-variation items before adding variations to names
megaDf['Name'].replace('explorer shirt', 'explorer tee', inplace=True)

# Make naming convention of clothing match the hhp dataset
clothing = ['accessories','bags','bottoms','clothingother','dressup','headwear','tops','umbrellas','socks','shoes']
megaDf.loc[megaDf['Tab'].isin(clothing) & ~megaDf['Variation'].isna(), 'Name'] = megaDf['Name'] + " (" + megaDf['Variation'] + ")"

# Fix any remaining items lacking variations and incorrect names
megaDf['Name'].replace({
    "welding mask": "welding mask (Red)",
    "matronly bun": "matronly bun (Hair Color)",
    "Noh mask": "Noh mask (White)",
    "gold helmet": "gold helmet (Gold)",
    "knight's helmet": "knight's helmet (Gray)",
    "composer's wig": "composer's wig (Hair Color)",
    "visual-punk wig": "visual-punk wig (Hair Color)",
    "skeleton hood": "skeleton hood (White)",
    "King Tut mask": "King Tut mask (Gold)",
    "curly mustache": "curly mustache (Hair Color)",
    "space helmet": "space helmet (White)",
    "mohawk wig": "mohawk wig (Hair Color)",
    "pompadour wig": "pompadour wig (Hair Color)",
    "Nook Inc. snorkel": "Nook Inc. snorkel (Blue)",
    "conch": "spiral shell",
    "hot-dog hood": "hot-dog hood (Red)",
    "hockey mask": "hockey mask (White)",
    "paper-bag hood": "paper-bag hood (Beige)",
    "stagehand hat": "stagehand hat (Black)",
    "handlebar mustache": "handlebar mustache (Hair Color)"
}, inplace=True)

# Incorrect names in dictionary
furnToVill['log chair'] = furnToVill.pop('log sofa')
furnToVill['fish-and-chips'] = furnToVill.pop('fish and chips')
furnToVill["pesce all'acqua pazza"] = furnToVill.pop("pesce all&apos;acqua pazza")
furnToVill['paper-bag hood (Beige)'] = furnToVill.pop('paper bag (Beige)')

# Combine clothing into one tab, tag becomes old tab
megaDf.loc[megaDf['Tab'].isin(clothing), 'Tag'] = megaDf['Tab']
megaDf.loc[megaDf['Tab'].isin(clothing), 'Tab'] = 'clothing'

# ================================================== Grouping variations together for all other items ==================================================

# Consolidate patterns into variations
megaDf.loc[~megaDf['Pattern'].isna(), 'Variation'] = megaDf['Variation'] + " + " + megaDf['Pattern']
megaDf.loc[megaDf['Variation'].isna(), 'Variation'] = megaDf['Pattern']
megaDf.drop('Pattern',axis=1,inplace=True)

# Including columns with all null values (0 unique values) in subset will result in some variations not getting grouped together properly
# The only exception is 'Sell' because no items without a sell price have variations, and 'Sell' is needed to differentiate genuine artworks
groupCols = ['Name','DIY','Sell','Source','Catalog','Tab','Customize','Cyrus']

# Group by all columns except 'Variation' and 'Image', consolidating 'Variation' and 'Image' into lists
groupedMegaDf = megaDf.groupby(groupCols,as_index=False)[["Variation","Image"]].agg({
    	# Single variations remain strings, not single-item lists
        "Variation": lambda x: x.iloc[0] if len(x) == 1 else list(x),
        "Image": lambda x: x.iloc[0] if len(x) == 1 else list(x),
    })

# Merge the grouped data back to the original DataFrame
mergeDf = pd.merge(megaDf, groupedMegaDf, on=groupCols, how='left', suffixes=('', '_grouped'))

# Replace original columns with the grouped lists where applicable
mergeDf['Variation'] = mergeDf['Variation_grouped'].combine_first(mergeDf['Variation'])
mergeDf['Image'] = mergeDf['Image_grouped'].combine_first(mergeDf['Image'])

# Drop the intermediate columns used for grouping
mergeDf.drop(['Variation_grouped', 'Image_grouped'], axis=1, inplace=True)
# Remove duplicate rows while keeping consolidated lists
megaDf = mergeDf.drop_duplicates(subset=[col for col in mergeDf.columns if col not in ['Variation', 'Image']])
# Remove duplicate simple wooden fence
megaDf.drop(megaDf.index[(megaDf['Name'] == "simple wooden fence") & (megaDf['Source Notes'].isnull())], inplace=True)

# ================================================ Adding "photo studio" items not in original acnh datasets ================================================

# Combine flower bags into "seed bag"
oldBags = megaDf['Name'].str.contains('bag') & (megaDf['Source'] == "Nook's Cranny; Leif")
megaDf = megaDf[~oldBags]
seedBag = {
	'Name': 'seed bag',
    'DIY': False,
    'Buy': 240,
    'Sell': 60,
    'Source': "Nook's Cranny; Leif",
    'Tab': 'other',
    'Tag': 'Plants',
    'Customize': False,
    'Cyrus': False,
    'Image': 'https://acnhcdn.com/latest/FtrIcon/PhotoStudioSeedBag.png'
}
seedBag = pd.DataFrame([seedBag])
megaDf = pd.concat([megaDf,seedBag],ignore_index=True)

# Combine shrub starts
shrubs = ['blue-hydrangea','holly','orange-tea-olive','pink-azalea','pink-camellia','pink-hydrangea','pink-plumeria','red-camellia','red-hibiscus',
		  'white-azalea','white-plumeria','yellow-hibiscus','yellow-tea-olive']
shrubRe = "|".join(re.escape(item) for item in shrubs)
oldShrubStarts = megaDf['Name'].str.contains(shrubRe) & (megaDf['Source'] == "Leif")
megaDf = megaDf[~oldShrubStarts]
shrubStart = {
	'Name': 'shrub start',
    'DIY': False,
    'Buy': 280,
    'Sell': 70,
    'Source': "Leif",
    'Tab': 'other',
    'Tag': 'Plants',
    'Customize': False,
    'Cyrus': False,
    'Image': 'https://acnhcdn.com/latest/FtrIcon/SeedHydrangeaBlue.png'
}
shrubStart = pd.DataFrame([shrubStart])
megaDf = pd.concat([megaDf,shrubStart],ignore_index=True)

# Combine produce starts
produce = ['carrot','pumpkin','sugarcane','tomato','wheat']
produceRe = "|".join(re.escape(item) for item in produce)
oldProduce = megaDf['Name'].str.contains(produceRe) & (megaDf['Source'] == "Leif")
megaDf = megaDf[~oldProduce]
produceStart = {
	'Name': 'produce start',
    'DIY': False,
    'Buy': 280,
    'Sell': 70,
    'Source': "Leif",
    'Tab': 'other',
    'Tag': 'Plants',
    'Customize': False,
    'Cyrus': False,
    'Image': 'https://acnhcdn.com/latest/FtrIcon/SeedCarrot.png'
}
produceStart = pd.DataFrame([produceStart])
megaDf = pd.concat([megaDf,produceStart],ignore_index=True)

# Other items that are only obtainable in editing mode
wallpaperItem = {
	'Name': 'wallpaper',
	'DIY': False,
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Etc',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/PhotoStudioWall.png'
}
flooringItem = {
	'Name': 'flooring',
	'DIY': False,
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Etc',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/PhotoStudioFloor.png'
}
recipeItem = {
	'Name': 'recipe',
	'DIY': False,
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Etc',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/PhotoStudioRecipe.png'
}
rock = {
	'Name': 'rock',
	'DIY': False,
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/GardenEditStone.png'
}
hardwoodStump = {
	'Name': 'hardwood-tree stump',
	'DIY': False,
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/GardenEditTreeOakStump.png'
}
cedarStump = {
	'Name': 'cedar-tree stump',
	'DIY': False,
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/GardenEditTreeCedarStump.png'
}
coconutStump = {
	'Name': 'coconut-tree stump',
	'DIY': False,
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/GardenEditTreePalmStump.png'
}
bambooStump = {
	'Name': 'cut bamboo',
	'DIY': False,
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/GardenEditTreeBambooStump.png'
}
decorCedar = {
	'Name': 'decorated cedar tree',
	'DIY': False,
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/GardenEditTreeCedarDeco.png'
}

decorModeItems = pd.DataFrame([wallpaperItem,flooringItem,recipeItem,rock,hardwoodStump,cedarStump,coconutStump,bambooStump,decorCedar])
megaDf = pd.concat([megaDf,decorModeItems],ignore_index=True)

# ====================================== Mapping dictionary of villager furniture lists and checking for missing items ======================================

# Add list of villagers/facilities to each item
megaDf['HHP Source'] = megaDf['Name'].map(furnToVill)

# missing = [i for i in furnToVill if i not in megaDf['Name'].tolist() and "'s poster" not in i and "'s photo" not in i]
# print(missing) # bivalve (scallop), goldfish, killifish, crawfish
# critter tables are outside the scope of this project (the vast majority aren't HHP unlockable)

# Remove villager lists from fake artworks and add "Fake" to names
megaDf.loc[(megaDf['Tab'] == 'artwork') & (megaDf['Sell'].isna()), 'HHP Source'] = None
megaDf.loc[(megaDf['Tab'] == 'artwork') & (megaDf['Sell'].isna()), 'Name'] = megaDf['Name'] + ' (Fake)'

# Fill in HHP sources aside from villagers/facilities
megaDf['HHP Source'].fillna("From player catalog after 27th home", inplace=True)

# Remove everything else if "Start" is a source
megaDf.loc[(megaDf['HHP Source'].apply(lambda x: 'Start' in x)), 'HHP Source'] = "Start"

# Replace all string values with lists
megaDf['HHP Source'] = megaDf['HHP Source'].apply(listConvert)

# ================================================== Organizing data in order of in-game catalog ==================================================

# Statues in housewares/miscellaneous
megaDf.loc[(megaDf['Tab'] == 'artwork') & (megaDf['Name'].str.contains(r"\b(?:ancient|mystic)\b")), 'Tab'] = 'miscellaneous'
megaDf.loc[(megaDf['Tab'] == 'artwork') & (megaDf['Name'].str.contains("statue")), 'Tab'] = 'housewares'
# Paintings in housewares/wall-mounted
megaDf.loc[(megaDf['Tab'] == 'artwork') & (megaDf['Name'].str.contains("wild painting")), 'Tab'] = 'housewares'
megaDf.loc[(megaDf['Tab'] == 'artwork') & (megaDf['Name'].str.contains("painting")), 'Tab'] = 'wallmounted'

# Fencing, music, toolsgoods in Other
megaDf.loc[(megaDf['Tab'] == 'fencing'), 'Tag'] = 'fencing'
megaDf.loc[(megaDf['Tab'] == 'fencing'), 'Tab'] = 'other'
megaDf.loc[(megaDf['Tab'] == 'music'), 'Tag'] = 'music'
megaDf.loc[(megaDf['Tab'] == 'music'), 'Tab'] = 'other'
megaDf.loc[(megaDf['Tab'] == 'toolsgoods'), 'Tag'] = 'toolsgoods'
megaDf.loc[(megaDf['Tab'] == 'toolsgoods'), 'Tab'] = 'other'

# posters in wall-mounted
megaDf.loc[(megaDf['Tab'] == 'posters'), 'Tag'] = 'Posters'
megaDf.loc[(megaDf['Tab'] == 'posters'), 'Tab'] = 'wallmounted'

# rename tabs
megaDf.loc[(megaDf['Tab'] == 'wallmounted'), 'Tab'] = 'wall-mounted'
megaDf.loc[(megaDf['Tab'] == 'ceilingdecor'), 'Tab'] = 'ceiling decor'
megaDf.loc[(megaDf['Tab'] == 'clothing'), 'Tab'] = 'fashion items'

# specify tab order to match in-game
megaDf['Tab'] = pd.Categorical(megaDf['Tab'], ['housewares','miscellaneous','wall-mounted','ceiling decor','wallpaper','floors','rugs','fashion items','other','artwork'])
megaDf.sort_values(['Tab','Tag','Name'],inplace=True)
 
# ================================================== Exporting finished dataset ==================================================

#print(megaDf[megaDf['Name']=='framed poster'])
#megaDf.info()

# For viewing & searching in excel/google sheets
megaDf.to_csv("preprocessing/output/allitems.csv", index=False)

# For use in frontend
megaDf.to_json("src/items.json",orient='records',force_ascii=False)