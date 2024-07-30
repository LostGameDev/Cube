from pygame.locals import *
import pygame.draw
import pygame.time
from math import sin, cos
import json

ORIGINX = 0
ORIGINY = 0
cube_coords_dict = {}

def get_object_names():
	objectnameDict = []
	f = open('./objects.json')
	data = json.load(f)
	for i in data:
		objectnameDict.append(i)
	f.close()
	return objectnameDict

def load_cube(name):
	objectDict = {}
	f = open('./objects.json')
	data = json.load(f)
	for i in data[name]:
		objectDict[f"{name}X"] = i["X"]
		objectDict[f"{name}Y"] = i["Y"]
		objectDict[f"{name}Scale"] = i["Scale"]
		objectDict[f"{name}Red"] = i["Red"]
		objectDict[f"{name}Green"] = i["Green"]
		objectDict[f"{name}Blue"] = i["Blue"]
	
	f.close()
	return objectDict

def draw_3dline(surface, color, offsetX, offsetY, a, b):
	"""Convert 3D coordinates to 2D and draw line."""
	ax, ay = a[0]+(a[2]*0.3)+ORIGINX+offsetX, a[1]+(a[2]*0.3)+ORIGINY-offsetY
	bx, by = b[0]+(b[2]*0.3)+ORIGINX+offsetX, b[1]+(b[2]*0.3)+ORIGINY-offsetY
	pygame.draw.line(surface, color, (ax, ay), (bx, by))

def create_cube(Scale=50):
	cube = [(-Scale,Scale,Scale),  (Scale,Scale,Scale),  (Scale,-Scale,Scale),  (-Scale,-Scale,Scale),
			(-Scale,Scale,-Scale), (Scale,Scale,-Scale), (Scale,-Scale,-Scale), (-Scale,-Scale,-Scale)]
	return cube
def draw_cube(surface, color, offsetX, offsetY, cube):
	"""Draw 3D cube."""
	a, b, c, d, e, f, g, h = cube
	draw_3dline(surface, color, offsetX, offsetY, a, b)
	draw_3dline(surface, color, offsetX, offsetY, b, c)
	draw_3dline(surface, color, offsetX, offsetY, c, d)
	draw_3dline(surface, color, offsetX, offsetY, d, a)
	
	draw_3dline(surface, color, offsetX, offsetY, e, f)
	draw_3dline(surface, color, offsetX, offsetY, f, g)
	draw_3dline(surface, color, offsetX, offsetY, g, h)
	draw_3dline(surface, color, offsetX, offsetY, h, e)
	
	draw_3dline(surface, color, offsetX, offsetY, a, e)
	draw_3dline(surface, color, offsetX, offsetY, b, f)
	draw_3dline(surface, color, offsetX, offsetY, c, g)
	draw_3dline(surface, color, offsetX, offsetY, d, h)

def rotate_3dpoint(p, angle, axis):
	"""Rotate a 3D point around given axis."""
	ret = [0, 0, 0]
	cosang = cos(angle)
	sinang = sin(angle)
	ret[0] += (cosang+(1-cosang)*axis[0]*axis[0])*p[0]
	ret[0] += ((1-cosang)*axis[0]*axis[1]-axis[2]*sinang)*p[1]
	ret[0] += ((1-cosang)*axis[0]*axis[2]+axis[1]*sinang)*p[2]
	ret[1] += ((1-cosang)*axis[0]*axis[1]+axis[2]*sinang)*p[0]
	ret[1] += (cosang+(1-cosang)*axis[1]*axis[1])*p[1]
	ret[1] += ((1-cosang)*axis[1]*axis[2]-axis[0]*sinang)*p[2]
	ret[2] += ((1-cosang)*axis[0]*axis[2]-axis[1]*sinang)*p[0]
	ret[2] += ((1-cosang)*axis[1]*axis[2]+axis[0]*sinang)*p[1]
	ret[2] += (cosang+(1-cosang)*axis[2]*axis[2])*p[2]
	return ret

def rotate_object(screen, obj, angle, axis):
	"""Rotate an object around given axis."""
	screen.fill(Color("black"))
	for i in range(len(obj)):
		obj[i] = rotate_3dpoint(obj[i], angle, axis)


def translate_object(screen, cube_coords, newcoords=(0,0)):
	"""Move an object to a specific coordinate"""
	screen.fill(Color("black"))
	cube_coords = newcoords
	return cube_coords
	

def main():
	global ORIGINX, ORIGINY
	pygame.init()
	screen = pygame.display.set_mode((640,480), pygame.RESIZABLE)
	# Move origin to center of screen
	ORIGINX = screen.get_width()/2
	ORIGINY = screen.get_height()/2

	objects_loaded = False
	loaded_objects_list = []
	cube_points_dict = {}

	while True:
		for i in get_object_names():
			if objects_loaded == False:
				cubedict = load_cube(i)
				cube = create_cube(cubedict[f"{i}Scale"])
				cube_points_dict[i] = cube
				draw_cube(screen, (cubedict[f"{i}Red"], cubedict[f"{i}Green"], cubedict[f"{i}Blue"]), cubedict[f"{i}X"], cubedict[f"{i}Y"], cube)
				CubeCoords = (cubedict[f"{i}X"], cubedict[f"{i}Y"])
				cube_coords_dict[i] = CubeCoords
				loaded_objects_list.append(i)
				if loaded_objects_list == get_object_names():
					objects_loaded = True
			if objects_loaded == True:
				cubedict = load_cube(i)
				cube = cube_points_dict[i]
				CubeCoords = cube_coords_dict[i]
				draw_cube(screen, (cubedict[f"{i}Red"], cubedict[f"{i}Green"], cubedict[f"{i}Blue"]), cubedict[f"{i}X"], cubedict[f"{i}Y"], cube)
		event = pygame.event.poll()
		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			break
		if event.type == pygame.VIDEORESIZE:
			ORIGINX = screen.get_width()/2
			ORIGINY = screen.get_height()/2
		if event.type == KEYDOWN and event.key == K_r:
			screen.fill(0)
			cube_points_dict.clear()
			loaded_objects_list.clear()
			objects_loaded = False
		pygame.display.flip()
		pygame.time.delay(25)
		if objects_loaded == True:
			for i in loaded_objects_list:
				translate_object(screen, cube_coords_dict[i], (10, 10))
				#rotate_object(screen, cube_points_dict[i], 0.1, (0,1,0))
				#rotate_object(screen, cube_points_dict[i], 0.01, (0,0,1))
				#rotate_object(screen, cube_points_dict[i], 0.01, (1,0,0))

if __name__ == "__main__":
	main()