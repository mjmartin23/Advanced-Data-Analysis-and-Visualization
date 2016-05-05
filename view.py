# Author: Adam Carlson
# Date: 02/26/16
# view.py: handles how the data and axes should be viewed

import numpy as np
import math

# models the view of the data
class View:
	
	# initializes the view object
	def __init__(self):
	
		self.vrp = np.matrix([.5,.5,1]) # stores the vrp coordinates
		self.vpn = np.matrix([0,0,-1]) # stores the vpn vector
		self.vup = np.matrix([0,1,0]) # stores the vup vector
		self.u = np.matrix([-1,0,0]) # stores the u vector
		self.extent = [1,1,1] # stores the visual extent
		self.screen = [400,400] # stores the size of the screen
		self.offset= [20,20] # stores the offset
	
	# builds the matrix which transforms data to the viewing area
	def build(self):
		vtm = np.identity( 4, float )
		t1 = np.matrix( [[1, 0, 0, -self.vrp[0, 0]],
					[0, 1, 0, -self.vrp[0, 1]],
					[0, 0, 1, -self.vrp[0, 2]],
					[0, 0, 0, 1] ] )
		vtm = t1 * vtm			  
		tu = np.cross(self.vup, self.vpn)
		tvup = np.cross(self.vpn, tu)
		tvpn = self.vpn
		self.vpn = self.normalize(tvpn)
		self.vup = self.normalize(tvup)
		self.u = self.normalize(tu)
		
		r1 = np.matrix( [[ tu[0, 0], tu[0, 1], tu[0, 2], 0.0 ],
					[ tvup[0, 0], tvup[0, 1], tvup[0, 2], 0.0 ],
					[ tvpn[0, 0], tvpn[0, 1], tvpn[0, 2], 0.0 ],
					[ 0.0, 0.0, 0.0, 1.0 ] ] )
		vtm = r1 * vtm
		
					
		t1 = np.matrix( [[ 1.0, 0.0, 0.0, .5*self.extent[0] ],
					[  0.0, 1.0, 0.0, .5*self.extent[1] ],
					[  0.0, 0.0, 1.0, 0.0 ],
					[ 0.0, 0.0, 0.0, 1.0 ] ] )
		vtm = t1*vtm			
					
		s1 = np.matrix( [[ -self.screen[0] / self.extent[0], 0.0, 0.0, 0.0 ],
					[  0.0, -self.screen[1] / self.extent[1], 0.0, 0.0 ],
					[  0.0, 0.0, 1.0 / self.extent[2], 0.0 ],
					[ 0.0, 0.0, 0.0, 1.0 ] ] )
					
		vtm = s1*vtm			 
					
		t2 = np.matrix( [[ 1.0, 0.0, 0.0, self.screen[0] + self.offset[0] ],
					[  0.0, 1.0, 0.0, self.screen[1] + self.offset[1] ],
					[  0.0, 0.0, 1.0, 0.0 ],
					[ 0.0, 0.0, 0.0, 1.0 ] ] ) 
		vtm = t2*vtm
		return vtm															
	
	# returns the normalized input vector	
	def normalize(self,vector):
		v = vector.tolist()[0]
		vnorm = []
		length = math.sqrt( v[0]*v[0] + v[1]*v[1] + v[2]*v[2] )
		vnorm.append( v[0] / length )
		vnorm.append( v[1] / length )
		vnorm.append( v[2] / length )
		return np.matrix(vnorm)
	
	# updates the viewing vectors after a given rotation
	def rotateVRC(self, vupAngle, uAngle):
		t1 = np.matrix( [[ 1.0, 0.0, 0.0, -1*(self.vrp[0,0]+self.vpn[0,0]*self.extent[2]*.5) ],
					[  0.0, 1.0, 0.0, -1*(self.vrp[0,1]+self.vpn[0,1]*self.extent[2]*.5) ],
					[  0.0, 0.0, 1.0, -1*(self.vrp[0,2]+self.vpn[0,2]*self.extent[2]*.5) ],
					[ 0.0, 0.0, 0.0, 1.0 ] ] )
					
		Rxyz = np.matrix( [[ self.u[0, 0], self.u[0, 1], self.u[0, 2], 0.0 ],
					[ self.vup[0, 0], self.vup[0, 1], self.vup[0, 2], 0.0 ],
					[ self.vpn[0, 0], self.vpn[0, 1], self.vpn[0, 2], 0.0 ],
					[ 0.0, 0.0, 0.0, 1.0 ] ] )
					
		r1 = np.matrix( [[ math.cos(vupAngle), 0.0, math.sin(vupAngle), 0.0 ],
					[ 0.0, 1.0, 0.0, 0.0 ],
					[ -1*math.sin(vupAngle), 0.0, math.cos(vupAngle), 0.0 ],
					[ 0.0, 0.0, 0.0, 1.0 ] ] )							
		
		r2 = np.matrix( [[1.0, 0.0, 0.0, 0.0 ],
					[ 0.0, math.cos(uAngle), -1*math.sin(uAngle), 0.0 ],
					[0.0, math.sin(uAngle), math.cos(uAngle), 0.0 ],
					[ 0.0, 0.0, 0.0, 1.0 ] ] )
					
		t2 = np.matrix( [[ 1.0, 0.0, 0.0, self.vrp[0,0]+self.vpn[0,0]*self.extent[2]*.5 ],
					[  0.0, 1.0, 0.0, self.vrp[0,1]+self.vpn[0,1]*self.extent[2]*.5 ],
					[  0.0, 0.0, 1.0, self.vrp[0,2]+self.vpn[0,2]*self.extent[2]*.5],
					[ 0.0, 0.0, 0.0, 1.0 ] ] )
					
		tvrc = np.matrix( [[self.vrp[0,0], self.vrp[0,1], self.vrp[0,2], 1.0 ],
					[  self.u[0,0], self.u[0,1], self.u[0,2], 0.0 ],
					[  self.vup[0,0], self.vup[0,1], self.vup[0,2], 0.0 ],
					[ self.vpn[0,0], self.vpn[0,1], self.vpn[0,2], 0.0 ] ] )
					
		tvrc = (t2*Rxyz.T*r2*r1*Rxyz*t1*tvrc.T).T
		
		
		self.vrp = np.matrix(tvrc.tolist()[0][0:3]) 
		self.u = self.normalize( np.matrix( tvrc.tolist()[1][0:3] ) )
		self.vup = self.normalize( np.matrix(tvrc.tolist()[2][0:3]) )
		self.vpn = self.normalize( np.matrix(tvrc.tolist()[3][0:3]) )
	
	# resets the viewing vectors	
	def reset(self):
		self.extent = [1,1,1]
		self.screen = [400,400]
		self.offset = [20,20]
		self.vrp = np.matrix([.5,.5,1])
		self.vpn = np.matrix([0,0,-1])
		self.vup = np.matrix([0,1,0])
		self.u = np.matrix([-1,0,0])
		
	def miniReset(self):
		self.vrp = np.matrix([.5,.5,1])
		self.vpn = np.matrix([0,0,-1])
		self.vup = np.matrix([0,1,0])
		self.u = np.matrix([-1,0,0])			
	
																
	# creates a clone of the view object	
	def clone(self):
		v2 = View()
		v2.vrp = self.vrp.copy()
		v2.vpn = self.vpn.copy()
		v2.vup = self.vup.copy()
		v2.u = self.u.copy()
		v2.extent = self.extent[:]
		v2.screen = self.screen[:]
		v2.offset = self.offset[:]
		return v2	
		
# some test code			
def main():
	v = View()
	v.build()
	v.rotateVRC(30,60)
	print v.normalize(np.matrix([1,2,3]))
	
if __name__ == "__main__":	
	main()			