#
# Author: Adam Carlson
# Date: 04/01/16
# pcaData: subclass of Data which is specifically designed to handle PCA analysis

import data

# subclass of Data which is specifically designed to handle PCA analysis
class PCAData(data.Data):
	
	# initializes all needed fields in order to continue Data object functionality	
	def __init__(self, projected_data, eigenvalues, eigenvectors, data_means, data_headers):
		data.Data.__init__(self)
		self.eigenvalues = eigenvalues
		self.eigenvectors = eigenvectors
		self.data_means = data_means
		self.original_headers = data_headers
		
		
		
		for i in range(len(data_headers)):
			self.raw_headers.append("PCA%02d"%(i))
			self.numeric_headers.append("PCA%02d"%(i))
			self.raw_types.append('numeric')
			self.header2raw[self.raw_headers[i]] = i
			self.header2matrix[self.raw_headers[i]] = i
			
		self.raw_data = projected_data.tolist()
		
		self.matrix_data = projected_data
		
		
	# getter methods
		
	def get_eigenvalues(self):
		return self.eigenvalues
		
	def get_eigenvectors(self):
		return self.eigenvectors
		
	def get_data_means(self):
		return self.data_means
		
	def get_data_headers(self):
		return self.original_headers				