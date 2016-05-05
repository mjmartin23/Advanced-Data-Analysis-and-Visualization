# Authors: Matt Martin and Adam Carlson
# Date: 05/01/16
# display: This program allows the user to read in data from a csv file. The data can
	# then be viewed, scaled, panned, and reoriented in 3-D space. In addition, the program
	# can utilize the webcam and provided color detectors in order to provide the same
	# functionality with hand motions.

import Tkinter as tk
import tkFont as tkf
import tkMessageBox
import math
import random
import view
import numpy as np
import sys
import tkFileDialog
import data
import analysis
import scipy.stats
import tkSimpleDialog
import video as tV


# create a class to build and manage the display
class DisplayApp:
	
	# initializes the display app
	def __init__(self, width, height):
		
		# stores hand motion information
		self.colorDiff = 0
		self.stillVideo = False
		self.prevAreaG = 4.0
		self.prevPosG = (200,200)
		self.prevAreaB = 4.0
		self.prevPosB = (200,200)
		self.counter = 0
		self.video = None
		
		# stores the rightctnlframe position at a higher scope
		self.position = None
		
		# tells whether at least one analysis has been made
		self.made_analysis = False
		
		# stores the listbox where the analysis selects appear
		self.box = None

		# create a tk object, which is the root window
		self.root = tk.Tk()
		
		# stores information in text form for the user about how the program is running
		self.label = None
		
		# width and height of the window
		self.initDx = width
		self.initDy = height

		# set up the geometry for the window
		self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )
		
		# reads in previously established name
		f = open('name.txt', 'r')
		self.name = f.readlines()[0]
		 
		
		# set the title of the window
		self.root.title("Basic Data Visualization")

		# set the maximum size of the window for resizing
		self.root.maxsize( 1600, 900 )

		# setup the menus
		self.buildMenus()
		
		# stores whether the ok button was pressed for the dialog box
		self.ok = True
		
		# stores the number of random points to be printed to the screen
		self.numData = tk.StringVar(self.root, value=300)
		
		# stores the shape type of the data points
		self.shapeOption = "Dot"
		
		# build the controls
		self.buildControls()

		# build the Canvas
		self.buildCanvas()

		# bring the window to the front
		self.root.lift()

		# - do idle events here to get actual canvas size
		self.root.update_idletasks()
		
		# stores the view object
		self.view = view.View()

		# now we can ask the size of the canvas
		print self.canvas.winfo_geometry()
		
				# set up the application state
		self.objects = [] # list of data objects that will be drawn in the canvas
		self.data = None # will hold the raw data someday.
		self.baseClick = None # used to keep track of mouse movement for translating
		self.baseClick2 = None # used to keep track of mouse movement for rotating
		self.baseExtent = None # stores the original extent before scaling
		self.viewClone = None # stores a clone of the view object when needed
		
		# stores the data for each coordinate
		self.xData = None
		self.yData = None
		self.zData = None
		self.colorData = None
		self.sizeData = None
		
		# stores a list of all the data sizes if given 5 dimensions to plot
		self.sizes = None
		
		# stores the base axes
		self.axes = np.matrix([[0,0,0,1],[1,0,0,1],[0,0,0,1],[0,1,0,1],[0,0,0,1],[0,0,1,1]])
		
		# stores the lines which visually show the base axes
		self.lines = []
		
		# stores the oval/square data shapes displayed on the screen
		self.dataObjects = []
		
		
		
		# stores a matrix of all the data that is displayed on the screen
		self.points = None
		
		# stores the canvas regression line objects
		self.regressionLines = []
		
		# stores the matrix data for the regression line coordinates
		self.regressionMatrix = None
		
		# stores the data associated with each PCA analysis in a dictionary
		self.results = {}
		
		#stores ten colors for clustering
		# red, green, blue, yellow, grey, pink, lightblue, black, orange, purple
		self.colors = [ (255.0,0.0,0.0), (0.0,255.0,0.0), (0.0,0.0,255.0), (255.0,255.0,0.0), (192.0,192.0,192.0),  (255.0,51.0,255.0), (0.0,255.0,255.0), (0.0,0.0,0.0), (255.0,128.0,0.0), (153.0,51.0,255.0)      ]

		# set up the key bindings
		self.setBindings()


	# handles opening and reading in a file
	def handleOpen(self, event=None):
		 fn = tkFileDialog.askopenfilename( parent=self.root, title='Choose a data file', initialdir='.' )
		 if fn != "":
			if fn[-4:] !=".csv":
				tkMessageBox.showwarning("Instructions", "You must select a csv file")
				return 
				
			self.data = data.Data(fn)
			self.label["text"] = "File Successfully Uploaded"
			self.addedCategory = 0
		 else:
			self.label["text"] = "No file selected" 
		 
	# handles plotting the data by calling other helper functions
	def handlePlotData(self, headers = '', notSmooth = '', codes=None):
		if self.data == None:
			
			tkMessageBox.showwarning(
			"Instructions", "First upload a csv file before selecting data"
		)
			return
		
		if headers == '':	
			self.buildPoints( self.handleChooseAxes() )
		else:
			self.buildPoints( self.handleChooseAxes(headers, True), notSmooth, codes )	
	
	# creates a dialog box for the user to choose what data goes on each axis	
	def handleChooseAxes(self, headers = '', cluster=False):
		
		if headers == '':
			self.createDialog(self.data.get_headers())
		else:
			self.createDialog(headers, cluster=True)	
		print "okField ", self.ok
		ret = []
		if self.ok == False:
			self.label['text'] = "Data selection cancelled"
			return None
		if self.xData == None or self.yData == None:
			print "in here again"
			tkMessageBox.showwarning("Instructions", "You must input data for the x and y coordinates")
			return None
		ret.append(self.xData)
		ret.append(self.yData)
		if self.zData != None:
			ret.append(self.zData)
		if self.colorData != None:
			ret.append(self.colorData)
		if self.sizeData != None:
			ret.append(self.sizeData)
					
		return [self.xData,self.yData, self.zData, self.colorData, self.sizeData]	
	
	# builds the menus	
	def buildMenus(self):
		
		# create a new menu
		menu = tk.Menu(self.root)

		# set the root menu to our new menu
		self.root.config(menu = menu)

		# create a variable to hold the individual menus
		menulist = []

		# create a file menu
		filemenu = tk.Menu( menu )
		menu.add_cascade( label = "File", menu = filemenu )
		menulist.append(filemenu)

		# create another menu for kicks
		cmdmenu = tk.Menu( menu )
		menu.add_cascade( label = "Data", menu = cmdmenu )
		menulist.append(cmdmenu)

		# menu text for the elements
		# the first sublist is the set of items for the file menu
		# the second sublist is the set of items for the option menu
		menutext = [ [ '-', '-', 'Quit	\xE2\x8C\x98-Q', '-', '-','Clear  \xE2\x8C\x98-N', '-', '-','Open  \xE2\x8C\x98-O' ],
					 [ 'Plot Regression', '-', '-', 'PCA Analysis', '-', '-', 'Show PCA Data', '-', '-','Cluster Data', '-', '-'  ] ]

		# menu callback functions (note that some are left blank,
		# so that you can add functions there if you want).
		# the first sublist is the set of callback functions for the file menu
		# the second sublist is the set of callback functions for the option menu
		menucmd = [ [None, None, self.handleQuit, None, None, self.clearData, None, None, self.handleOpen],
					[self.handleLinearRegression, None, None, self.handlePCA, None, None, self.showPCA, None, None, self.cluster, None, None] ]
		
		# build the menu elements and callbacks
		for i in range( len( menulist ) ):
			for j in range( len( menutext[i]) ):
				if menutext[i][j] != '-':
					menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
				else:
					menulist[i].add_separator()

	# create the canvas object
	def buildCanvas(self):
		self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy )
		self.canvas.pack( expand=tk.YES, fill=tk.BOTH )
		return

	# build a frame and put controls in it
	def buildControls(self):

		### Control ###
		# make a control frame on the right
		self.position = tk.Frame(self.root)
		self.position.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)
		rightcntlframe = self.position
		print "In Build"
		print self.position	
		# make a separator frame
		sep = tk.Frame( self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
		sep.pack( side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)

		# labels that holds name of user
		self.nameLabel = tk.Label( rightcntlframe, text="Welcome " + self.name, width=20 )
		self.nameLabel.pack( side=tk.TOP, pady=10 )
		
		# used to crawl internet for potential csv sources
		nameButton = tk.Button( rightcntlframe, text="Change Name", 
							   command=self.changeName , pady=20)
		nameButton.pack(side=tk.TOP)  # default side is top
		
		
		
		# holds the color of the data
		self.colorOption = tk.StringVar( self.root )
		
		self.colorOption.set("black")
		
		
		
		# label and menu for shape selection
		label = tk.Label( rightcntlframe, text="Select a Shape:", width=20 )
		label.pack( side=tk.TOP, pady=5 )
		self.shapeOption = tk.StringVar( self.root )
		self.shapeOption.set("Dot")
		shapeMenu = tk.OptionMenu( rightcntlframe, self.shapeOption, 
										"Dot","Square") # can add a command to the menu
		shapeMenu.pack(side=tk.TOP)
							  
		
		# button to generate random points
		button2 = tk.Button( rightcntlframe, text="Select Data", 
							   command=self.handlePlotData , pady=10)
							  
		button2.pack(side=tk.TOP)  # default side is top
		
		# reset orientation button
		button3 = tk.Button( rightcntlframe, text="Reset Orientation", 
							   command=self.resetOrientation , pady=10)
							  
		button3.pack(side=tk.TOP)  # default side is top
		button1 = tk.Button( rightcntlframe, text="Initialize Hand Control",
							 command=self.startVideo, pady=10).pack(side=tk.TOP)
		
		# labels for the color coordinating of the base axes
		label = tk.Label( rightcntlframe, text="X-Axis: Green", width=20, fg='green' )
		label.pack( side=tk.TOP, pady=2 )
		label = tk.Label( rightcntlframe, text="Y-Axis: Red", width=20, fg='Red' )
		label.pack( side=tk.TOP, pady=2 )
		label = tk.Label( rightcntlframe, text="Z-Axis: Blue", width=20, fg='Blue' )
		label.pack( side=tk.TOP, pady=2 )
		
		# tells the user new information about the program as it runs
		label = tk.Label( rightcntlframe, text="Program Messages:", width=20, fg='Black' )
		label.pack( side=tk.TOP, pady=2 )
		self.label = tk.Label( rightcntlframe, text="No New Messages", width=20, fg='green' )
		self.label.pack( side=tk.TOP, pady=2 )
		
		
		
		
		return
	
	# set the bindings
	def setBindings(self):
		#button1 bindings: left click
		self.canvas.bind( '<Button-1>', self.handleLeftClick )
		self.canvas.bind( '<B1-Motion>', self.handlePanning )
		
		#button2 bindings: right click
		self.canvas.bind( '<Button-2>', self.handleRightClick )
		self.canvas.bind( '<B2-Motion>', self.handleRotating )
		self.canvas.bind( '<Control-Button-1>', self.handleRightClick )
		self.canvas.bind( '<Control-Button1-Motion>', self.handleRotating )
		
		#button3 bindings: middle scroll button
		self.canvas.bind( '<Button-3>', self.handleScrollClick )
		self.canvas.bind( '<B3-Motion>', self.handleScaling )
		

		# bind command sequences to the root window
		self.root.bind( '<Command-q>', self.handleQuit )
		self.root.bind( '<Command-n>', self.clearData )
		self.root.bind( '<Command-o>', self.handleOpen )
		self.root.bind( '<Command-d>', self.deleteAnalysis )
	
	# terminates app
	def handleQuit(self, event=None):
		print 'Terminating'
		self.root.destroy()
	
	# clears current data	
	def clearData(self, event=None):
		print 'Clearing'
		self.objects = []
		self.dataObjects = []
		self.canvas.delete("all")
		self.buildAxes()
	
	# changes the name of the user	
	def changeName(self, event=None):
		newName = tkSimpleDialog.askstring("Change User Name", "Please enter a new name:")
		if newName != None:
			file = open("name.txt", "w")
			
			file.write(newName)
		file.close()
		
		self.nameLabel["text"] = "Welcome " + newName			
	
	# handles deleting an analysis (CMD-d)	
	def deleteAnalysis(self,event=None):
		if len(self.box.curselection()) > 0:
			self.results.pop(self.box.get(self.box.curselection()[0]), None)
			self.box.delete(self.box.curselection()[0])
			
		else:		
			tkMessageBox.showwarning("Instructions", "Please select an analysis")
	
	# allows you to select data for a PCA analysis		
	def handlePCA(self, event=None):
		if self.data == None:
			tkMessageBox.showwarning("Instructions", "You must read in a file first")
			return
		headers = self.data.get_headers()	
		p = PCASelect(self.root,headers)
		print p.result
		if not p.result:
			return
		else:
			if p.result[2] in self.results.keys():
				tkMessageBox.showwarning("Instructions", "You have already used that filename. Either delete it (Select then Cmd-d) or choose a new name")
				return
			self.label['text'] = "PCA Read Successful"
			self.results[p.result[2]] = [self.data, p.result[1], p.result[0] ] 
			if not self.made_analysis:
				self.made_analysis = True
				label = tk.Label( self.position, text="PCA Data Sets", width=20, fg='Black' )
				label.pack( side=tk.TOP, pady=2 )
				self.box = tk.Listbox(self.position, selectmode=tk.SINGLE, exportselection=0)
				self.box.pack( side=tk.TOP, pady=2 )
				button = tk.Button( self.position, text="Plot PCA", 
							   command=self.plotPCA )
				button.pack(side=tk.TOP)  # default side is top
			self.box.insert(tk.END, p.result[2])
	
	# handles actually plotting the PCA analysis		
	def plotPCA(self,event=None):
		if len(self.box.curselection()) > 0:
			selected = self.box.get(self.box.curselection()[0])
			dataInfo = self.results[selected]
			newData = None
			print dataInfo[1]
			if dataInfo[2] == 1:
				newData = analysis.pca(dataInfo[0], dataInfo[1])
			else:
				newData = analysis.pca(dataInfo[0], dataInfo[1], normalize=False)	
			
			temp = self.data
			self.data = newData
			self.buildPoints( self.handleChooseAxes() )
			self.data = temp	 
			
		else:
			tkMessageBox.showwarning("Instructions", "Please select an analysis")		
	
	# handles showing the PCA results with all eigenvectors included		
	def showPCA(self, event=None):
		if self.box != None and len(self.box.curselection()) > 0:
			selected = self.box.get(self.box.curselection()[0])
			dataInfo = self.results[selected]
			newData = None
			if dataInfo[2] == 1:
				newData = analysis.pca(dataInfo[0], dataInfo[1])
			else:
				newData = analysis.pca(dataInfo[0], dataInfo[1], normalize=False)	
			print newData.get_eigenvalues()
				
			PCAShowDialog(self.root,newData)
			
		else:
			tkMessageBox.showwarning("Instructions", "Please run a PCA analysis, then select a data set to examine")
			
	# asks the user for needed information and then clusters the data		
	def cluster(self, event = None):
		if self.data == None:
			tkMessageBox.showwarning("Instructions", "You must read in a file first")
			return
		headers = self.data.get_headers()
		output = ClusterSelect(self.root, headers)
		if output.okField == False:
			self.label['text'] = "Data selection cancelled"
			return
		if output.result == False:
			return	
		print output.result
		codes = analysis.kmeans(self.data, output.result[0], output.result[1], whiten=True, categories = '')[1]
		newCol = ["Categories", "numeric"]
		codes = codes.T.tolist()[0]
		for code in codes:
			newCol.append(code)
		self.data.addData(newCol)
		newHeaders =output.result[0]
		newHeaders.append("Categories")
		print "Cheking if checked"
		print output.result[1]
		d = self.handlePlotData(newHeaders, output.result[2], codes)
		
		# removes the added Categories column once finished
		self.data.removeLast()
					
	
	# creates a dialog box to ask the user for independent and dependent variables for regression	
	def handleLinearRegression(self, event=None):
		if self.data == None:
			tkMessageBox.showwarning("Instructions", "You must read in a file first")
			return
		d = RegressionBox(self.root, "Select Data types", self.data.get_headers())
		if d.okField == False:
			self.label['text'] = "Regression cancelled"
			return
		if d.result == [] or d.result[0] == None or d.result[1] == None:
			return
		else:
			self.clearData()
			self.resetOrientation()
			self.regressionLines = []
			self.regressionMatrix = None
			self.updateAxes()
			self.buildLinearRegression(d.result)
	
	# handles actually getting the regression line on the screen		
	def buildLinearRegression(self,headers):
		
		
		normalized = analysis.normalize_columns_separately( headers, self.data )
		
		list = normalized.tolist()
		for row in range(len(list)):
			list[row].append(0)
			list[row].append(1)
		normalized = np.matrix(list)	
		self.points = normalized
		vtm = self.view.build()
		pts = (vtm * self.points.T).T
		for i in range( pts.shape[0] ):
			row = pts.tolist()[i]
			dx = 3
			dy = 3
			
			
			
			if self.shapeOption.get() == "Dot":		
				pt = self.canvas.create_oval( row[0]-dx, row[1]-dx, row[0]+dx, row[1]+dx,
											  fill=self.colorOption.get(), outline='', tags="data" )
				self.dataObjects.append(pt)							  
				self.objects.append(pt)
										  
			
			elif self.shapeOption.get() == "Square":
				pt = self.canvas.create_rectangle( row[0]-dx, row[1]-dx, row[0]+dx, row[1]+dx,
											  fill=self.colorOption.get(), outline='', tags ="data" )
				self.dataObjects.append(pt) 
				self.objects.append(pt)
		
		unnormalized = self.data.get_data(headers).T.tolist()	
		regress_output = scipy.stats.linregress(unnormalized[0],unnormalized[1])
		m = round(regress_output[0],3)
		b = round(regress_output[1], 3)
		r = round(regress_output[2]*regress_output[2], 3)
		ranges = analysis.data_range(headers,self.data)
		xmin = ranges[0][0]
		xmax = ranges[0][1]
		ymin = ranges[1][0]
		ymax = ranges[1][1]
		pt1 = [0.0, ((xmin * m + b) - ymin)/(ymax - ymin),0,1 ]
		pt2 = [1.0, ((xmax * m + b) - ymin)/(ymax - ymin),0,1 ]
		print "point1"
		print pt1
		print "point2"
		print pt2		
		self.regressionMatrix = np.matrix([pt1,pt2])	
		pts = (vtm * self.regressionMatrix.T).T
		print pts
		best_fit = self.canvas.create_line(pts[0,0],pts[0,1],pts[1,0],pts[1,1], width=3, fill='gold',tags="data")
		self.regressionLines.append(best_fit)
		self.label['text'] = "The best fit line equation:\n y = " + str(m) + "x + " + str(b)+"\n\nR^2 value: " + str(r)
						
	
	# reset orientation axes	
	def resetOrientation(self, event=None):
		self.view.reset()
		self.updatePoints()
		self.updateAxes()

	# updates the data color
	def handleButton1(self):
		for obj in self.objects:
			self.canvas.itemconfig(obj, fill=self.colorOption.get() )
	
													  
				
	# handles first menu command: empty for now
	def handleMenuCmd1(self):
		print 'handling menu command 1'
	
	# runs after left click
	def handleLeftClick(self, event):
		print 'handle mouse button 1: %d %d' % (event.x, event.y)
		self.baseClick = (event.x, event.y)
		
	
		
	# runs after right click
	def handleRightClick(self, event):
		self.baseClick2 = (event.x, event.y)
		self.viewClone = self.view.clone()
		print 'handle mouse button 2: %d %d' % (event.x, event.y)
		# dx = 3
#		rgb = "#%02x%02x%02x" % (random.randint(0, 255), 
#									 random.randint(0, 255), 
#									 random.randint(0, 255) )
#		oval = self.canvas.create_oval( event.x - dx,
#											event.y - dx, 
#											event.x + dx, 
#											event.y + dx,
#											fill = rgb,
#											outline='')
#		self.objects.append( oval ) 
	
	# handle scroll button click	
	def handleScrollClick(self, event):
		print 'handle mouse button 3: %d %d' % (event.x, event.y)
		self.baseClick = (event.x, event.y)
		self.baseExtent = self.view.clone().extent
		
	

	
	# pans the data, a none-zero value for motion indicates webcam is on
	def handlePanning(self, event, motion = 0):

		if motion is not 0:
			dx = -1.0*float(motion[0])
			if math.fabs(motion[0]) < .005:
				dx = 0.0
			dx = dx / self.view.screen[0]
			dx = dx * self.view.extent[0]
			delta0 = dx

			dy = float(motion[1])
			if math.fabs(motion[1]) < .005:
				dy = 0.0	
			dy = dy / self.view.screen[1]
			dy = dy * self.view.extent[1]
			delta1 = dy

		else:

			dx = float(event.x - self.baseClick[0])
			dx = dx / self.view.screen[0]
			dx = dx * self.view.extent[0]
			delta0 = dx

			dy = float(event.y - self.baseClick[1])
			dy = dy / self.view.screen[1]
			dy = dy * self.view.extent[1]
			delta1 = dy

			self.stillVideo = False
		
		self.view.vrp = self.view.vrp + delta0*self.view.u+delta1*self.view.vup
		if len(self.dataObjects) > 0:
			self.updatePoints()
		self.updateAxes()
		self.updateRegression()
		
		if motion == 0:
			self.baseClick = (event.x,event.y)


			
	# rotates the data with right button click motion, a none-zero value for motion indicates webcam is on
	def handleRotating(self, event, motion = 0):
		if motion is not 0:
			
		
			
			delta0 = min(float(motion)*4096, 1024.0) / (self.canvas.winfo_width()) * math.pi
			
			delta1 = 0.0
			

		else:
			delta0 = float(event.x - self.baseClick2[0]) / (self.canvas.winfo_width()) * math.pi
			delta1 = float(event.y - self.baseClick2[1]) / (self.canvas.winfo_height()) * math.pi
		
		self.view = self.viewClone.clone()

		self.view.rotateVRC( delta0, delta1 )
		
		self.updateAxes()
		
		if len(self.dataObjects) > 0:
			self.updatePoints()
		self.updateRegression()	
	
	
	# scales the data with scroll button motion, a none-zero value for motion indicates webcam is on 
	def handleScaling(self, event, motion = 0):
		
		if motion is not 0:
			if math.fabs(motion) < .002:
				return
			
			if motion < 0:
				dy = motion*5000.0
			else:	
				dy = motion*5000.0
		else:	
			dy = float(event.y-self.baseClick[1])
			self.stillVideo = False
		k = 1.0/self.canvas.winfo_height()
		f = 1.0+k*dy
		f=max(.1,min(f,3.0) )
		self.view.extent = [self.baseExtent[0]*f, self.baseExtent[1]*f, self.baseExtent[2]*f]
		self.updateAxes()
		if len(self.dataObjects) > 0:
			self.updatePoints()
		self.updateRegression()	
		
	
	# creates the dialog box, records answers
	def createDialog(self, headers, cluster=False):
		
		d = SelectDistr(self.root, "Select Your Data", headers, cluster)
		self.ok = d.okField
		if d.result != [] and len(d.result) > 1:
			self.xData = d.result[0]
			self.yData = d.result[1]
			self.zData = d.result[2]
			self.colorData = d.result[3]
			self.sizeData = d.result[4]
		
	
	# builds the initial axes	
	def buildAxes(self):
		vtm = self.view.build()
		pts = (vtm * self.axes.T).T
		pts = pts.tolist()
		xAxis = self.canvas.create_line(pts[0][0],pts[0][1],pts[1][0],pts[1][1], width=3, fill='green')
		yAxis = self.canvas.create_line(pts[2][0],pts[2][1],pts[3][0],pts[3][1], width=3, fill='red')
		zAxis = self.canvas.create_line(pts[4][0],pts[4][1],pts[5][0],pts[5][1], width=3, fill='blue')
		self.lines = [xAxis,yAxis,zAxis]
		
	
	# builds the data points	
	def buildPoints(self,headers,categories=False, codes = None):
			
		self.sizes = None
		if headers == None:
			return
		
		# stores the number of dimensions read in	
		realLength = 0
		
		# stores the features that were not equal to None when read in
		realHeaders = []
		
		for header in headers:
			if header != None:
				realLength += 1
				realHeaders.append(header)
				
		numHeaders = len(headers)
		
		# first delete all data points already on screen
		self.canvas.delete("data")
		
		# creates self.points if no z-dimension
		self.dataObjects = []
		if realLength >= 2 and headers[2] == None:
			data = self.data.get_data([headers[0],headers[1]])
			data = data.tolist()
			for i in range(len(data)):					
				data[i].append(0)
				data[i].append(1)
			print "making a numpy matrix"
			self.points = np.matrix(data)

		
		# keeps track of all dimensions of data
		allData = self.data.get_data(realHeaders)
		colorIndex = 3
		sizeIndex = 4
		if headers[2] == None:
			colorIndex = 2
		if headers[2] == None and headers[3] == None:
			sizeIndex = 2
		elif headers[2] == None or headers[3] == None:
			sizeIndex = 3		
		
	
		colorData = self.data.get_data( [ realHeaders[-1] ] )
	
		
		# creates self.points when a z-dimension exists	
		if realLength > 2 and headers[2] != None:
			tempHeaders = [headers[0],headers[1],headers[2]]
			data = self.data.get_data(tempHeaders)
			data = data.tolist()
			for i in range(len(data)):					
				data[i].append(1)
			self.points = np.matrix(data)
			
			
			
			
		mins = np.amin(self.points, axis = 0)	
		maxes = np.amax(self.points, axis = 0)
		
		if headers[3] == None:
			self.colorOption.set("black")
			

		# normalizes without z-dimension
		if realLength == 2 or (realLength >= 3 and headers[2] == None):
			for i in range( self.points.shape[0] ):
				for j in range( self.points.shape[1]-2 ):
					self.points[i,j] = float( self.points[i,j] - mins[0,j] )/ float( maxes[0,j] - mins[0,j] )
		
		# normalizes if z-dimension is present			
		if realLength >= 3 and headers[2] != None:
					
			for i in range( self.points.shape[0] ):
				for j in range( self.points.shape[1]-1 ):
					self.points[i,j] = float( self.points[i,j] - mins[0,j] )/ float( maxes[0,j] - mins[0,j] )
		
		# normalize allData matrix as well for color and size calculations
	
		if realLength >= 3:
			mins = np.amin(allData, axis = 0)	
			maxes = np.amax(allData, axis = 0)
			for i in range( allData.shape[0] ):
				for j in range( allData.shape[1] ):
					allData[i,j] = float( allData[i,j] - mins[0,j] )/ float( maxes[0,j] - mins[0,j] )
		
								
		# builds view pipeline		
		vtm = self.view.build()
		
		
		pts = (vtm * self.points.T).T
		
		# initializes field to empty list
		if headers[4] != None:
			self.sizes = []
			
		print "Shape option: {}".format( self.shapeOption.get() )
		
		for i in range( pts.shape[0] ):
			row = pts.tolist()[i]
			dx = 3
			dy = 3
			
			if categories == False or categories == 0:
				if headers[3] != None:
					rgb = (255.0*float(allData[i,colorIndex]),255.0*float(1-allData[i,colorIndex]),0.0)
					#print rgb
					self.colorOption.set('#%02x%02x%02x' % rgb)
					
			if categories == 1:	
				self.colorOption.set( '#%02x%02x%02x' % self.colors[int(codes[i])] )
				
			
			elif self.data.get_headers()[-1] == "class":
				self.colorOption.set( '#%02x%02x%02x' % self.colors[ int(colorData[i]) ] )	
				
			if headers[4] != None:
				
				
				dx =3 + 7 * float(allData[i,sizeIndex])
				self.sizes.append(dx)	
			
			
			if self.shapeOption.get() == "Dot":		
				pt = self.canvas.create_oval( row[0]-dx, row[1]-dx, row[0]+dx, row[1]+dx,
											  fill=self.colorOption.get(), outline='', tags="data" )
				self.dataObjects.append(pt)							  
				self.objects.append(pt)
										  
			
										  
			elif self.shapeOption.get() == "Square":
				pt = self.canvas.create_rectangle( row[0]-dx, row[1]-dx, row[0]+dx, row[1]+dx,
											  fill=self.colorOption.get(), outline='', tags ="data" )
				self.dataObjects.append(pt) 
				self.objects.append(pt)
			
			string = ""
			if numHeaders > 1:
				string += "X-Data: "
				string += str(self.xData)
				string += "\n"
				string += "Y-Data: "
				string += str(self.yData)
				string += "\n"
				
			if numHeaders > 2 and headers[2] != None:
				string += "Z-Data: "
				string += str(self.zData)
				string += "\n"
				
			if headers[3] != None:
				string += "Color-Data: "
				string += str(self.colorData)
				string += "\n"
				
			if headers[4] != None:
				string += "Size-Data: "
				string += str(self.sizeData)
				string += "\n"			
				
			self.label["text"] = string
			
		self.startVideo()
		#self.root.after(1000,self.handleVideo)
	
	# if given permission, tracks hand motions for data control 
	def startVideo(self):
		result = tkMessageBox.askquestion("Webcam Permission", "Would you like the program to have access to your webcam? You will be able to control data via hand motions if you have the designed hand trackers?", icon='warning')
		if result != "yes":
			return
		self.video = tV.Video(True)
		self.stillVideo = True
		self.counter = 0
		self.root.after(1000, self.handleVideo)
	
	# tracks hand motions
	# green detector is for zooming and panning
	# moving green and red detectors from and to screen simultaneously causes rotating
	# if the green detector is not detected webcam resets orientation and waits for green
		# shown again				
	def handleVideo(self):
		
		self.baseExtent = self.view.clone().extent
		
		# run one frame of video
		ret = self.video.run()
		
		# exit video if needed
		if ret == -1:
			self.stillVideo = False
			return
			
		if not self.stillVideo:
			self.video.end()
			return
		
		# use a multiplier to make distances/centers more easily usable with pixels	
		dstG = ret[0]*10
		dstR = ret[1]*10
		centerG = ret[2]
		centerR = ret[3]
		
		# finds where resting position of detectors is within first 10 frames
		if self.counter < 10:
			self.counter += 1
			self.prevAreaG = dstG
			self.prevPosG = centerG
			if self.stillVideo:
				self.root.after(5,self.handleVideo)
			return
		
		# reset orientation if green detector out of view 
		elif dstG >= 11.5:
			if self.stillVideo:
				self.resetOrientation()
				self.counter = 0
				if self.stillVideo:
					self.root.after(5,self.handleVideo)
			return			
		
		# calculate change in green pixel area
		differenceG = dstG - self.prevAreaG
		

		# calculate change in green pixel center
		posDiffG = (centerG[0]-self.prevPosG[0],centerG[1]-self.prevPosG[1])

		
		self.prevAreaG = dstG
		self.prevPosG = centerG
		
		# if red detector sensed, try rotating data
		if dstR != 0:
			colorDiff = self.colorDiff-(dstG-dstR)
			self.viewClone = self.view.clone()
			self.handleRotating( None, motion = colorDiff )
			self.colorDiff = dstG-dstR 
			if self.stillVideo:
				self.root.after(5,self.handleVideo)
			return
			
		# reset orientation but not scale if rotating performed but red no longer detected	
		elif dstR == 0 and self.colorDiff != 0:
			self.colorDiff = 0
			self.view.miniReset()
		
		# perform scaling		
		self.handleScaling(None, motion = differenceG)
		
		# perform panning
		self.handlePanning(None, motion=posDiffG)	

		if not self.video.capture.isOpened():
			self.stillVideo = False
		
		# recall function in 5 milliseconds to allow program to update in other areas
		if self.stillVideo:
			self.root.after(5,self.handleVideo)
			
		else:
			self.video.end()
			

				
	# updates the axes after translating, scaling, rotating, etc.
	def updateAxes(self):
		vtm = self.view.build()
		pts = (vtm * self.axes.T).T.tolist()
		#print pts
		#print "First axis: {}".format(pts[0])
		
		for i in range(len(self.lines)):
			#print (pts[2*i][0],pts[2*i][1],pts[2*i+1][0],pts[2*i+1][1])
			self.canvas.coords(self.lines[i], pts[2*i][0],pts[2*i][1],pts[2*i+1][0],pts[2*i+1][1])
		
	# updates the points after a pan, rotation, or scale	
	def updatePoints(self):
		
		if self.points == None:
			return 
		vtm = self.view.build()
		
		
		pts = (vtm * self.points.T).T.tolist()
		
	
	
		
		
		for i in range(len(self.dataObjects)):
			if self.sizes == None:
				self.canvas.coords(self.dataObjects[i], pts[i][0]-3, pts[i][1]-3,pts[i][0]+3, pts[i][1]+3)
			else:	
				self.canvas.coords(self.dataObjects[i], pts[i][0]-self.sizes[i], pts[i][1]-self.sizes[i],pts[i][0]+self.sizes[i], pts[i][1]+self.sizes[i])
	
	# updates the regression line after a pan, scale, or rotation	
	def updateRegression(self):
		if self.regressionMatrix != None:
			vtm = self.view.build()
		
		
			pts = (vtm * self.regressionMatrix.T).T.tolist()
			
		for i in range(len(self.regressionLines)):
			
			self.canvas.coords(self.regressionLines[i], pts[i][0], pts[i][1],pts[i+1][0], pts[i+1][1])
	
			
	# crawls the internet for data for a certain source and pops up with potential website options			

			
	
	# runs the main loop
	def main(self):
		print 'Entering main loop'
		self.root.mainloop()

# tk dialog class		
class Dialog(tk.Toplevel):

	def __init__(self, parent, title = None, headers=None):

		tk.Toplevel.__init__(self, parent)
		self.transient(parent)
		
		if title:
			self.title(title)

		self.parent = parent
		
		self.headers = headers
		
		self.result = []
		
		self.okField = False
	
		body = tk.Frame(self)
		self.initial_focus = self.body(body)
		body.pack(padx=5, pady=5)

		self.buttonbox()

		self.grab_set()

		if not self.initial_focus:
		   self.initial_focus = self

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
								  parent.winfo_rooty()+50))

		self.initial_focus.focus_set()

		self.wait_window(self)
		
		
		
		
	#
	# construction hooks

	def body(self, master):
		# create dialog body.  return widget that should have
		# initial focus.  this method should be overridden

		pass

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons

		box = tk.Frame(self)

		w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

	#
	# standard button semantics

	def ok(self, event=None):

		if not self.validate():
			self.initial_focus.focus_set() # put focus back
			return

		self.withdraw()
		self.update_idletasks()

		self.okField = True
		
		self.apply()

		self.cancel()
		
		
	def cancel(self, event=None):
		
		# put focus back to the parent window
		self.parent.focus_set()
		self.destroy()
		

	#
	# command hooks

	def validate(self):

		return 1 # override

	def apply(self):

		pass # override		

# my dialog subclass
class SelectDistr(Dialog):
	
	def __init__(self, parent, title, headers, cluster=False):
		
		self.cluster = cluster
		Dialog.__init__(self, parent, title, headers)
	
	def body(self, master):
			
			# creates labels for x and y
			tk.Label(master, text="X-Data:").grid(row=0)
			tk.Label(master, text="Y-Data:").grid(row=1)
			tk.Label(master, text="Z-Data:").grid(row=2)
			tk.Label(master, text="Color Dimension:").grid(row=3)
			tk.Label(master, text="Size Dimension:").grid(row=4)
			
			# creates a listbox for each coordinate with basic spacing
			self.e1 = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
			self.e2 = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
			self.e3 = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
			self.e4 = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
			self.e5 = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
			
			self.e1.grid(row=0, column=1)
			self.e2.grid(row=1, column=1)
			self.e3.grid(row=2, column=1)
			self.e4.grid(row=3, column=1)
			self.e5.grid(row=4, column=1)
			
			for i in range(len(self.headers)):
				if i == len(self.headers) - 1 and self.cluster:
					break
				
				self.e1.insert(tk.END, self.headers[i])
				self.e2.insert(tk.END, self.headers[i])
				self.e3.insert(tk.END, self.headers[i])
				
				if(self.cluster == False):
					self.e4.insert(tk.END, self.headers[i])
					
				self.e5.insert(tk.END, self.headers[i])
			if self.cluster == True:
				self.e4.insert(tk.END, self.headers[-1])	
			
			return None
	
	#records user input into dialog box
	def apply(self):
						
		self.result.append( self.e1.get(tk.ACTIVE) )
		self.result.append( self.e2.get(tk.ACTIVE) )
		
		self.result.append( self.e3.get(tk.ACTIVE) )
	
		self.result.append( self.e4.get(tk.ACTIVE) )
		self.result.append( self.e5.get(tk.ACTIVE) )
		
		
		if not self.e1.curselection():
			self.result[0] = None
			print "e1 active is ", self.result[0]
		if not self.e2.curselection():
			self.result[1] = None
			print "e2 active is ", self.result[1]	
		if not self.e3.curselection():
			self.result[2] = None
			print "e3 active is ", self.result[2]
		if not self.e4.curselection():
			self.result[3] = None
			print "e4 active is ", self.result[3]
		if not self.e5.curselection():
			self.result[4] = None
			print "e5 active is ", self.result[4]

# dialog box to determine for which data to plot a regression line			
class RegressionBox(Dialog):
	def body(self, master):
			
			# creates labels for x and y
			tk.Label(master, text="Independent Variable:").grid(row=0)
			tk.Label(master, text="Dependent Variable").grid(row=1)
			
			
			# creates a listbox for each coordinate with basic spacing
			self.e1 = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
			self.e2 = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
			
			
			self.e1.grid(row=0, column=1)
			self.e2.grid(row=1, column=1)
		
			
			for i in range(len(self.headers)):
				
				self.e1.insert(tk.END, self.headers[i])
				self.e2.insert(tk.END, self.headers[i])
				
			
			return None
	
	#records user input into dialog box
	def apply(self):
						
		self.result.append( self.e1.get(tk.ACTIVE) )
		self.result.append( self.e2.get(tk.ACTIVE) )
		
		
		
		if not self.e1.curselection():
			self.result[0] = None
			print "e1 active is ", self.result[0]
		if not self.e2.curselection():
			self.result[1] = None
			print "e2 active is ", self.result[1]	
		
		length = 0
		for i in range(len(self.result)):
			if self.result[i] != None:
				length+=1
		
		if(length == 2):
			
			return self.result
		else:
			tkMessageBox.showwarning("Instructions", "You must select an independent and a dependent variable")
			return None

class PCASelect(Dialog):
	def __init__(self, parent, headers):
		
		self.normalized = tk.IntVar(parent, value=0)
		self.name = tk.StringVar(parent, value="Default")
		self.boxSettings = None
		Dialog.__init__(self, parent, "Principal Component Analysis", headers=headers)
		
	def body(self, master):
			
		tk.Label(master, text=" Choose PCA Variables\n").grid(row=0)
		tk.Label(master, text="PCA Name").grid(row=1)
		tk.Entry(master, textvariable=self.name).grid(row=2)
		tk.Checkbutton(master, text="Normalize", variable=self.normalized).grid(row=3)
		
		self.boxSettings = tk.Listbox(master, selectmode=tk.MULTIPLE, exportselection=0)
		self.boxSettings.grid(row=4)	
		
		for i in range(len(self.headers)):
			self.boxSettings.insert(tk.END, self.headers[i])
		
				
			
	def apply(self):
		selectedVariables = []
		for i in self.boxSettings.curselection():
			 selectedVariables.append(self.boxSettings.get(i))
			 
		if len(selectedVariables) < 3:
			tkMessageBox.showwarning("Instructions", "You must select at least three variables")
			self.result = False
			return
			 
		self.result = [self.normalized.get(), selectedVariables, self.name.get()]

# dialog box used to show PCA results		
class PCAShowDialog(Dialog):
	def __init__(self, parent, pObj):
		self.pca = pObj
		Dialog.__init__(self, parent, "PCA Results")
		
	def body(self, master):
		headers = self.pca.get_data_headers()
		newHeaders = self.pca.get_headers()
		eVals = self.pca.get_eigenvalues()
		eVecs = self.pca.get_eigenvectors()
		print "Eigenvectors:"
		print eVecs
		tk.Label(master, text="E-Vec").grid(row=0,column=0)
		tk.Label(master, text="E-Val").grid(row=0,column=1)
		tk.Label(master, text="Cumulative").grid(row=0,column=2)
		
		evalTot = 0
		tempTot = 0
		#create the headers
		for i in range(len(headers)):	
			tk.Label(master, text=headers[i]).grid(row=0,column=3+i)
			evalTot += eVals[i]
		
		for i in range(len(headers)):
 			for j in range(len(newHeaders)):
 				if j == 0:
 					tk.Label(master, text=newHeaders[i]).grid(row=1+i,column=0)
 				if j == 1:
 					
 					tk.Label(master, text=round(eVals[i],4)).grid(row=1+i,column=1)
 				if j ==	2:
 					value = round((eVals[i]+tempTot)/evalTot,4)
 					tk.Label(master, text=value).grid(row=1+i,column=2)
 					tempTot += eVals[i]
 					
 		for i in range(len(headers)):
 			for j in range(len(newHeaders)):			
 				value = round(eVecs[i,j],4)	
 				tk.Label(master, text=value).grid(row=1+i,column=3+j)
 						
		
		
				
			
	def apply(self):
		pass

# dialog box to select cluster features		
class ClusterSelect(Dialog):
	def __init__(self, parent, headers):
		
		self.numClusters = tk.IntVar(parent, value=0)
		self.notSmooth = tk.IntVar(parent, value=0)
		
		self.boxSettings = None
		Dialog.__init__(self, parent, "Clustering Analysis", headers=headers)
		
	def body(self, master):
			
		tk.Label(master, text=" Choose Variables\n").grid(row=0)
		tk.Label(master, text="How Many Clusters").grid(row=1)
		tk.Entry(master, textvariable=self.numClusters).grid(row=2)
		tk.Checkbutton(master, text="Use Non-Smooth Coloring", variable=self.notSmooth).grid(row=3)
	
	
		tk.Label(master, text="\n").grid(row=4)
		self.boxSettings = tk.Listbox(master, selectmode=tk.MULTIPLE, exportselection=0)
		self.boxSettings.grid(row=5)	
		
		for i in range(len(self.headers)):
			self.boxSettings.insert(tk.END, self.headers[i])
		
				
			
	def apply(self):
		selectedVariables = []
		for i in self.boxSettings.curselection():
			 selectedVariables.append(self.boxSettings.get(i))
		print len(selectedVariables)	 
		if len(selectedVariables) < 2:
			tkMessageBox.showwarning("Instructions", "You must select at least two variables")
			self.result = False
			return
			 
		self.result = [selectedVariables, self.numClusters.get(), self.notSmooth.get()]
			


			 
											
		
		
# run the app
if __name__ == "__main__":
	
	dapp = DisplayApp(1200, 675)

	dapp.buildAxes()
	dapp.updateAxes()
	dapp.main()
	

