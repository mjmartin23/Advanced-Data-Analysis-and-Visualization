# Authors: Matt Martin and Adam Carlson
# Date: 05/01/16
# testVideo: This program starts capturing video from the webcam. It identifies where your
	# hands are based on the green and red strap devices we provided.
	

import numpy as np
import cv2
import scipy.cluster.vq as vq
import math

# models the video class
class Video:
	
	# initializes the video
	def __init__(self, show=False):
		self.capture = cv2.VideoCapture(0)
		
		# setting the resolution
		self.capture.set(3,640)
		self.capture.set(4,480)
		
		# to show debugging windows
		self.show = show
		
		# number of frames run
		self.frames = 0
	
		# focal length of webcam (for physics calculations)
		self.focalLength = 1
	
	# runs one frame and does one round of calculations
	def run(self):

		if not self.capture.isOpened():
			return -1
		np.set_printoptions(threshold=np.nan)

		ret, frame = self.capture.read()

		# number of green and red pixels
		numG = 1
		numR = 1
		
		# sum of x and y coordinates of the green and red pixels
		# used to calculate average x and y positions for the red and green pixels
		totXG = 0
		totYG = 0
		totXR = 0
		totYR = 0
		
		# Convert BGR to RGB
		rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		newrgb = np.array( np.zeros( (rgb.shape[0],rgb.shape[1],3) ) )
		
		# loops over the frame's pixels, skips every 100 pixels for efficiency
		for i in range( 0, rgb.shape[0], rgb.shape[0]/100 ):
			for j in range( 0, rgb.shape[1], rgb.shape[1]/100 ):
				
				# the rgb tuple for a given pixel
				temp = rgb[i,j]
				
				if temp[0]+temp[1]+temp[2] == 0:
					continue
				tempr = float(temp[0])
				tempg = float(temp[1])
				tempb = float(temp[2])
				
				# calculates chromaticity	
				rValue = tempr / (tempr+tempg+tempb)
				gValue = tempg / ( tempr+tempg+tempb )
				bValue = tempb / ( tempr+tempg+tempb )
				
				# checks if pixel is very green
				if gValue > 2.0*rValue and gValue > 2.0*bValue and (tempr + tempg + tempb > 50):
				 	
 					numG += 1
 					newrgb[i,j,:] = np.array([0,255,0])
 					totXG += j
 					totYG += i
 				
 				# checks if pixel is very red
				elif rValue > 2.3*gValue and rValue > 2.3*bValue and (tempr + tempg + tempb > 75):
			
 					numR += 1
 					newrgb[i,j,:] = np.array([255,100,100])
 					totXR += j
 					totYR += i
 				
 				# if neither green nor black pixel turned to black	
 				else:
 					newrgb[i,j,:] = np.array([0,0,0])
 		
 		# reduces noise from background red colors
 		if numR < 15:
 			numR = 0.0
 		
 		# recalculates total green and red pixels because many were skipped over for efficiency	
 		totG = (numG * rgb.shape[0]/100 * rgb.shape[1]/100)
 		totR = (numR * rgb.shape[0]/100 * rgb.shape[1]/100)
 	
 		
 		# calculates the magnification of the hand-detecting images due to the webcam's vision
 		# use physics optics to calculate object distance from webcam 
 		mG = math.sqrt(totG)/200.0
 		mR = math.sqrt(totR)/200.0
 		distanceG = (self.focalLength*200.0*mG)/(200.0*mG - self.focalLength)
		distanceR = (self.focalLength*200.0*mR)/(200.0*mR - self.focalLength) 		
 		
 		# in order to avoid division by 0 in next calculation
 		if numR == 0:
 			numR = 1
 			
		# calculates average x and y positions for very green and red pixels		
		avgxG = totXG/numG
		avgyG = totYG/numG
		avgxR = totXR/numR
		avgyR = totYR/numR
		
		# determines the percentage of pixels that are very green or red
		percentG = float(numG)/float(rgb.shape[0]*rgb.shape[1])*100.0	
		percentR = float(numR)/float(rgb.shape[0]*rgb.shape[1])*100.0	
		
		# creates a circle at the average green and red positions
		cv2.circle(frame,(int(avgxG),int(avgyG)),3,(255,0,0),-1)
		cv2.circle(frame,(int(avgxR),int(avgyR)),3,(0,0,255),-1)


		# if hit "q" while focus on program window, terminates program
		k = cv2.waitKey(5)
		if k == 27 or k == 81:
			return -1
	
		# if was able to read in video information
		if ret==True:
			# displays various debugging windows
			if self.show:
				#cv2.imshow('mask',mask)
				cv2.imshow('item tracking',frame)
				#cv2.imshow('hand',drawing)
				cv2.imshow('chromaticity',newrgb)
				#print ''
			if cv2.waitKey(1) & 0xFF == ord('q'):
				return -1
				
		# if escape not clicked, increment frames field		
		else:
			return -1
		self.frames += 1
		
		return distanceG,distanceR,(avgxG,avgyG),(avgxR,avgxR)
	
	
	# Release everything if job is finished
	def end(self):
		self.capture.release()
		cv2.destroyAllWindows()

# tests color detection by the webcam
def main():
	v = Video(True)
	while v.capture.isOpened():
		ret = v.run()
		if ret == -1:
			break
		perc = ret[0]
		x = ret[2][0]
		y = ret[2][0]
	v.end()

if __name__ == '__main__':
	main()