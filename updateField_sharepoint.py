import arcpy
import csv

from arcgis import GIS
from arcgis import features
import pandas as pd
from arcgis.features import FeatureLayer
from IPython.display import display
from arcgis.features import FeatureLayerCollection
import csv
import pandas as pd
from copy import deepcopy

import os
def folders_with_no_files(base_directory):
    folders_with_no_files_list = []

    for folder_name in os.listdir(base_directory):
        folder_path = os.path.join(base_directory, folder_name)

        # Check if all items in the folder are not files
        if all(not os.path.isfile(os.path.join(folder_path, item)) for item in os.listdir(folder_path)):
            folders_with_no_files_list.append(folder_name)

    return folders_with_no_files_list


def find_empty_folders(directory):
    empty_folders = []
    
    for folder_name in os.listdir(directory):
        folder_path = os.path.join(directory, folder_name)
        
        # Check if it's a directory and if it's empty
        if os.path.isdir(folder_path) and not os.listdir(folder_path):
            empty_folders.append(folder_name)

    return empty_folders

# Replace "path/to/your/directory" with the actual path to your directory of folders
directory_path = r"C:\Projects\hawaii\FolderStructureExample\PHFolder"

empty_folders2 = find_empty_folders(directory_path)
empty_folders = folders_with_no_files(directory_path)
print(empty_folders)
print(empty_folders2)


def extract_numbers(input_list):
    return [''.join(char for char in item if char.isdigit()) for item in input_list]
folder_list = extract_numbers(empty_folders)
float_list = [float(value) for value in folder_list]
print(folder_list)

# Convert the list to a DataFrame for joining with feature layer to get the records that have PH with no folders
folder_df = pd.DataFrame({'PH': folder_list})

# Display the DataFrame
print(folder_df)

# Update username and password for the AGOL account 
gis = GIS("https://histategis.maps.arcgis.com/home","zzz_dot_vsmith-lang", "FinnyLang3")
#hosted feature layer content id

road_item = '7daae1ba637e47f091b17359dac7360a'

roads_flayer = gis.content.get(road_item).layers[0] 
roads_fset = roads_flayer.query()
overlap_rows = pd.merge(left = roads_fset.sdf, right = folder_df.astype(float), how='inner',
                       on = 'PH')
#roads_feat = roads_flayer.query(where="EasementTy = 'Utility'",outfields ='FID,Calculated')
#print(len(roads_feat.features))

print(overlap_rows)
features_for_update = [] 
all_features = roads_fset.features

for ph in overlap_rows['PH']:
    # get the feature to be updated
    original_feature = [f for f in all_features if f.attributes['PH'] == ph][0]
    #feature_to_be_updated = deepcopy(original_feature)
    original_feature.attributes['numfiles'] = 0

    features_for_update.append(original_feature)
print(features_for_update)
roads_flayer.edit_features(updates=features_for_update)

''''
name_edit = update_features
name_edit.attributes['Name'] = 'Updated'
print(roads_flayer.properties.capabilities)
updated_result = roads_flayer.edit_features(updates=[name_edit])

'''