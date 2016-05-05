import cv2
import time 

 
def takePicture(frame, camera): 
	# Camera 0 is the integrated web cam 
	camera_port = 0
 
	#Number of frames to throw away while the camera adjusts to light levels
	ramp_frames = 30
 
	# Now we can initialize the camera capture object with the cv2.VideoCapture class.
	# All it needs is the index to a camera port.
	
 	
	# Captures a single image from the camera and returns it in PIL format
	def get_image():
	 # read is the easiest way to get a full image out of a VideoCapture object.
	 retval, im = camera.read()
	 return im
 
	# Ramp the camera - these frames will be discarded and are only used to allow v4l2
	# to adjust light levels, if necessary
	for i in xrange(ramp_frames):
	 temp = get_image()
	
	# Take the actual image we want to keep
	camera_capture = get_image()
	file = "Pictures/image" + str(frame) + ".png"
	
	# A nice feature of the imwrite method is that it will automatically choose the
	# correct format based on the file extension you provide. Convenient!
	cv2.imwrite(file, camera_capture)
 
	# You'll want to release the camera, otherwise you won't be able to create a new
	# capture object until your script exits
	#del(camera)
	
	
def main():
	numPhotos = 0
	camera = cv2.VideoCapture(0)
	#camera.set(3,100)
	#camera.set(4,100)
	start = time.time()
	for i in range(10):
		takePicture(i, camera)
	end = time.time()
	print end - start	
		
main()			


# threshold function

# http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_gui/py_video_display/py_video_display.html