import os, os.path
import pandas as pd

def printDict(dic):
	for key,value in dic.items():
		print(key + ": " + ", ".join(value))

# Pandas print options
pd.set_option('display.max_rows', 0)
pd.set_option('display.max_columns', 0)
pd.set_option('display.width', 0)

# ================================================== Importing ACNH data ==================================================

# Rename csvs (only need to do once)
for filename in os.listdir('acnh_data'):
	if filename.startswith('Data Spreadsheet'):
		newName = filename[52:] # "Data Spreadsheet..." prefix is 52 characters long
	else:
		newName = filename
	newName = newName.lower().replace(" ","")
	os.rename('acnh_data/'+filename, 'acnh_data/'+newName)

# Create dataframes
varList = []
dfList = []
for filename in os.listdir('acnh_data'):
	varName = os.path.splitext(filename)[0] # removes '.csv'
	data = pd.read_csv('acnh_data/'+filename,dtype=object)
	globals()[varName] = data

	# Add column with the category/"tab" name
	globals()[varName]["Tab"] = varName

	# Lists of dfs and their names
	varList.append(varName)
	dfList.append(globals()[varName])

print(varList)

# ================================================== Removing items that can't be used in HHP ==================================================

# 'Other' table has different filename columns
other.rename({"Storage Filename": "Filename"}, axis=1, inplace=True)
# Storage image file does not exist for plants, use inventory image instead
other.loc[(other['Tag'] == 'Plants') & (other['Name'].str.contains(r"\b(bush|plant|tree)\b")), 'Filename'] = other['Inventory Filename']
# 'Unnecessary' items (permits, recipe sets, tent kits, etc) are not in HHP building catalog
other.drop(other[other['Tag'] == 'Unnecessary'].index, inplace=True)

# Set-up kits, Jingle bag, May Day worn axe
toolsgoods.drop(toolsgoods[toolsgoods['Catalog'] == 'Not in catalog'].index, inplace=True)

# Hazure songs
music.drop(music[music['Catalog'] == 'Not in catalog'].index, inplace=True)

# HHP uniforms
tops.drop(tops[tops['Source Notes'] == 'Only available as a work clothes for Paradise Planning'].index, inplace=True)
dressup.drop(dressup[dressup['Source Notes'] == 'Only available as a work clothes for Paradise Planning'].index, inplace=True)

# ================================================== Villager & facility unlocks ==================================================

# Import HHP furniture lists
villagerUnlocks = pd.read_csv('hhp_data/furniture-per-villager.csv',dtype=object)
facilityUnlocks = pd.read_csv('hhp_data/furniture-per-facility.csv',dtype=object)

# typo in facilities csv
facilityUnlocks.loc[facilityUnlocks['English Name (added)'] == "tee with silicon bib", 'English Name (added)'] = "tee with silicone bib"

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

# ================================================== Combining everything into one table ==================================================

# Create dataframe with all items
megaDf = pd.concat(dfList,ignore_index=True)
#megaDf.to_csv("output/mega.csv")

# Customize/Cyrus customize booleans
megaDf['Customize'] = megaDf['Kit Cost'].notnull()
megaDf['Cyrus'] = megaDf['Cyrus Customize Price'].notnull()

# Remove unnecessary columns (most of them)
megaDf = megaDf.filter(['Filename','Name','Variation','Pattern','DIY','Buy','Sell','Source','Source Notes','Catalog','Tab','Tag','Customize','Cyrus'])

# Create image link from filename
megaDf['Image'] = "https://acnhcdn.com/latest/FtrIcon/" + megaDf['Filename'] + ".png"
# Use menu icon instead for plants that don't have an inventory image
megaDf.loc[(megaDf['Tag'] == 'Plants') & (megaDf['Name'].str.contains(r"\b(bush|plant|tree)\b")), 'Image'] = "https://acnhcdn.com/latest/MenuIcon/" + megaDf['Filename'] + ".png"
megaDf.drop('Filename',axis=1,inplace=True) # Don't need filename anymore

# Make naming convention of clothing match the hhp dataset
clothing = ['accessories','bags','bottoms','clothingother','dressup','headwear','tops','umbrellas','socks','shoes']
megaDf.loc[megaDf['Tab'].isin(clothing) & ~megaDf['Variation'].isna(), 'Name'] = megaDf['Name'] + " (" + megaDf['Variation'] + ")"

# Combine clothing into one tab, tag becomes old tab
megaDf.loc[megaDf['Tab'].isin(clothing), 'Tag'] = megaDf['Tab']
megaDf.loc[megaDf['Tab'].isin(clothing), 'Tab'] = 'clothing'

# Consolidate patterns into variations
megaDf.loc[~megaDf['Pattern'].isna(), 'Variation'] = megaDf['Variation'] + " + " + megaDf['Pattern']
megaDf.loc[megaDf['Variation'].isna(), 'Variation'] = megaDf['Pattern']
megaDf.drop('Pattern',axis=1,inplace=True)

# Group by all columns except 'Variation' and 'Image', consolidating 'Variation' and 'Image' into lists
groupedMegaDf = (
    megaDf.groupby(
        [col for col in megaDf.columns if col not in ["Variation", "Image"]], as_index=False
    ).agg({
    	# Single variations remain strings, not single-item lists
        "Variation": lambda x: x.iloc[0] if len(x) == 1 else list(x),
        "Image": lambda x: x.iloc[0] if len(x) == 1 else list(x),
    })
)
# Merge the grouped data back to the original DataFrame
mergeDf = pd.merge(
    megaDf, groupedMegaDf, 
    on=[col for col in megaDf.columns if col not in ["Variation", "Image"]], 
    how='left', 
    suffixes=('', '_grouped')
)
# Replace original columns with the grouped lists where applicable
mergeDf['Variation'] = mergeDf['Variation_grouped'].combine_first(mergeDf['Variation'])
mergeDf['Image'] = mergeDf['Image_grouped'].combine_first(mergeDf['Image'])
# Drop the intermediate columns used for grouping
mergeDf.drop(['Variation_grouped', 'Image_grouped'], axis=1, inplace=True)
# Remove duplicate rows while keeping consolidated lists
megaDf = mergeDf.drop_duplicates(subset=[col for col in mergeDf.columns if col not in ['Variation', 'Image']])

# ================================================== Adding "photo studio" items not in original acnh datasets ==================================================

# Combine flower bags into "seed bag"
oldBags = megaDf['Name'].str.contains('bag') & (megaDf['Source'] == "Nook's Cranny; Leif")
megaDf = megaDf[~oldBags]
seedBag = {
	'Name': 'seed bag',
    'DIY': 'No',
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

# Other items that are only obtainable in editing mode
wallpaperItem = {
	'Name': 'wallpaper',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Etc',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/PhotoStudioWall.png'
}
flooringItem = {
	'Name': 'flooring',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Etc',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/PhotoStudioFloor.png'
}
recipeItem = {
	'Name': 'recipe',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Etc',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/PhotoStudioRecipe.png'
}
rock = {
	'Name': 'rock',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/GardenEditStone.png'
}
hardwoodStump = {
	'Name': 'hardwood-tree stump',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/GardenEditTreeOakStump.png'
}
cedarStump = {
	'Name': 'cedar-tree stump',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/GardenEditTreeCedarStump.png'
}
coconutStump = {
	'Name': 'coconut-tree stump',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/GardenEditTreePalmStump.png'
}
bambooStump = {
	'Name': 'cut bamboo',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/GardenEditTreeBambooStump.png'
}
decorCedar = {
	'Name': 'decorated cedar tree',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False,
	'Image': 'https://acnhcdn.com/latest/FtrIcon/GardenEditTreeCedarDeco.png'
}

decorModeItems = pd.DataFrame([wallpaperItem,flooringItem,recipeItem,rock,hardwoodStump,cedarStump,coconutStump,bambooStump,decorCedar])
megaDf = pd.concat([megaDf,decorModeItems],ignore_index=True)

# ================================================== Fixing other misspelled/missing items ==================================================

megaDf.loc[megaDf['Name'] == "explorer shirt", 'Name'] = "explorer tee"
megaDf.loc[megaDf['Name'] == 'welding mask', 'Name'] = 'welding mask (Red)'
megaDf.loc[megaDf['Name'] == 'matronly bun', 'Name'] = 'matronly bun (Hair Color)'
megaDf.loc[megaDf['Name'] == 'Noh mask', 'Name'] = 'Noh mask (White)'
megaDf.loc[megaDf['Name'] == 'welding mask', 'Name'] = 'welding mask (Red)'
megaDf.loc[megaDf['Name'] == 'gold helmet', 'Name'] = 'gold helmet (Gold)'
megaDf.loc[megaDf['Name'] == "knight's helmet", 'Name'] = "knight's helmet (Gray)"
megaDf.loc[megaDf['Name'] == "composer's wig", 'Name'] = "composer's wig (Hair Color)"
megaDf.loc[megaDf['Name'] == "visual-punk wig", 'Name'] = "visual-punk wig (Hair Color)"
megaDf.loc[megaDf['Name'] == "composer's wig", 'Name'] = "composer's wig (Hair Color)"
furnToVill['log chair'] = furnToVill.pop('log sofa')
furnToVill['fish-and-chips'] = furnToVill.pop('fish and chips')
furnToVill["pesce all'acqua pazza"] = furnToVill.pop("pesce all&apos;acqua pazza")
megaDf.loc[megaDf['Name'] == "skeleton hood", 'Name'] = "skeleton hood (White)"
megaDf.loc[megaDf['Name'] == "King Tut mask", 'Name'] = "King Tut mask (Gold)"
megaDf.loc[megaDf['Name'] == "curly mustache", 'Name'] = "curly mustache (Hair Color)"
megaDf.loc[megaDf['Name'] == "space helmet", 'Name'] = "space helmet (White)"
megaDf.loc[megaDf['Name'] == "mohawk wig", 'Name'] = "mohawk wig (Hair Color)"
megaDf.loc[megaDf['Name'] == "pompadour wig", 'Name'] = "pompadour wig (Hair Color)"
megaDf.loc[megaDf['Name'] == "curly mustache", 'Name'] = "curly mustache (Hair Color)"
megaDf.loc[megaDf['Name'] == "Nook Inc. snorkel", 'Name'] = "Nook Inc. snorkel (Blue)"
megaDf.loc[megaDf['Name'] == "conch", 'Name'] = "spiral shell"
megaDf.loc[megaDf['Name'] == "hot-dog hood", 'Name'] = "hot-dog hood (Red)"
megaDf.loc[megaDf['Name'] == "hockey mask", 'Name'] = "hockey mask (White)"
furnToVill['paper-bag hood (Beige)'] = furnToVill.pop('paper bag (Beige)')
megaDf.loc[megaDf['Name'] == "paper-bag hood", 'Name'] = "paper-bag hood (Beige)"
megaDf.loc[megaDf['Name'] == "stagehand hat", 'Name'] = "stagehand hat (Black)"
megaDf.loc[megaDf['Name'] == "handlebar mustache", 'Name'] = "handlebar mustache (Hair Color)"

# Missing values are bivalve/scallop (in sea creatures table, not included) and Sanrio posters (photos and posters tables not included)
#missing = [i for i in furnToVill if i not in megaDf['Name'].tolist() and "'s poster" not in i and "'s photo" not in i]
#print(missing)

# ================================================== Adding, fixing, and cleaning up columns ==================================================

#megaDf['Catalog'].fillna("Not in catalog")
megaDf['DIY'] = megaDf['DIY'].map({'Yes':True,'No':False}).astype(bool)

# Add list of villagers/facilities to each item
megaDf['HHP Source'] = megaDf['Name'].map(furnToVill)

# todo: Fill in HHP sources aside from villagers/facilities

# ================================================== Exporting finished dataset ==================================================

#print(megaDf[megaDf['Name']=='blue-hyacinth plant'])
megaDf.info()

megaDf.to_csv("output/allitems.csv")
