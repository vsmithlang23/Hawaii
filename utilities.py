import os
import os.path
import arcpy
from arcgis import GIS
import csv


######Build the sharepoint folder variables#############
### These are the folder links #######
name = ""
ph1 = f'<a href="https://hawaiioimt-my.sharepoint.com/personal/christopher_guerin_hawaii_gov/_layouts/15/onedrive.aspx?ga=1&id=%2Fpersonal%2Fchristopher%5Fguerin%5Fhawaii%5Fgov%2FDocuments%2FHWYDC%20Office%20PH%2Fph%20'
ph2 =f'%2FCURRENT&noAuthRedirect=1" target="_top">PH {" "}'
ph3 = f'</a>'


calc1 = f'<a href="https://hawaiioimt-my.sharepoint.com/personal/christopher_guerin_hawaii_gov/_layouts/15/onedrive.aspx?ga=1&id=%2Fpersonal%2Fchristopher%5Fguerin%5Fhawaii%5Fgov%2FDocuments%2FCalculation%20Folder%2F'
calc2 = f'" target="_top">Calculation FLR {" "}'
calc3 =f'</a>'


f1 = f'<a href="https://hawaiioimt-my.sharepoint.com/personal/christopher_guerin_hawaii_gov/_layouts/15/onedrive.aspx?ga=1&id=%2Fpersonal%2Fchristopher%5Fguerin%5Fhawaii%5Fgov%2FDocuments%2FField%20Book%2F'
f2 = f'" target="_top">Field Book {" "}' 
f3 =f'</a>'

d1 = f'<a href="https://hawaiioimt-my.sharepoint.com/personal/christopher_guerin_hawaii_gov/_layouts/15/onedrive.aspx?ga=1&id=%2Fpersonal%2Fchristopher%5Fguerin%5Fhawaii%5Fgov%2FDocuments%2FDescription%20Folder%2F'
d2 = f'" target="_top">Description FLR{" "}'
d3 = f'</a>'
d4 = f'" target="_top">{" "}'

c1 = f'<a href="https://hawaiioimt-my.sharepoint.com/personal/christopher_guerin_hawaii_gov/_layouts/15/onedrive.aspx?ga=1&id=%2Fpersonal%2Fchristopher%5Fguerin%5Fhawaii%5Fgov%2FDocuments%2FCertificate%20Folder%2F'
c2 = f'" target="_top">Certificate FLR {" "}'
c3 = f'</a>'

data1 =f'<a href= "https://hawaiioimt-my.sharepoint.com/personal/christopher_guerin_hawaii_gov/_layouts/15/onedrive.aspx?ga=1&id=%2Fpersonal%2Fchristopher%5Fguerin%5Fhawaii%5Fgov%2FDocuments%2FData%20Folder%2F'
data2 =f' " target="_top">Data FLR {" "}'
data3 = f'</a>'

def getfoldernumber(folder_list):
    folder_num = []
    output_list = []
    for value in folder_list:
        part = value.split("-")
        parts = [x.strip(' ') for x in part]
        if len(parts) >= 2:
            folder_num.append(parts[0])  # This selects the part before the  "-"
            arcpy.AddMessage("Foldernanmes are" + parts[0])
        else:
            folder_num.append(parts)  # If there is no "-", keep the original string
            arcpy.AddMessage("Foldernanmes are without dashes" + parts[0])
    for item in folder_num:
        if isinstance(item, list):
            # Check if it's a list
            if len(item) > 0:
                output_list.append(item[0])
        elif isinstance(item, str):
            # Check if it's a string
            output_list.append(item)
    return output_list

def get_file_names(folder_path,target):
    #Returns a list of all file names in a given folder path
    file_names = ""
    file_names = []
    pdf_path = os.path.join(folder_path,"Description Folder",target)
    arcpy.AddMessage(folder_path+" Description Folder "+target)
    for filename in os.listdir(pdf_path):
        #arcpy.AddMessage("Filename is "+ filename)
        if filename.endswith ('.pdf'):
            file_names.append(os.path.splitext(filename)[0])
    return file_names

def csv_dict_create(csvfile,csv_field,new_dict):
    # Read the CSV file and populate the dictionary
    with open(csvfile, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            project_id = row['Project ID']
            name = row[csv_field]
            new_dict[project_id] = name

def UpdateFolder(table,csv_dict,joinfield,updatefield,share1,share2,share3):
    with arcpy.da.UpdateCursor(table,[joinfield,updatefield,])as sc:
        for row in sc:
            if row[0] in list(csv_dict.keys()):
                row[1] = csv_dict[row[0]]
                folder = csv_dict[row[0]]
                if folder != "":
                    if ';' in row[1]:
                        name_list = row[1].split(";")
                        folder_list = getfoldernumber(name_list)
                        arcpy.AddMessage(folder_list)
                        unique_list = [item for index, item in enumerate(folder_list) if item not in folder_list[:index]]
                        arcpy.AddMessage("uniques folders are :" + str(unique_list))
                        result_variable = ""
                        for name in unique_list:
                            name_calc = share1+str(name)+share2+str(name)+share3 + ' :'
                            result_variable += name_calc
                            row[1]= result_variable.rstrip(result_variable[-1])
                        sc.updateRow(row)
                    else:                                        
                        name = folder.split("-")[0]
                        row[1] = share1+str(name)+share2+str(name)+share3
                        sc.updateRow(row)
                else:
                    arcpy.AddMessage("empty dictionary")

def UpdateNotes(table,csv_dict,joinfield,notesfield):
    with arcpy.da.UpdateCursor(table,[joinfield,updatefield,notesfield])as sc:
        for row in sc:
            notes_list = ""
            if row[0] in list(csv_dict.keys()):
                row[1] = csv_dict[row[0]]
                folder = csv_dict[row[0]]
                foldername_list = ""
                if folder != "":
                    notes_list = updatefield + ": "+ folder
            arcpy.AddMessage (notes_list)


def replace_underscore(input_string):
    modified_string = input_string.replace("_", "%5F").upper()
    return modified_string


def pdf_link(filename,foldern):
    file_name2 = replace_underscore(filename)
    file_type = ".pdf"
    file1 = 'https://hawaiioimt-my.sharepoint.com/personal/christopher_guerin_hawaii_gov/_layouts/15/onedrive.aspx?ga=1&id=%2Fpersonal%2Fchristopher%5Fguerin%5Fhawaii%5Fgov%2FDocuments%2FDescription%20Folder%2F'
    file2 = "%2Epdf&parent=%2Fpersonal%2Fchristopher%5Fguerin%5Fhawaii%5Fgov%2FDocuments%2FDescription%20Folder%2F"
    file3 = '</a>'
    linked_pdf = file1+str(foldern)+"%2F"+file_name2+file2+str(foldern)
    return linked_pdf