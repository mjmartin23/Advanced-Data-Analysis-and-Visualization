# Author: Adam Carlson
# Date: 02/20/16
# FileName: data.py - reads in and handles data from a csv file

import numpy as np
import csv


# models a csv data handler
class Data:
	
	# initializes the class
	def __init__(self, filename = None):
		
		self.raw_headers = [] #holds all of the raw headers
		
		self.raw_types = [] #holds all of the raw types
		
		self.raw_data =[] #holds all the raw data
		
		self.header2raw = {} #dictionary which maps raw headers to column indices
		
		self.numeric_headers = [] #holds all numeric headers
		
		self.matrix_data = np.matrix([]) # matrix of numeric data
		
		self.header2matrix = {} # dictionary mapping numeric headers to column indices
		
		#if filename given, read it in
		if filename is not None:
			self.read( filename )
	
	# reads in the file and fills all relavent class fields
	def read(self, filename):
		fp = file(filename, 'rU')
		cread = csv.reader(fp)
		self.raw_headers = cread.next() #fill in raw headers field
		for i in range(len(self.raw_headers)):
			self.raw_headers[i] = self.raw_headers[i].strip()
		self.raw_types = cread.next() #fill in raw types field
		for i in range(len(self.raw_types)):
			self.raw_types[i] = self.raw_types[i].strip()
		#loop through and fill in each row of raw data
		for row in cread:
			self.raw_data.append( row )
			
		#loop through headers and fill in each index of raw dictionary	
		for i in range( len(self.raw_headers) ):
			self.header2raw[ self.raw_headers[i] ] = i
		
		numeric_data = []
		
		#loop through raw data and fill in numeric fields
		
		
		
		
		for i in range( len(self.raw_data) ):
			
			numeric_row = []
			
			
			for j in range( len(self.raw_headers) ):
				
				colNum = self.header2raw[ self.raw_headers[j] ]	
				
				if self.raw_types[j] == "numeric":
						
					if i == 0:
						
						self.numeric_headers.append( self.raw_headers[j] )
					numeric_row.append( float( self.raw_data[i][colNum] ) )
			numeric_data.append( numeric_row )
				
		
		
		
		
		
		
		
		self.matrix_data = np.matrix( numeric_data )	
		counter = 0;
		
		
		
		
		for i in range( len(self.raw_headers) ):
			if self.raw_types[i] == "numeric":
				self.header2matrix[ self.raw_headers[i] ] = counter
				counter+=1
	
	# writes the given headers to the given filename			
	def write(self, filename, headers = None):
		file = open(filename, "w")
		if headers != None:
			for header in headers:
				file.write(header+ " ")
		file.close()
	
	def writeData(self, filename, dataObj = None):
		file = open(filename, "w")
		if dataObj is not None:
			for header in dataObj.get_headers():
				file.write(header+ ",")
				
			file.write("\n")
			
			for type in dataObj.get_headers():
				file.write("numeric,")
				
			
			
			data = dataObj.get_data( dataObj.get_headers() ).tolist()
		
			for i in range( len( data ) ):  #rows
				file.write("\n")
				
				for j in range( len( data[0] ) ): # columns
					file.write(str(data[i][j])+ ",")
					
		file.close()	

			 			
	
	#adds a column to the dataset if you input the correct numer of rows
	def addData(self, dataList):
		if len(dataList) != (len(self.raw_data) + 2):
			print len(dataList)
			print len(self.raw_data) + 2
			print "You must input " + str((len(self.raw_data) + 2)) + " rows including headers and types"
			return
			
		self.raw_headers.append(dataList[0])
		self.raw_types.append(dataList[1])
		data_length = len(self.raw_data[0])
		for i in range(len(self.raw_data)):
			self.raw_data[i].append(dataList[2+i])
		self.header2raw[dataList[0]] = data_length
		if dataList[1] == "numeric":
			self.numeric_headers.append(dataList[0])
			data_length = self.matrix_data.shape[1]
			matrix = self.matrix_data.tolist()
			for i in range(len(matrix)):
				matrix[i].append(dataList[2+i])
			newMatrix = np.matrix(matrix)
			self.matrix_data = newMatrix	
			self.header2matrix[dataList[0]] = data_length
	
	# removes the last column from the dataset		
	def removeLast(self, classify = False):
		del self.raw_headers[-1]
		del self.numeric_headers[-1]
		del self.raw_types[-1]
		if classify == True:
			del self.header2raw["class"]
			del self.header2matrix["class"]
		else:
			del self.header2raw["Categories"]
			del self.header2matrix["Categories"]
		for i in range(len(self.raw_data)):
			del self.raw_data[i][-1]
		temp = 	self.matrix_data.tolist()
		for i in range(len(temp)):
			del temp[i][-1]
		self.matrix_data = np.matrix(temp)	
					
		
		 
			
	#returns raw headers			
	def get_raw_headers(self):
		return self.raw_headers
	
	#returns raw types
	def get_raw_types(self):
		return self.raw_types
	
	#returns number of raw columns
	def get_raw_num_columns(self):
		return len( self.raw_headers )
	
	#returns number of raw rows	
	def get_raw_num_rows(self):
		return len( self.raw_data ) 
	
	#returns a specified raw row
	def get_raw_row(self,row):
		return self.raw_data[ row ]
	
	#returns a raw data value given a row and header feature	
	def get_raw_value(self,row, feature):
		colNum = self.header2raw[feature]
		return self.raw_data[row][colNum]	
	
	#returns numeric headers	
	def get_headers(self):
		return self.numeric_headers	
	
	#returns number of numeric columns	
	def get_num_columns(self):
		return len( self.numeric_headers )
	
	#returns a row of the numeric data as a single list	
	def get_row( self,row ):
		return self.matrix_data[row].tolist()[0]
	
	#returns a value in the numeric data given a row and header feature	
	def get_value( self,row, header ):
		col = self.header2matrix[ header ]
		return self.matrix_data.item(row,col);
	
	#returns the numeric data of the input list of headers	
	def get_data(self, hList):
		
		temp = self.matrix_data.tolist()
		colList = [0]*len(hList)
		for i in range( len(hList) ):
			
			colList[i] = self.header2matrix[hList[i]]		
		
		tempList = []
		
		for i in range( len(temp) ):
			row = []
			for j in range(len(colList)):
				row.append( temp[i][colList[j]] )
				if j == len(colList) -1:
					tempList.append(row)
				
				
				
		return np.matrix(tempList)		

								
											
			
		return np.matrix(temp)							
	
	#returns a string representation of the data object
	def __str__(self):
		ret = "Headers: "
		for i in range(len(self.raw_headers)):
			ret += self.raw_headers[i]
			ret += " "
			if i == len(self.raw_headers) -1:
				ret += "\n"
				
		ret += "Types: "
		for i in range(len(self.raw_types)):
			ret += self.raw_types[i]
			ret += " "
			if i == len(self.raw_types) -1:
				ret += "\n"
				
		ret += "Data:\n"
		
		for i in range(len(self.raw_data)):
			for j in range(len(self.raw_headers)):			
				ret += str(self.get_raw_value(i, self.raw_headers[j]))
				ret += " "
				if j == len(self.raw_headers) -1:
					ret += "\n"

		return ret	

#tests the class' functionality		
def main():
 	d = Data( "real_estate.csv" )
# 	print d
# 	print d.get_raw_headers()
# 	print d.get_raw_types()
# 	print d.get_raw_num_columns()
# 	print d.get_raw_num_rows()
# 	print d.get_raw_row(1)
# 	print d.get_raw_value(1, "price")
# 	
# 	print d.get_headers()
# 	print d.get_num_columns()
# 	print d.get_row(0)
# 	print d.get_value(3,'latitude')
# 	print d.get_data( ['latitude','sq__ft'] )
# 	
# 	d2 = Data("testdata1.csv")
# 	print d2
# 	list = ['thing6','numeric',1,2,3,4,5,6,7,8,9,1,2,3,4,5]
# 	d2.addData(list)
# 	print d2
	d.write("output.txt", ["header1", "header2", "header3"])

if __name__ == "__main__":	
	main()	