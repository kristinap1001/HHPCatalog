import os, os.path
from re import sub
import pandas as pd
import math
from functools import reduce

def printDict(dic):
	for key,value in dic.items():
		print(key + ": " + ", ".join(value))

# Pandas print options
pd.set_option('display.max_rows', 0)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 0)

# Count number of acnh csvs and rename files
dataDir = 'acnh_data'
dataFiles = len([name for name in os.listdir(dataDir) if os.path.isfile(os.path.join(dataDir, name))])
print(dataFiles)

# Rename csvs (only need to do once)
for filename in os.listdir('acnh_data'):
	if filename.startswith('Data Spreadsheet'):
		newName = filename[52:] # "Data Spreadsheet..." prefix is 52 characters long
	else:
		newName = filename
	newName = newName.lower().replace(" ","")
	os.rename(dataDir+'/'+filename, dataDir+'/'+newName)

# Create dataframes
varList = []
dfList = []
for filename in os.listdir(dataDir):
	varName = os.path.splitext(filename)[0] # removes '.csv'
	data = pd.read_csv(dataDir+'/'+filename,dtype=object)
	globals()[varName] = data

	# Add column with the category/"tab" name
	globals()[varName]["Tab"] = varName

	# Lists of dfs and their names
	varList.append(varName)
	dfList.append(globals()[varName])

# Import HHP furniture lists
villagerUnlocks = pd.read_csv('furniture-per-villager-h.csv',dtype=object)
facilityUnlocks = pd.read_csv('furniture-per-facility-v.csv',dtype=object)

# typo in facilities csv
facilityUnlocks.loc[facilityUnlocks['English Name (added)'] == "tee with silicon bib", 'English Name (added)'] = "tee with silicone bib"

# Dict mapping villagers to their furniture lists
villToFurn = {
	row["Villager"]: [i for i in row.drop(["ID","Label","Villager"]).tolist() if not pd.isna(i)]
	for _, row in villagerUnlocks.iterrows()
}

# the facilities csv is so fucking messy
facilities = ["School", "Cafe", "Restaurant", "Hospital", "Apparel Shop", "Start"]
for facility in facilities:
    villToFurn[facility] = []

for _, row in facilityUnlocks.iterrows():
	if str(row["Variation Name (added)"]) not in ["nan","No Variations"]:
		itemName = f'{row["English Name (added)"]} ({row["Variation Name (added)"]})'
	else:
		itemName = row["English Name (added)"]
	for facility in facilities:
		if row[facility] == '1':
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

# Create dataframe with all items
megaDf = pd.concat(dfList,ignore_index=True)
megaDf.to_csv("output/mega.csv")

# Customize/Cyrus customize booleans
megaDf['Customize'] = megaDf['Kit Cost'].notnull()
megaDf['Cyrus'] = megaDf['Cyrus Customize Price'].notnull()

# Remove unnecessary columns (most of them)
megaDf = megaDf.filter(['Filename','Name','Variation','Pattern','DIY','Buy','Sell','Source','Source Notes','Catalog','Tab','Tag','Customize','Cyrus'])

# Create image link from filename
megaDf['Image'] = "https://acnhcdn.com/latest/FtrIcon/" + megaDf['Filename'] + ".png"
megaDf.drop('Filename',axis=1,inplace=True)

# Make naming convention of clothing match the hhp dataset
megaDf.loc[megaDf['Name'] == "explorer shirt", 'Name'] = "explorer tee"
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
        "Variation": list,
        "Image": list
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
	'Cyrus': False
}
flooringItem = {
	'Name': 'flooring',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Etc',
	'Customize': False,
	'Cyrus': False
}
recipeItem = {
	'Name': 'recipe',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Etc',
	'Customize': False,
	'Cyrus': False
}
rock = {
	'Name': 'rock',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False
}
hardwoodStump = {
	'Name': 'hardwood-tree stump',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False
}
cedarStump = {
	'Name': 'cedar-tree stump',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False
}
coconutStump = {
	'Name': 'coconut-tree stump',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False
}
bambooStump = {
	'Name': 'cut bamboo',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False
}
decorCedar = {
	'Name': 'decorated cedar tree',
	'DIY': 'No',
	'Buy': 'NFS',
	'Source': 'Decorating mode',
	'Tab': 'other',
	'Tag': 'Plants',
	'Customize': False,
	'Cyrus': False
}

decorModeItems = pd.DataFrame([wallpaperItem,flooringItem,recipeItem,rock,hardwoodStump,cedarStump,coconutStump,bambooStump,decorCedar])
megaDf = pd.concat([megaDf,decorModeItems],ignore_index=True)

# Check if any furniture items exist in dict but not in df
#missing = [i for i in furnToVill if i not in megaDf['Name'].tolist() and "'s poster" not in i and "'s photo" not in i]
#print(missing)

# Fix missing entries
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
missing = [i for i in furnToVill if i not in megaDf['Name'].tolist() and "'s poster" not in i and "'s photo" not in i]
print(missing)

# Add list of villagers/facilities to each item
megaDf['HHP Source'] = megaDf['Name'].map(furnToVill)
print(megaDf)

megaDf.to_csv("output/mega_nobs.csv")


'''
 #   Column                     Non-Null Count  Dtype
---  ------                     --------------  -----
 0   Name                       20097 non-null  object
 1   Closet Image               5380 non-null   object x
 2   Storage Image              5756 non-null   object x
 3   Variation                  17153 non-null  object
 4   DIY                        19917 non-null  object
 5   Buy                        20097 non-null  object
 6   Sell                       19962 non-null  object
 7   HHA Base Points            19998 non-null  object x
 8   Color 1                    19626 non-null  object x
 9   Color 2                    19622 non-null  object x
 10  Size                       19073 non-null  object x
 11  Exchange Price             12714 non-null  object x
 12  Exchange Currency          12714 non-null  object x
 13  Source                     20097 non-null  object
 14  Source Notes               7968 non-null   object
 15  Season/Event               2365 non-null   object x
 16  Season/Event Exclusive     2361 non-null   object x
 17  Seasonal Availability      5432 non-null   object x
 18  Seasonality                5432 non-null   object x
 19  Mannequin Season           454 non-null    object x
 20  Gender                     5500 non-null   object x
 21  Villager Gender            3607 non-null   object x
 22  Style 1                    5432 non-null   object x
 23  Style 2                    5431 non-null   object x
 24  Sort Order                 5432 non-null   object x
 25  Label Themes               5432 non-null   object x
 26  Type                       1169 non-null   object x
 27  Villager Equippable        5814 non-null   object x
 28  Catalog                    19687 non-null  object
 29  Version Added              20097 non-null  object x
 30  Unlocked?                  20097 non-null  object x
 31  Filename                   19687 non-null  object x
 32  ClothGroup ID              5432 non-null   object x
 33  Internal ID                20097 non-null  object x
 34  Unique Entry ID            20097 non-null  object
 35  Tab                        20097 non-null  object
 36  Image                      14077 non-null  object x
 37  High-Res Texture           46 non-null     object x
 38  Genuine                    70 non-null     object x
 39  Category                   70 non-null     object x
 40  Real Artwork Title         70 non-null     object x
 41  Artist                     70 non-null     object x
 42  Description                70 non-null     object x
 43  HHA Concept 1              13471 non-null  object x
 44  HHA Concept 2              10162 non-null  object x
 45  HHA Series                 3831 non-null   object x
 46  HHA Set                    569 non-null    object x
 47  Interact                   12940 non-null  object x
 48  Tag                        14074 non-null  object
 49  Speaker Type               11790 non-null  object x
 50  Lighting Type              13254 non-null  object x
 51  Body Title                 12113 non-null  object x
 52  Pattern                    7063 non-null   object x
 53  Pattern Title              7479 non-null   object x
 54  Body Customize             12870 non-null  object x
 55  Pattern Customize          12870 non-null  object x
 56  Pattern Customize Options  7479 non-null   object x
 57  Kit Cost                   9279 non-null   object x
 58  Kit Type                   9279 non-null   object x
 59  Cyrus Customize Price      12382 non-null  object x
 60  HHA Category               2638 non-null   object x
 61  Outdoor                    12870 non-null  object x
 62  Variant ID                 12382 non-null  object x
 63  Primary Shape              1069 non-null   object x
 64  Secondary Shape            1069 non-null   object x
 65  Customize                  413 non-null    object
 66  Stack Size                 4006 non-null   object x
 67  VFX                        515 non-null    object x
 68  Surface                    11720 non-null  object x
 69  Food Power                 271 non-null    object x
 70  Framed Image               107 non-null    object x
 71  Album Image                107 non-null    object x
 72  Inventory Image            404 non-null    object x
 73  Inventory Filename         410 non-null    object X
 74  Storage Filename           410 non-null    object X
 75  Size Category              209 non-null    object X
 76  Uses                       314 non-null    object X
 77  Set                        80 non-null     object X
 78  Door Deco                  731 non-null    object X
 79  VFX Type                   38 non-null     object X
 80  Window Type                151 non-null    object X
 81  Window Color               151 non-null    object X
 82  Pane Type                  151 non-null    object X
 83  Curtain Type               99 non-null     object X
 84  Curtain Color              99 non-null     object X
 85  Ceiling Type               306 non-null    object X
 '''