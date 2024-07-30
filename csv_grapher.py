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

filelocations = []  #list of multiple csv files
annots = [] #list of annotations
graphs = [] #list of graphs plotted


class Graph:
    def __init__(self, figureNum):
        """Graph instance. Contains the figure, axes and all other components of a graph (other than subplot - refer to class SubplotGraph)

        Args:
            figureNum (int): Describes the figure identity, used to prevent plotted CSV from overwritting current figure.
        """
        
        # Listed components of the graph
        self.fig = plt.figure(figureNum, figsize=(12,7))    #plot figure
        
        self.line = None    #axis instance
        self.lines = []     #list of axes
        
        self.annotation = None  #annotation property for creating annotations on click
        self.annot = None   #annotation property for updating live annotations on hover
        self.annots = []    #list of annotations
        
        self.legend = None  #graph legend
        self.grid = plt.grid()  #graph grid
        self.figureNum = figureNum  #figure ID
        counter = 0
        
        for yField in yFields:
            
            self.line, = plt.plot(data[xField], data[yField], pickradius = 2, marker='o', markersize=2)   #plot the data attained from openCSV function
            self.line.set_label(f"{yFields[counter]}")  #set label according to yField index
            self.lines.append(self.line)    #add axis to axes list
            self.annot = plt.annotate(  #describe annot property for live annotations
                        "", 
                        xy=(0,0), 
                        xytext=(-20,20),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
            self.annot.set_visible(False)
            self.annots.append(self.annot)
            self.legend = plt.legend(prop={"size": 10}, loc="upper right")
            counter += 1
            
        self.title = plt.title(title, fontdict=titleFont)   #title of graph
        
        # Determines whether or not 2nd row is plotted as data based on if units are present
        if hasUnitsVar:
            self.xlabel = plt.xlabel(units[0], fontdict=axisLabelFont)
        else:
            self.xlabel = None
        
        if hasUnitsVar and (len(yFields) < 2 or len(set(yUnits)) <= 1):
            self.ylabel = plt.ylabel(yUnits[0], fontdict=axisLabelFont)
        else:
            self.ylabel = None
        
        # Connecting the figures to the event listener callback function
        self.fig.canvas.mpl_connect("motion_notify_event", hover)   #hovering
        self.fig.canvas.mpl_connect('button_press_event', mouse_event)  #clicking
        
    def setAnnotVisibility(self, boolValue):
        """sets the visibility of the live annotation

        Args:
            boolValue (bool): Sets the live annotation visibility
        """
        self.annot.set_visible(boolValue)


class SubplotGraph:
    def __init__(self, filepaths, figureNum, num):
        """Subplot instance. Contains the figure, axes and all other components of the subplot.
        
        Args:
            filepaths (list): list of CSVs paths to be included in the subplot
            figureNum (int): Describes the figure identity, used to prevent plotted subplot from overwritting current figure.
            num (int): number of plots in the sublot (min=2, max=4)
        """

        # These are generally the same as the properties of the Graph class
        self.fig = plt.figure(figureNum, figsize=(12,7))
        
        self.line = None
        self.lines = []
        
        self.ax = None
        self.axes = []  #list of all axes in the subplot in order to live annotate different axes

        self.annotation = None
        self.annot = None
        self.annots = []
        self.figureNum = figureNum
        
        # For every plot in the subplot
        for i in range(num):
            openCSV(filepaths[i])   #read the CSV. This is added here to maintain the simplicity of openCSV function
            counter = 1
            # This is used to determine the layout of the subplots based on how many plots
            match num:
                case 2:
                    self.rows = 1   #number of rows
                    self.columns = 2    #number of columns
                    self.ind = i + 1    #ind is a plt conventional variable used to determine which plot is in 'focus'
                
                case 3:
                    self.rows = 3
                    self.columns = 1
                    self.ind = i + 1
                    
                case 4:
                    self.rows = 2
                    self.columns = 2
                    self.ind = i + 1

            plt.subplot(self.rows, self.columns, self.ind)  #peform the subplot
            
            #generally same as Graph class
            for yField in yFields:
                self.line, = plt.plot(data[xField], data[yField], pickradius = 2)
                self.line.set_label(f"{yFields[counter]}")
                self.lines.append(self.line)
                self.annot = plt.annotate(
                            "", 
                            xy=(0,0), 
                            xytext=(-20,20),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
                self.annot.set_visible(False)
                self.annots.append(self.annot)
                counter += 1
            
            #These are added in order to enable live annotations on every subplot
            self.ax = plt.gca() #get the current axis
            self.axes.append(self.ax)   #adds them to a list of axis
            
            self.ax.set_title(title, loc="left")    #set title
            
            #determines whether or not to plot 2nd row based on presence of units like Graph class
            if hasUnitsVar:
                self.xlabel = plt.xlabel(units[0], fontdict=axisLabelFont)
            else:
                self.xlabel = None
            
            if hasUnitsVar and (len(yFields) < 2 or len(set(yUnits)) <= 1):
                self.ylabel = plt.ylabel(yUnits[0], fontdict=axisLabelFont)
            else:
                self.ylabel = None
                
            self.ax.label_outer()   #shows other labels for easier arrangement
            
            plt.legend(prop={"size": 10}, loc="upper right")   #create a legend
            plt.grid()  #create a grid
        
        #connect figures to event listener callback functions
        self.fig.canvas.mpl_connect("motion_notify_event", hover)
        self.fig.canvas.mpl_connect('button_press_event', mouse_event)
        
    def setAnnotVisibility(self, boolValue):
        self.annot.set_visible(boolValue)
                                     
        
def openCSV(filename):
    """Opens CSV files to attain certain information about the graph being plotted and assigns them to global variables

    Args:
        filename (str): file path of CSV to be read
    """    
   
    with open(filename, "r") as file:
        global hasUnitsVar  #tells whether or not there are units in the 2nd row
        global yFields  #list of yFields
        global xField   #name of xField
        global yUnits   #list of yUnits
        global title    #title of the graph which is the filename
        global units    #list of all units
        global data     #pandas dataframe object of the CSV file - allows simpler importing of data into pyplot
        
        # Determines whether 2nd row has units
        if values["forOsci"]:
            hasUnitsVar = True
        else:
            hasUnitsVar = False
            
        fields = file.readline().split(",")     #all fields in a file
        units = [i.strip() for i in file.readline().split(",")]     #all units in a file
        yUnits = [i for i in units if units.index(i) > 0]       #all y units
    
        
        xField = fields.pop(0).strip()
        yFields = [i.strip() for i in fields]
        title = filename.split("/")[-1].split(".")[0]
        
        print(yFields)
        print(units)
    
    #skips the second line when reading with pandas since it usually contains unit information and not data 
    if hasUnitsVar:
        try:
            data = pd.read_csv(filename, skiprows=[1])
        except pd.errors.EmptyDataError:
            window["statusText"].update("Empty file")
    else:
        try:
            data = pd.read_csv(filename)
        except pd.errors.EmptyDataError:
            window["statusText"].update("Empty file")
    

def update_annot(event, annot):
    """update annotations when hover event is activated within the axis

    Args:
        event: hover event
        annot: annotation to be updated
    """
    x,y = event.xdata, event.ydata      #get the x,y data from the event
    annot.xy = (x, y)   #set the annotation x and y coordinates
    annot.set_text(f"{x:.10f},{y:.10f}")    #set text of annotation to the values of the location being hovered
    annot.get_bbox_patch().set_alpha(0.2)
    graph.setAnnotVisibility(True)

   
    
def create_annot(x,y):
    """Create annotation box when click event occurs

    Args:
        x (float): x-xoordinate
        y (float): y-coordinate
    """
    graph.annotation = plt.annotate("", xy=(x,y), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
    graph.annotation.set_text(f"{x:.7f},{y:.7f}")
    graph.annotation.get_bbox_patch().set_alpha(0.4)
    graph.annotation.set_visible(True)


def hover(event):
    """Hover callback function

    Args:
        event: hover event
    """
    for line in graph.lines:
        if event.inaxes:    #if the event is within the graph
            cont, ind = line.contains(event)
            annot = graph.annots[graph.lines.index(line)]
            if cont:    #if the event is within the plotted line
                update_annot(event, annot)
                annot.set_visible(True)
                graph.fig.canvas.draw_idle() #redraw the canvas i.e. update the canvas
            else: 
                if annot.get_visible():
                    annot.set_visible(False)
                    graph.fig.canvas.draw_idle()

                
def mouse_event(event):
    """mouse click callback function

    Args:
        event: click event
    """
    for line in graph.lines:
        if event.inaxes:
            cont, ind = line.contains(event)
            if cont:
                create_annot(event.xdata, event.ydata)
    



# ---------------------------------------------------------------------
# This is for the GUI using PySimpleGUI - read the PySimpleGui docs for more details on how this was created

# layout for the gui
layout = [[sg.Text("Please select .csv file below:")],
          [sg.Input(key="fileInput", enable_events=True), sg.FileBrowse(key="fileBrowse", file_types=(("CSV Files", "*.csv"),))],
          [sg.Checkbox("Contains units in 2nd row", default=True, key="forOsci")],
          [sg.Radio("Use one CSV", "morethanone" ,default=True, key="oneCSV", enable_events=True)],
          [sg.Radio("Use multiple CSVs", "morethanone" ,default=False, key="multiCSV", enable_events=True)],
          [sg.Radio("Graph every csv in directory", "morethanone", default=False, key="dirGraph", enable_events=True)], 
          [sg.Push(), sg.FolderBrowse("Browse for folder", key="folderBrowse", visible=False), sg.Push()],
          [sg.Radio("Same Graph", "multiplot", key="sameplotMultiplot", default=True, visible=False, enable_events=True), sg.Radio("Separate Graphs", "multiplot", key="diffplotMultiplot", visible=False, enable_events=True), sg.Radio("Subplot", "multiplot", key="subplotMultiplot", visible=False, enable_events=True)],
          [sg.Text("No. of Subplots:", key="csvnumbertext", visible=False), sg.Radio("2", "csvnumber", key="2csv", default=True, visible=False), sg.Radio("3", "csvnumber", key="3csv", default=False, visible=False), sg.Radio("4", "csvnumber", key="4csv", default=False, visible=False)],
          [sg.Text("No. of CSVs:", key="multiCSVtext", visible=False)], 
          [sg.Push(), sg.Text("", key="statusText")],
          [sg.Push(), sg.Text("", key="filename"), sg.Push()],
          [sg.Push(), sg.Button("Clear", key="clear", visible=True), sg.Button("Add File", key="addfile", visible=False)],
          [sg.Push(), sg.Button("OK", key="okay", bind_return_key=True), sg.Push()]]

# creating the window
window = sg.Window(".CSV Grapher (github.com/Edzemundo)", layout=layout)
oneCSVCounter = 1
# allows window to be open persistently and values to be actively available
while True:
    # event listener and active value reading method
    event, values = window.read()
    
    # if okay button is clicked
    if event == "okay":
        window["statusText"].update("")
        try:
            # graph the csv file selected
            if values["oneCSV"] == True:
                if values["fileInput"] != "":
                    openCSV(values["fileInput"])
                    graph = Graph(oneCSVCounter)
                    plt.show()
                else:
                    openCSV(values["fileBrowse"])
                    graph = Graph(oneCSVCounter)
                    plt.show()
                oneCSVCounter +=1
            
            elif values["multiCSV"] == True:
                if values["subplotMultiplot"] == True:
                    if values["2csv"] == True:
                        graph = SubplotGraph(filelocations, 1, 2)
                        plt.show()
                    elif values["3csv"] == True:
                        graph = SubplotGraph(filelocations, 1, 3)
                        plt.show()
                    elif values["4csv"] == True:
                        graph = SubplotGraph(filelocations, 1, 4)
                        plt.show()
                    
                elif values["sameplotMultiplot"] == True:
                    for file in filelocations:
                        openCSV(file)
                        graph = Graph(1)
                    plt.show()
            
                elif values["diffplotMultiplot"] == True:
                    counter = 1
                    for file in filelocations:
                        openCSV(file)
                        graph = Graph(counter)
                        counter += 1                    
                    plt.show()
                
                    
            elif values["dirGraph"] == True:
                
                dirCSVFiles = [file for file in os.listdir(values["folderBrowse"]) if file.endswith(".csv")]
                print(dirCSVFiles)
                filelocations = [values["folderBrowse"] + f"/{i}" for i in dirCSVFiles]
                window["statusText"].update(f"{len(dirCSVFiles)} files found")             
                if values["sameplotMultiplot"] == True:
                    for CSVfile in dirCSVFiles:
                        openCSV(values["folderBrowse"] + f"/{CSVfile}")
                        graph = Graph(1)
                    plt.show()
                    
                elif values["diffplotMultiplot"] == True:
                    i = 1
                    for CSVfile in dirCSVFiles:
                        openCSV(values["folderBrowse"] + f"/{CSVfile}")
                        graph = Graph(i)
                        i += 1                    
                    plt.show()
                    
                    
                elif values["subplotMultiplot"] == True:
                    if values["2csv"] == True:
                        n = 2
                    if values["3csv"] == True:
                        n = 3
                    if values["4csv"] == True:
                        n = 4
                    counter = 1
                    sublists = [filelocations[i:i + n] for i in range(0, len(filelocations), n)]  
                    for sublist in sublists:
                        if len(sublist) == n:
                            if values["2csv"] == True:
                                graph = SubplotGraph(sublist, counter, 2)
                            elif values["3csv"] == True:
                                graph = SubplotGraph(sublist, counter, 3)
                            elif values["4csv"] == True:
                                graph = SubplotGraph(sublist, counter, 4)
                                print("confirmed")
                            counter += 1
                            print(counter)
                        
                        elif len(sublist) == 1:
                            openCSV(sublist[0])
                            if counter != 0:
                                graph = Graph(counter + 1)
                            else:
                                graph = Graph(1)
                                
                        else:
                            graph = SubplotGraph(sublist, counter, n-1)
                    plt.show()

                    
                    
        # error handling for type and file not found errors
        except FileNotFoundError:
            window["statusText"].update("File not found or input file/folder not selected.")
            window["fileInput"].update("")
            
        except TypeError:
            window["statusText"].update("Syntax error - further support coming")
            window["fileInput"].update("")
            
        except IndexError:
            filelocations = []
            filenames = []
            window["filename"].update("")
            window["statusText"].update("Minimim number of files not added")
            window["fileInput"].update("")
        
    if event in ("oneCSV", "multiCSV", "dirGraph", "subplotMultiplot", "sameplotMultiplot", "diffplotMultiplot"):
        if values["multiCSV"] == True or values["dirGraph"] == True:
            window["multiCSVtext"].update(visible=True)
            window["addfile"].update(visible=True)
            window["sameplotMultiplot"].update(visible=True)
            window["subplotMultiplot"].update(visible=True)
            window["diffplotMultiplot"].update(visible=True)
            
            if event == "subplotMultiplot":
                window["csvnumbertext"].update(visible=True)
                window["2csv"].update(visible=True)
                window["3csv"].update(visible=True)
                window["4csv"].update(visible=True)
            
            if event == "sameplotMultiplot":
                window["csvnumbertext"].update(visible=False)
                window["2csv"].update(visible=False)
                window["3csv"].update(visible=False)
                window["4csv"].update(visible=False)
            
            if event == "diffplotMultiplot":
                window["csvnumbertext"].update(visible=False)
                window["2csv"].update(visible=False)
                window["3csv"].update(visible=False)
                window["4csv"].update(visible=False)
                
            
        if values["multiCSV"] == False and values["dirGraph"] == False:
            window["multiCSVtext"].update(visible=False)
            window["csvnumbertext"].update(visible=False)
            window["2csv"].update(visible=False)
            window["3csv"].update(visible=False)
            window["4csv"].update(visible=False)
            window["2csv"].update(visible=False)
            window["addfile"].update(visible=False)
            window["sameplotMultiplot"].update(visible=False)
            window["subplotMultiplot"].update(visible=False)
            window["diffplotMultiplot"].update(visible=False)
            
        if values["dirGraph"] == True:
            window["folderBrowse"].update(visible=True)
        else:
            window["folderBrowse"].update(visible=False)

            
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
        
        
    # if the GUI window is closed, break the code
    if event == sg.WIN_CLOSED:
        break