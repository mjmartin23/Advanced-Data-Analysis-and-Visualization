# Template by Bruce Maxwell
# Spring 2015
# CS 251 Project 8
#
# Classifier class and child definitions

import sys
import data
import analysis as an
import numpy as np
import scipy.cluster.vq as vq

# main classifier class
class Classifier:

	def __init__(self, type):
		'''The parent Classifier class stores only a single field: the type of
		the classifier.	 A string makes the most sense.

		'''
		self._type = type

	def type(self, newtype = None):
		'''Set or get the type with this function'''
		if newtype != None:
			self._type = newtype
		return self._type
	
	# constructs a confusion matrix 
	def confusion_matrix( self, truecats, classcats ):
		'''Takes in two Nx1 matrices of zero-index numeric categories and
		computes the confusion matrix. The rows represent true
		categories, and the columns represent the classifier output.
		'''
		
		unique, mapping = np.unique( np.array(truecats.T), return_inverse=True)
		truecats = truecats.T.tolist()[0]
		classcats = classcats.T.tolist()[0]
		
		
		matrix = np.matrix(np.zeros((len(unique), len(unique))))

		for i in range(len(truecats)):
			matrix[classcats[i],mapping[i]] += 1
				

		return matrix
	
	# prints out a confusion matrix in an appealing manner
	def confusion_matrix_str( self, cmtx ):
		'''Takes in a confusion matrix and returns a string suitable for printing.'''
		
		s = "\nConfusion Matrix:\n"
		s += 'Actual->\t'
		
		for i in range( cmtx.shape[0] ):
			s += 'Category ' + str(i) + "\t"
			
		for i in range(cmtx.shape[0]):
			s += "\nCluster " + str(i) + "\t"
			for j in range( cmtx.shape[1] ):
				s += str(cmtx[i,j])
				s += "\t\t"
		

		return s

	def __str__(self):
		'''Converts a classifier object to a string.  Prints out the type.'''
		return str(self._type)


# stores the mean and standard deviation from each class, calculates probability that the 
	# new point belongs to each class, pick highest probability 
class NaiveBayes(Classifier):
	'''NaiveBayes implements a simple NaiveBayes classifier using a
	Gaussian distribution as the pdf.

	'''

	def __init__(self, dataObj=None, headers=[], categories=None):
		'''Takes in a Data object with N points, a set of F headers, and a
		matrix of categories, one category label for each data point.'''

		# call the parent init with the type
		Classifier.__init__(self, 'Naive Bayes Classifier')
		
		self.headers = headers
		self.numClasses = 0
		self.numFeatures = 0
		
		self.means = None
		self.vars = None
		self.scales = None
		
		
		if dataObj != None:
			self.build(dataObj, self.labels)
	
	# builds the naive bayes classifier, stores mean, std, and scale for each feature of a
		# given class

	def build( self, A, categories ):
		
		self.numFeatures = A.shape[1]
		self.labels = categories
	
		unique, mapping = np.unique( np.array(categories.T), return_inverse=True)
	
		self.numClasses = len(unique)
		self.means = np.zeros((self.numClasses, self.numFeatures))
		self.vars = np.zeros((self.numClasses, self.numFeatures))
		self.scales = np.zeros((self.numClasses, self.numFeatures))	 
		
		# create the matrices for the means, vars, and scales
		for i in range(self.numClasses):
			self.means[i, :] = np.mean( A[(mapping==i),:], axis=0 )
			self.vars[i, :] = np.var( A[(mapping==i),:], axis=0 )
			self.scales[i, :] = 1/(np.sqrt( 2*np.pi*self.vars[i,:] ) )

		return
	
	# classifies each point in a data set by comparing it to the previously stored data
	def classify( self, A, return_likelihoods=False ):
		'''Classify each row of A into one category. Return a matrix of
		category IDs in the range [0..C-1], and an array of class
		labels using the original label values. If return_likelihoods
		is True, it also returns the NxC likelihood matrix.

		'''

		# error check to see if A has the same number of columns as
		# the class means
		
		
		if A.shape[1] != self.means.shape[1]:
			print "error in matrix dimensions"
			return 
		
		# make a matrix that is N x C to store the probability of each
		# class for each data point
		# a matrix of zeros that is N (rows of A) x C (number of classes)
		P = np.matrix(np.zeros( (A.shape[0], self.numClasses) ))

		# calculate the probabilities by looping over the classes
		#  with numpy-fu you can do this in one line inside a for loop
		
		for i in range(self.numClasses):
			
			# fills in the probability of the point being in each of the classes
			# received help with numpy syntax
			P[:,i] = np.prod(np.multiply(self.scales[i,:], np.exp(-(np.square(A - self.means[i,:]))/(2*self.vars[i,:]))), axis=1)

		# calculate the most likely class for each data point
		cats = np.argmax(P, axis=1) # take the argmax of P along axis 1

		# use the class ID as a lookup to generate the original labels
		labels = self.labels[cats]

		if return_likelihoods:
			return cats, labels, P

		return cats, labels

	def __str__(self):
		'''Make a pretty string that prints out the classifier information.'''
		s = "\nNaive Bayes Classifier\n"
		for i in range(self.numClasses):
			s += 'Class %d --------------------\n' % (i)
			s += 'Mean	: ' + str(self.means[i,:]) + "\n"
			s += 'Var	: ' + str(self.vars[i,:]) + "\n"
			s += 'Scales: ' + str(self.scales[i,:]) + "\n"

		s += "\n"
		return s
		
	def write(self, filename):
		'''Writes the Bayes classifier to a file.'''
		# extension
		return

	def read(self, filename):
		'''Reads in the Bayes classifier from the file'''
		# extension
		return

# store matrix data from each class in a list from training data, take distance of each row
	# of each matrix from the new data point (exemplars), whichever matrix has minimum sum of 
	# exemplars classifies the new data point	
class KNN(Classifier):

	def __init__(self, dataObj=None, headers=[], categories=None, K=None):
		'''Take in a Data object with N points, a set of F headers, and a
		matrix of categories, with one category label for each data point.'''

		# call the parent init with the type
		Classifier.__init__(self, 'KNN Classifier')
		
		self.headers = headers
		self.numClasses = len(headers)
		self.numFeatures = 0
		self.categories = None
		
		self.exemplars = [] # simply a sum between the data point and another point within a class
		
		if dataObj is not None:
			self.data_obj = dataObj
			A = dataObj.get_data(headers)
			self.build(A,categories)
			
		# store the headers used for classification
		# number of classes and number of features
		# original class labels
		# unique data for the KNN classifier: list of exemplars (matrices)
		# if given data,
			# call the build function

	def build( self, A, categories, K = None ):
		'''Builds the classifier give the data points in A and the categories'''
		
			
		unique, mapping = np.unique(np.array(categories.T), return_inverse=True)
		self.numClasses = len(unique)
		self.numFeatures = A.shape[0]
		self.categories = categories

	 
		for i in range(self.numClasses):
			if K is None:
				self.exemplars.append(A[(mapping == i),:])
			else:
				codebook,codes = vq.kmeans(A[(mapping == i),:],K)
				self.exemplars.append(codebook)

		return
		
		# figure out how many categories there are and get the mapping (np.unique)
		# for each category i, build the set of exemplars
			# if K is None
				# append to exemplars a matrix with all of the rows of A where the category/mapping is i
			# else
				# run K-means on the rows of A where the category/mapping is i
				# append the codebook to the exemplars

		# store any other necessary information: # of classes, # of features, original labels

		
	# use knn classification
	def classify(self, A, K=3, return_distances=False):
		'''Classify each row of A into one category. Return a matrix of
		category IDs in the range [0..C-1], and an array of class
		labels using the original label values. If return_distances is
		True, it also returns the NxC distance matrix.

		The parameter K specifies how many neighbors to use in the
		distance computation. The default is three.'''

		# error check to see if A has the same number of columns as the class means
		

		# make a matrix that is N x C to store the distance to each class for each data point
		# a matrix of zeros that is N (rows of A) x C (number of classes)
		D =	 np.matrix(np.zeros((A.shape[0],self.numClasses))) 
		
		# for each class i
			# make a temporary matrix that is N x M where M is the number of examplars (rows in exemplars[i])
			# calculate the distance from each point in A to each point in exemplar matrix i (for loop)
			# sort the distances by row
			# sum the first K columns
			# this is the distance to the first class
			
		# got help with this loop functionality	
		for i in range(self.numClasses):
			temp = np.matrix(np.zeros((A.shape[0],self.exemplars[i].shape[0])))
			for j in range(A.shape[0]):
				for k in range(self.exemplars[i].shape[0]):
					# distance between point and each exemplar
					temp[j,k] = np.linalg.norm(A[j,:]-self.exemplars[i][k,:])
			
			# add up all distances calculated for the point and add them to the distance matrix
			temp = np.sort(temp,axis=1)
			D[:,i] = np.sum(temp[:,K],axis=1)
	

		# calculate the most likely class for each data point
		# take the argmin of D along axis 1
		cats = np.argmin(D,axis=1) 

		# use the class ID as a lookup to generate the original labels
		labels = self.categories[cats]

		if return_distances:
			return cats, labels, D

		return cats, labels

	def __str__(self):
		'''Make a pretty string that prints out the classifier information.'''
		s = "\nKNN Classifier\n"
		for i in range(self.numClasses):
			s += 'Class %d --------------------\n' % (i)
			s += 'Number of Exemplars: %d\n' % (self.exemplars[i].shape[0])
			s += 'Mean of Exemplars	 :' + str(np.mean(self.exemplars[i], axis=0)) + "\n"

		s += "\n"
		return s


	def write(self, filename):
		'''Writes the KNN classifier to a file.'''
		# extension
		return

	def read(self, filename):
		'''Reads in the KNN classifier from the file'''
		# extension
		return
	
