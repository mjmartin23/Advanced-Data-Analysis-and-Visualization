# Author: Adam Carlson
# Date: 02/20/16
# FileName: analysis.py - handles the contents of a data object

import data as d
import numpy as np
import scipy.stats
import math
import pcaData
import random
import scipy.cluster.vq as vq
from bs4 import BeautifulSoup
import urllib


# returns a list of 2-element lists with the minimum and maximum values for each column
def data_range(headers, data):
	numeric = data.get_data(headers).tolist()

	ret = []
	min = None
	max = None
	for i in range( len(headers) ):
		for j in range( len(numeric) ):
			if j == 0:
				min = numeric[j][i]
				max = numeric[j][i]
			else:
				if numeric[j][i] < min:
					min = numeric[j][i]
				if numeric[j][i] > max:
					max = numeric[j][i]
		ret.append([min,max])
	return ret

# returns a list of the mean values for each specified column	
def mean( headers, data ):
	numeric = data.get_data(headers)
	
	return np.mean(numeric, axis=0).tolist()[0]

# returns a list of the standard deviation for each specified column	
def std( headers, data ):							
	numeric = data.get_data(headers)
	return np.std(numeric, axis=0).tolist()[0]

# returns a list of the median for each specified column
def median( headers, data ):
	numeric = data.get_data(headers)
	return np.median(numeric, axis=0).tolist()[0]

# returns a list of the sum for each specified column	
def sum( headers, data ):
	numeric = data.get_data(headers).T.tolist()
	sums = []
	for i in range( len(numeric) ):
		rowsum = 0
		for j in range( len(numeric[0]) ):
			rowsum += numeric[i][j]
			if j == len(numeric[0]) - 1:
				sums.append(rowsum) 
	return sums

# returns a matrix with each column normalized so its minimum value is mapped to zero
	# and its maximum value is mapped to 1	
def normalize_columns_separately( headers, data ):
	numeric = data.get_data(headers)
	ranges = data_range( headers, data)
	for i in range( numeric.shape[1] ):
		rangeTot = ranges[i][1]-ranges[i][0]
		for j in range( numeric.shape[0]  ):
			
			numeric[j,i] = (numeric[j,i] - ranges[i][0])/rangeTot
	return numeric

#returns a matrix with each entry normalized so that the minimum value
	#(of all the data in this set of columns) is mapped to zero and its maximum value is mapped to 1	
def normalize_columns_together( headers,data):	
	numeric = data.get_data(headers)
	ranges = data_range( headers, data)
	absMin = ranges[0][0]
	absMax = ranges[0][0]
	for i in range( len(ranges) ):
		for j in range( len(ranges[0]) ):
			if ranges[i][j] < absMin:
				absMin = ranges[i][j]
			elif ranges[i][j] > absMax:
				absMax = ranges[i][j]
			
	rangeTot = absMax-absMin
	for i in range( numeric.shape[1] ):
		
		for j in range( numeric.shape[0]  ):
			
			numeric[j,i] = (numeric[j,i] - absMin)/rangeTot
	return numeric

# returns information about a regression line for a certain data set with a given independent and dependent variable	
def linear_regression(dSet, ind, dep):
	data = d.Data(dSet)
	y = data.get_data( [ind] )
	A = data.get_data( dep ).tolist()
	for i in range( len(A) ):
		A[i].append(1)
	A = np.matrix(A)
	AAinv = np.linalg.inv( np.dot(A.T, A))
	x = np.linalg.lstsq( A, y )
	b = x[0]
	N = y.shape[0]
	C = len(b)
	df_e = N-C
	df_r = C-1
	error = y - np.dot(A, b)
	sse = np.dot(error.T, error) / df_e
	stderr = np.sqrt( np.diagonal( sse[0, 0] * AAinv ) )
	t = t = b.T / stderr
	p = 2*(1 - scipy.stats.t.cdf(abs(t), df_e))
	r2 = 1 - error.var() / y.var()
	return (b, sse, r2, t, p)

# takes in a data object and relevant headers and returns a pcaData object	
def pca(dataObj, headers, normalize = True):
	A = None
	if normalize:
		A = normalize_columns_separately(headers, dataObj)
		m = np.mean(A, axis=0 ).tolist()[0]
		
	else:
		A = dataObj.get_data(headers)
		m = mean(headers,dataObj)

	D = A-m
	result = np.linalg.svd(D, full_matrices=False)
	U = result[0]
	S = result[1]
	V = result[2]

	for i in range(len(S)):
		S[i] = S[i]*S[i]/(A.shape[0]-1)
	eigenvalues = S
	data = (V*D.T).T
	eigenvectors = V
	return pcaData.PCAData(data, eigenvalues, eigenvectors, m, headers)

# run a k-means cluster with the help of numpy	
def kmeans_numpy( d, headers, K, whiten = True):
	A = d.get_data(headers)
	W = vq.whiten(A)
	codebook, bookerror = vq.kmeans(W,K)
	codes, error = vq.vq(W, codebook)
	return [codebook,codes,error]

# run the same clustering method without heavy use of numpy	
def kmeans(d, headers, K, whiten=True, categories = ''):
	'''Takes in a Data object, a set of headers, and the number of clusters to create
	Computes and returns the codebook, codes and representation errors. 
	If given an Nx1 matrix of categories, it uses the category labels 
	to calculate the initial cluster means.
	'''
	
	A = d.get_data(headers)
	if whiten:
		W = vq.whiten(A)
	else:
		W = A
  
	codebook = kmeans_init(W,K,categories)

	codebook, codes, errors = kmeans_algorithm(W,codebook)
	
	return [codebook,codes, errors]			

# calculate initial means for kmeans clustering	
def kmeans_init(data, K, categories = ''):
	if categories == '':
		numRows = len(data.tolist())
		rowIndices = []
		points = []
		for i in range(K):
			index = random.randint(0,numRows-1)
			if index not in rowIndices: 
				rowIndices.append( index )
			else:
				success = False
				while( success == False ):
					index = random.randint(0,numRows-1)
					if index not in rowIndices:
						 rowIndices.append( index )
					success = True	 	
				
		for i in rowIndices:
			points.append( data.tolist()[i] )
		return np.matrix(points)
		
	else:
		data = data.tolist()
		finalList = []
		for i in range(K):
			finalList.append([])
		counter = 0
		
		for i in categories.T.tolist()[0]:
			
			finalList[int(i)].append(data[counter])

			counter+=1			
			
		
		allMeans = []	
		for i in finalList:
			matrix = np.matrix(i)
			means = np.mean(matrix, axis=0).tolist()[0]
			allMeans.append(means)
		return np.matrix(allMeans)

# classify which cluster each data point is closest to		
def kmeans_classify(data, means):
	data = data.tolist()
	means = means.tolist()
	fullReturn = []
	tempDist = []
	for i in range(len(data)):
		
		for k in range(len(means)): 
		
				
			sum = 0
				
			for j in range(len(data[0])):
			
		
			
				sum += ( (data[i][j]-means[k][j]) * (data[i][j]-means[k][j]) )
		
			
			if k == 0:
				tempDist = [0, math.sqrt(sum),]
			elif k>0 and math.sqrt(sum) < tempDist[1]:
				tempDist = [k, math.sqrt(sum)]	
				
				
		fullReturn.append(tempDist)
	
	fullReturn = np.matrix(fullReturn)
	idx = fullReturn[:,0]
	sums = fullReturn[:,1]
	return (idx,sums)

# main kmeans algorithm	
def kmeans_algorithm(A, means):
	# set up some useful constants
	MIN_CHANGE = 1e-7
	MAX_ITERATIONS = 100
	D = means.shape[1]
	K = means.shape[0]
	N = A.shape[0]

	# iterate no more than MAX_ITERATIONS
	for i in range(MAX_ITERATIONS):
		# calculate the codes
		codes, errors = kmeans_classify( A, means )

		# calculate the new means
		newmeans = np.zeros_like( means )
		counts = np.zeros( (K, 1) )
		for j in range(N):
			newmeans[codes[j,0],:] += A[j,:]
			counts[codes[j,0],0] += 1.0

		# finish calculating the means, taking into account possible zero counts
		for j in range(K):
			if counts[j,0] > 0.0:
				newmeans[j,:] /= counts[j, 0]
			else:
				newmeans[j,:] = A[random.randint(0,A.shape[0]),:]

		# test if the change is small enough
		diff = np.sum(np.square(means - newmeans))
		means = newmeans
		if diff < MIN_CHANGE:
			break

	# call classify with the final means
	codes, errors = kmeans_classify( A, means )

	# return the means, codes, and errors
	return (means, codes, errors)
	
			
					
				
def writeNewCSV(filename, test):
		
	numRows = 200
	
	if not test:
		numRows = 1000

	file = open(filename, "w")
	
	file.write("Dog1,Dog2,Dog3,class")
		
	file.write("\n")
	
	file.write("numeric,numeric,numeric,numeric")
	
	means = [ 3.0, 33.0, 67.0 ]
	stds = [ 0.2, 3.0, 7.0 ]
	

	for i in range( numRows ):  #rows
		file.write("\n")
		index = random.randint(0,2)
		for j in range( 4 ): # columns
			
			if j == 3:
				file.write( str(index) )
			else:
				if test:
					if random.random() < .25:
						file.write(str( random.gauss( means[index-1], stds[index-1] ) )+ ",")
					else:
						file.write(str( random.gauss( means[index], stds[index] ) )+ ",")	
				else:
					file.write(str( random.gauss( means[index], stds[index] ) )+ ",")		
				
				
	file.close()
	
def csvCollection():
	writeNewCSV("DogTrain.csv", False)
	writeNewCSV("DogTest.csv", True)
	
	data = d.Data( "DogTrain.csv" )
	pcaObj = pca(data, ["Dog1","Dog2","Dog3"] )
	classes = data.get_data(["class"])
	newList = ["class", "numeric"]
	cats = classes.T.tolist()[0]
	for cat in cats:
		newList.append(cat)
	pcaObj.addData( newList )	
	data.writeData("dog_train_pca.csv", pcaObj)
	
	data = d.Data( "DogTest.csv" )
	pcaObj = pca(data, ["Dog1","Dog2","Dog3"] )
	classes = data.get_data(["class"])
	newList = ["class", "numeric"]
	cats = classes.T.tolist()[0]
	for cat in cats:
		newList.append(cat)
	pcaObj.addData( newList )	
	data.writeData("dog_test_pca.csv", pcaObj)						
							


		
	
# tests the functionality of the methods
def main():
	# data = d.Data( "real_estate.csv" )
#	print data_range(['price','beds'],data)
#	print mean( ['sq__ft'],data )
#	print std( ['beds', 'baths'],data )
#	print median( ['beds', 'baths'],data )
#	print sum( ['beds', 'baths'],data )
#	print normalize_columns_separately( ['price','sq__ft'],data )
#	print normalize_columns_together( ['price','sq__ft'],data )
	#print linear_regression("data-clean.csv", "Y", ["X0","X1"])
	#print "\n"
	#print linear_regression("data-good.csv", "Y", ["X0","X1"])
	#print "\n"
	#print linear_regression("data-noisy.csv", "Y", ["X0","X1"])
	#webCrawl("weather")
	#betterCrawl()
	#data = d.Data( "real_estate_train.csv" )
	#pcaObj = pca(data, data.get_headers() )
	#data.writeData("real_estate_train_pca.csv", pcaObj)
	csvCollection()
	
			
if __name__ == "__main__":	
	main()		