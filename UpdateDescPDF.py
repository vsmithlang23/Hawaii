import os
import os.path
import arcpy
from arcgis import GIS
import csv
from importlib import reload

import arcpy
import utilities

reload(arcpy)
reload(utilities)


folder_path = arcpy.GetParameterAsText(0)
arcpy.env.workspace = arcpy.GetParameterAsText(1)
workspace = arcpy.GetParameterAsText(1)
csv_file_path = arcpy.GetParameterAsText(2)

DescFLD = "Description Folder"
dataset = "DOT"
arcpy.AddMessage (workspace)
Parcel = os.path.join(workspace, dataset, "Parcel")
Records = os.path.join(workspace, dataset, "ParcelFabric_Records")
filetype = ".pdf"

### Populate the feature classes with the links to the pdf files (Parcel, Easement,OUA,etc)
#####The folder name comes from the PH field of the csv file, the pdf files are in the DescriptionFolder/folder name of the folder_path for each ProjectID

# Initialize an empty dictionary to store the data
csv_dict = {}
csv_desc = {}
# Read the CSV file and populate the dictionary with the PH/ProjectID values from the csv file
with open(csv_file_path, 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        project_id = row['Project ID']
        name = row['PH']
        csv_dict[project_id] = name

with open(csv_file_path, 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        project_id = row['Project ID']
        name = row['Description FLR']
        csv_desc[project_id] = name

#create dictionary of GlobalID,ProjectID from Records table
projects = {r[0]:r[1] for r in arcpy.da.SearchCursor(Records,['GlobalID','ProjectID'])}
#
arcpy.AddMessage(projects)

with arcpy.da.SearchCursor(Records,'ProjectID')as sc:
    for row in sc:
        target_name = ""
        target_desc = ""
        target_project_id = row[0]
        fc_filenames = []
        arcpy.AddMessage (target_project_id)
        if target_project_id in csv_dict:
            target_name = csv_dict[target_project_id]
            target_desc = csv_desc[target_project_id]
            arcpy.AddMessage(f"The folder for ProjectID '{target_project_id}' is '{target_name}' and Desc is '{target_desc}'")
            fc_filenames = utilities.get_file_names(folder_path,target_desc)
            arcpy.AddMessage(fc_filenames)
        else:
            arcpy.AddMessage(f"ProjectID '{target_project_id}' not found in the dictionary.")
            break
       
        
        #create dictionary of GlobalID,ProjectID from Records table
        projects = {r[0]:r[1] for r in arcpy.da.SearchCursor(Records,['GlobalID','ProjectID'])}
        #print (projects)

        fcs = ["Easement","Parcel","AirRights","Lease","OUA"]
        #fcs = ["Parcel2"]
        for fc in fcs:
            #create list of tuples from table (name,CreatedByRecord)
            fc_name = os.path.join(workspace, dataset, fc)
            if arcpy.Exists(fc_name):
                arcpy.AddMessage(fc_name)
                tuple_list = []
                with arcpy.da.SearchCursor(fc_name,['Name','CreatedByRecord']) as sc:
                    for row in sc:
                        tuple_list.append((row[0],row[1]))
                    #arcpy.AddMessage(tuple_list)

                #create a list of tuples with unique combimation of projectid,name,global_id

                    fc_combos = []
                    for p in tuple_list:
                        project_name,global_id = p
                        project_id = projects[global_id]
                        fc_combos.append((project_id,project_name,global_id))
                        #arcpy.AddMessage (fc_combos)

                        edit = arcpy.da.Editor(workspace)
                        edit.startEditing()
                        with arcpy.da.UpdateCursor(fc_name,['Name','CreatedByRecord','DescriptionPDFLink']) as cursor:
                            for row in cursor:
                                project_name = row[0]
                                global_id = row[1]
                                for c in fc_combos:
                                    project_id,project_name1,global_id1 = c
                                    if project_name == project_name1 and global_id == global_id1:
                                        file_name = f"{fc}_{project_name}"
                                        #arcpy.AddMessage(file_name)
                                        #rcpy.AddMessage(fc_filenames)
                                        if file_name in fc_filenames:
                                            #arcpy.AddMessage("match")
                                            row[2] = utilities.d1 +target_desc+utilities.d4 + file_name + filetype
                                            cursor.updateRow(row)
                                            #arcpy.AddMessage (f'updated {file_name}')
                        # Stop the edit operation.
                        edit.stopOperation()
                        # Stop the edit session and save the changes
                        edit.stopEditing(True)

#arcpy.AddMessage("Error occured updating the Parcels table")

"""

#### create links to the folders in the Records table (folder values come from reading csv file)

# Initialize an empty dictionary to store the data
CalculationFolder_dict = {}
DataFolder_dict = {}
DescriptionFolder_dict = {}
FieldBookFolder_dict= {}
PHFolder_dict = {}
CertificateFolder_dict = {}



utilities.csv_dict_create(csv_file_path,'Description FLR',DescriptionFolder_dict)
utilities.csv_dict_create(csv_file_path,'PH',PHFolder_dict)
utilities.csv_dict_create(csv_file_path,'Calculation FLR',CalculationFolder_dict)
utilities.csv_dict_create(csv_file_path,'Data FLR',DataFolder_dict)
utilities.csv_dict_create(csv_file_path,'Field Book',FieldBookFolder_dict)
utilities.csv_dict_create(csv_file_path,'Certificate FLR',CertificateFolder_dict)



utilities.UpdateFolder(Records,DataFolder_dict,'ProjectID',"DataFolderLink",utilities.data1,utilities.data2,utilities.data3)
utilities.UpdateFolder(Records,PHFolder_dict,'ProjectID',"PHFolderLink",utilities.ph1,utilities.ph2,utilities.ph3)
utilities.UpdateFolder(Records,FieldBookFolder_dict,'ProjectID',"FieldBookFolderLink",utilities.f1,utilities.f2,utilities.f3)
utilities.UpdateFolder(Records,CalculationFolder_dict,'ProjectID',"CalculationFolderLink",utilities.calc1,utilities.calc2,utilities.calc3)
utilities.UpdateFolder(Records,DescriptionFolder_dict,'ProjectID',"DescriptionFolderLink",utilities.d1,utilities.d2,utilities.d3)
utilities.UpdateFolder(Records,CertificateFolder_dict,'ProjectID',"CertificateFolderLink",utilities.c1,utilities.c2,utilities.c3)


##### Add the full folder values for each ProjectID in the csv table to the Notes field of the Records table.
## Read the csv file and create a dictionary of the column name/value pairs to update the Notes field in the Records table.
projectID_notes= {}
# Read the CSV file
with open(csv_file_path, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row_number, row in enumerate(reader, start=1):
        # create an empty list to store column name-value pairs
        column_name_value_pairs = []
        
        # loop through the specified columns
        for column_name in ["Calculation FLR", "Description FLR", "Data FLR", "Field Book", "Certificate FLR"]:
            column_value = row[column_name]
            
            # drop the column value pair if the value is blank, only need values that are populated
            if column_value:
                # Concatenate the column name and value and add to the list
                column_name_value_pairs.append(f"{column_name}: {column_value}")
        
        # Create a concatenated string for the name, values...
        concatenated_string = ', '.join(column_name_value_pairs)
        project_id = row['Project ID']
        name = concatenated_string
        projectID_notes[project_id] = name       
arcpy.AddMessage(projectID_notes)


with arcpy.da.UpdateCursor(Records,['ProjectID','Notes']) as cursor:
    for row in cursor:
        if row[0] in list(projectID_notes.keys()):
                row[1] =projectID_notes[row[0]]
                arcpy.AddMessage (row[1])
                cursor.updateRow(row)
        else:
            row[1] = "<Null>"
            cursor.updateRow(row)
    
"""