import matplotlib.pyplot as plt
import PySimpleGUI as sg
import pandas as pd
import os

"""This program was created to create graphs using pandas and pyplot. 
This was created primarily to read csv files for an oscilloscope but
can be used to create graphs from regular CSV files.

Author(Edmund Agyekum https://github.com/Edzemundo)
"""

# Font for graph labels
titleFont = {'family': 'arial',
        'color':  'black',
        'weight': 'normal',
        'size': 20,
        }

axisLabelFont = {'family': 'serif',
        'color':  'black',
        'weight': 'normal',
        'size': 12,
        }

filelocations = []

def openCSV(filename):
    # opens csv file and determines the x-field, y-fields and units
    with open(filename, "r") as file:
        global fields 
        global units
        global yUnits
        global xField
        global yFields
        global data
        
        fields = file.readline().split(",")
        units = [i.strip() for i in file.readline().split(",")]
        yUnits = [i for i in units if units.index(i) > 0]
        xField = fields.pop(0).strip()
        yFields = [i.strip() for i in fields]
        print(fields)
        print(units)
        
        
        #skips the second line when reading with pandas since it usually contains unit information and not data 
        if values["forOsci"] == True:
            data = pd.read_csv(filename, skiprows=[1])
        
        else:
            data = pd.read_csv(filename)

def graph(filename):
    """graph function which creates the actual graphs

    Args:
        filename (text): csv file path
    """
    
    global data
    
    openCSV(filename)
    
    # if this is for a file given by the oscilloscope
    if values["forOsci"] == True:
        plt.figure(figsize=(12,7))
        
        # for every y field, plot a graph of x against that y field
        for yField in yFields:
            data[yField].plot(x = xField, y = yField)      
        
        # Create the title based on the filename and the x-axis label based on the unit
        plt.title(filename.split("/")[-1].split(".")[0], fontdict=titleFont)
        plt.xlabel(units[0], fontdict=axisLabelFont)
        
        # if there is only one y-field, create the y label based on its unit
        if len(yFields) < 2 or len(set(yUnits)) <= 1:
            plt.ylabel(yUnits[0], fontdict=axisLabelFont)
        
        plt.legend(prop={"size": 15})   #create a legend
        plt.grid()  #create a grid
        

    # else if graphing is not for the oscilloscope:
    else:
        data = pd.read_csv(filename)    #read the file
        data.plot() #plot the graph
        plt.title(filename.split(".")[0]) 
        plt.legend()
        plt.grid()
        plt.show()
        

def subplotGraph(filepaths, num):
    plt.figure(figsize=(12,7)).tight_layout()

    for i in range(num):
        openCSV(filepaths[i])
        
        match num:
            case 2:
                rows = 1
                columns = 2
                ind = i + 1
            
            case 3:
                rows = 3
                columns = 1
                ind = i + 1
                
            case 4:
                rows = 2
                columns = 2
                ind = i + 1
        
        plt.subplot(rows, columns, ind)
        
    
        # for every y field, plot a graph of x against that y field
        for yField in yFields:
            data[yField].plot(x = xField, y = yField)      
        
        # Create the title based on the filename and the x-axis label based on the unit
        plt.title(filepaths[i].split("/")[-1].split(".")[0], fontdict=titleFont, loc="left")
        plt.xlabel(units[0], fontdict=axisLabelFont)
        
        # if there is only one y-field, create the y label based on its unit
        if len(yFields) < 2 or len(set(yUnits)) <= 1:
            plt.ylabel(yUnits[0], fontdict=axisLabelFont)
        
        plt.legend(prop={"size": 10})   #create a legend
        plt.grid()  #create a grid
        
    plt.subplots_adjust(wspace=0.2, hspace=0.5)
    


# ---------------------------------------------------------------------
# This is for the GUI using PySimpleGUI - read the PySimpleGui docs for more details on how this was created

# layout for the gui
layout = [[sg.Text("Please select .csv file below:")],
          [sg.Input(key="fileInput"), sg.FileBrowse(key="fileBrowse")],
          [sg.Checkbox("For oscilloscope data", default=True, key="forOsci")],
          [sg.Checkbox("Use multiple CSVs", default=False, key="multicsv", enable_events=True)],
          [sg.Checkbox("Graph every csv in directory", default=False, key="dirGraph", enable_events=True)], 
          [sg.Push(), sg.FolderBrowse("Browse for folder", key="folderBrowse", visible=False), sg.Push()],
          [sg.Text("No. of CSVs:", key="multicsvtext", visible=False), sg.Radio("2", "csvnumber", key="2csv", default=True, visible=False), sg.Radio("3", "csvnumber", key="3csv", default=False, visible=False), sg.Radio("4", "csvnumber", key="4csv", default=False, visible=False)],
          [sg.Push(), sg.Text("", key="statusText")],
          [sg.Push(), sg.Text("", key="filename"), sg.Push()],
          [sg.Push(), sg.Button("Clear", key="clear", visible=False), sg.Button("Add File", key="addfile", visible=False)],
          [sg.Push(), sg.Button("OK", key="okay", bind_return_key=True), sg.Push()]]

# creating the window
window = sg.Window(".CSV Grapher (github.com/Edzemundo)", layout=layout)

# allows window to be open persistently and values to be actively available
while True:
    # event listener and active value reading method
    event, values = window.read()
    
    # if okay button is clicked
    if event == "okay":
        window["statusText"].update("")
        try:
            # graph the csv file selected
            if values["multicsv"] == False and values["dirGraph"] == False:
                if values["fileBrowse"] != "":
                    graph(values["fileBrowse"])
                    plt.show()
            
                else:
                    graph(values["fileInput"])
                    plt.show()
            
            elif values["multicsv"] == True:
                if values["2csv"] == True:
                    subplotGraph(filelocations, 2)
                    plt.show()
                elif values["3csv"] == True:
                    subplotGraph(filelocations, 3)
                    plt.show()
                elif values["4csv"] == True:
                    subplotGraph(filelocations, 4)
                    plt.show()
                    
            elif values["dirGraph"] == True:
                dirCSVFiles = [file for file in os.listdir(values["folderBrowse"]) if file.endswith(".csv")]
                print(dirCSVFiles)
                window["statusText"].update(f"{len(dirCSVFiles)} files found")
                counter = 1              
                for CSVfile in dirCSVFiles:
                    graph(values["folderBrowse"] + f"/{CSVfile}")
                    counter += 1
                plt.show()
                    
                    
    
            
        # error handling for type and file not found errors
        # except FileNotFoundError:
        #     window["statusText"].update("File not found")
        #     window["fileInput"].update("")
            
        except TypeError:
            window["statusText"].update("Syntax error - further support coming")
            window["fileInput"].update("")
            
        except IndexError:
            filelocations = []
            filenames = []
            window["filename"].update("")
            window["statusText"].update("Minimim number of files not added")
            window["fileInput"].update("")
        
    if event == "multicsv":
        if values["multicsv"] == True:
            window["multicsvtext"].update(visible=True)
            window["2csv"].update(visible=True)
            window["3csv"].update(visible=True)
            window["4csv"].update(visible=True)
            window["clear"].update(visible=True)
            window["addfile"].update(visible=True)
        
        else:
            window["multicsvtext"].update(visible=False)
            window["2csv"].update(visible=False)
            window["3csv"].update(visible=False)
            window["4csv"].update(visible=False)
            window["2csv"].update(visible=False)
            window["clear"].update(visible=False)
            window["addfile"].update(visible=False)
            
    if event == "addfile":
        filelocations.append(values["fileBrowse"])
        window["statusText"].update("File Added")
        window["fileInput"].update("")
        
        filenames = [filelocation.split("/")[-1] for filelocation in  filelocations]
        window["filename"].update(f"{filenames}")
        print(filelocations)
        
    if event == "clear":
        filelocations = []
        filenames = []
        window["filename"].update("")
        window["statusText"].update("Cleared")
        window["fileInput"].update("")
        
    if event == "dirGraph":
        if values["dirGraph"] == True:
            window["folderBrowse"].update(visible=True)
            # window["folderInput"].update(visible=True)
        else:
            window["folderBrowse"].update(visible=False)
            # window["folderInput"].update(visible=False)
        
    # if the GUI window is closed, break the code
    if event == sg.WIN_CLOSED:
        break