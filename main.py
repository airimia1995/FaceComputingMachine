import json
from utils_google import get_vision_api
from base64 import b64encode
from PIL import Image
from PIL import ImageDraw
from argparse import ArgumentParser
#from utils_image import (read_image, read_image_base64, save_image, draw_face, draw_box, draw_text)

#inputfile  = "input.jpeg"
outputfile = "output.jpeg"

def main(api_key,inputfile):

	vision = get_vision_api(api_key)
	
	body = make_request(inputfile)
	response = vision.images().annotate(body=body).execute()
	#faces = response['responses'][0]['faceAnnotations']
	print response
	show_results(inputfile, response, outputfile)

def read_image_base64(filename):
	with open(filename, 'rb') as f:
		return b64encode(f.read())
	
def make_request(inputfile):
	""" Create a request batch (one file at a time) """
	return {
		"requests":[
			{
				"image":{
	    				"content": read_image_base64(inputfile)
	    			},
				"features": [
					{
						"type":"LABEL_DETECTION",
      						"maxResults": 10
      					},
      					{
      						"type":"TEXT_DETECTION",
      						"maxResults": 10
      					},
      					{
      						"type":"FACE_DETECTION",
      						"maxResults": 20
      					}
      				]
			}
		]
	}

def show_results(inputfile, data, outputfile):

	#read original file
	im = Image.open(inputfile)
	draw = ImageDraw.Draw(im)
	#draw face, boxes and text for each response

	#for face in data[0]['faceAnnotations']:
	#    box = [(v['x'], v['y']) for v in face['fdBoundingPoly']['vertices']]
	#    draw.line(box + [box[0]], width=2, fill='#00ff00')

	for r in data['responses']:
		if 'faceAnnotations' in r:
			draw_face(im, draw, r['faceAnnotations'])

	del draw
	im.save(outputfile)

def draw_face(im, draw, annotations):
	for a in annotations:
		#tl ,br  = draw_box(im, draw, a['boundingPoly']['vertices'])
		draw_box(im, draw, a['boundingPoly']['vertices'])
		#tl_,br_ = draw_box(im, draw, a['fdBoundingPoly']['vertices'])
		draw_box(im, draw, a['fdBoundingPoly']['vertices'])
		#draw_angle(im, draw, a['panAngle'], a['tiltAngle'], pt=tl_, size=br_[0]-tl_[0])
		for landmark in a['landmarks']:
			draw_point(im, draw, landmark['position'])

def draw_point(im, draw, position):
	#pt = (int(position.get('x',0)), int(position.get('y',0)))
	p1 = int(position.get('x'))
	p2 = int(position.get('y'))
	draw.ellipse((p1-1,p2-1,p1+1,p2+1),outline="white")
	#draw.point((p1,p2),'white')
	#cv2.circle(im, pt, 3, (0,0,255))

def draw_box(im, draw, vertices):
	v1,v2 = extract_vertices(vertices)
	pt1 = v1.get('x')
	pt2 = v1.get('y')
	pt3 = v2.get('x')
 	pt4 = v2.get('y')
	draw.rectangle((pt1,pt2,pt3,pt4),outline="red")
	#draw.rectangle(pt1,pt3,outline = 'red')
	#cv2.rectangle(im, pt1, pt2, (0,0,255))
	#return pt1, pt2, pt3, pt4

def extract_vertices(vertices):
	""" Extract two opposite vertices from a list of 4 (assumption: rectangle) """

	min_x,max_x,min_y,max_y = float("inf"),float("-inf"),float("inf"),float("-inf")

	for v in vertices:
		if v.get('x',min_y) < min_x:
			min_x = v.get('x')
		if v.get('x',max_y) > max_x:
			max_x = v.get('x')
		if v.get('y',min_y) < min_y:
			min_y = v.get('y')
		if v.get('y',max_y) > max_y:
			max_y = v.get('y')

	v1 = next(v for v in vertices if v.get('x') == min_x and v.get('y') == min_y)
	v2 = next(v for v in vertices if v.get('x') == max_x and v.get('y') == max_y)

	return v1,v2
	
if __name__ == '__main__':
	p = ArgumentParser()
	p.add_argument("-k", dest="api_key", required=True)
	p.add_argument("-i", dest="image_path", required=True,help="path to image")
	a = p.parse_args()
	c = main(a.api_key,a.image_path)
	#main()