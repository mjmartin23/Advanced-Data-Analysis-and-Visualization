import data
import sys
import numpy as np
import classifier as c

# prints out a confusion matrix for the training and testing data, the testing set with
	# categories is then written out to classified.csv to be used for the GUI
def writeClassifier(argv):
	if len(argv) < 4:
		print 'usage: <Train CSV file>, <Test CSV file>, <classifier>, <optional train categories>, <optional test categories>'
		return
		
	dtrain = data.Data(argv[1])
	dtest = data.Data(argv[2])		
		
	if len(argv) > 4:
		traincatdata = data.Data(argv[4])
		traincats = traincatdata.get_data( [traincatdata.get_headers()[0]] )
		testcatdata = data.Data(argv[5])
		testcats = testcatdata.get_data( [testcatdata.get_headers()[0]] )
		A = dtrain.get_data( dtrain.get_headers() )
		B = dtest.get_data( dtest.get_headers() )
		
	else:
		# assume the categories are the last column
		traincats = dtrain.get_data( [dtrain.get_headers()[-1]] )
		testcats = dtest.get_data( [dtest.get_headers()[-1]] )
		A = dtrain.get_data( dtrain.get_headers()[:-1] )
		B = dtest.get_data( dtest.get_headers()[:-1] )
		
	
	# create a new classifier
	if argv[3] == "naive":
		nbc = c.NaiveBayes()
		nbc.build( A, traincats )
	else:
		nbc = c.KNN()
		nbc.build( A, traincats, 6 )	

	# build the classifier using the training data

	
	# use the classifier on the training data
	ctraincats, ctrainlabels = nbc.classify( A )
	ctestcats, ctestlabels = nbc.classify( B )
	
	
	
	trainMatrx = nbc.confusion_matrix( traincats, ctraincats  )
	print nbc.confusion_matrix_str( trainMatrx)
	
	testMatrx = nbc.confusion_matrix( testcats, ctestcats  )
	print nbc.confusion_matrix_str( testMatrx )
	
	newList = ["class", "numeric"]
	cats = ctestcats.T.tolist()[0]
	for cat in cats:
		newList.append(cat)
	
	if len(argv) > 4:
		dtest.addData( newList )
		
	else:
		dtest.removeLast(classify=True)
		dtest.addData( newList )	
	
	dtest.writeData( "classified.csv", dtest )
	
writeClassifier(sys.argv)				