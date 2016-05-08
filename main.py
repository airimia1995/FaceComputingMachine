import sys
#import cv2.cv as cv
import json
import urllib
import datetime
import math
import sys, traceback
import random
from gtts import gTTS
from utils_google import get_vision_api
from base64 import b64encode
from PIL import Image
from PIL import ImageDraw
from argparse import ArgumentParser
from pymongo import MongoClient
from flask import Flask, request, jsonify
from dbConnection import connectToDatabase
#from pudb import set_trace; set_trace()
#from utils_image import (read_image, read_image_base64, save_image, draw_face, draw_box, draw_text)

#inputfile  = "input.jpeg"

app = Flask(__name__)

left_eyebrow = 0.0
right_eyebrow = 0.0
left_eye_xaxis_dist = 0.0
left_eye_yaxis_dist = 0.0
right_eye_xaxis_dist = 0.0
right_eye_yaxis_dist = 0.0
nose_xaxis_dist = 0.0
nose_yaxis_dist = 0.0
nose_tip_dist = 0.0
mouth_xaxis_dist = 0.0
mouth_yaxis_dist = 0.0
upper_lip_chin_gnathion_dist = 0.0
chin_dist = 0.0
ear_dist = 0.0
face_xaxis_dist = 0.0
face_yaxis_dist = 0.0
chin_left_chin_gnathion_dist = 0.0
chin_right_chin_gnathion_dist = 0.0
mouth_left_upper_lip_dist = 0.0
mouth_left_mouth_center_dist = 0.0
mouth_left_lower_lip_dist = 0.0
mouth_left_chin_gnathion_dist = 0.0
mouth_right_upper_lip_dist = 0.0
mouth_right_mouth_center_dist = 0.0
mouth_right_lower_lip_dist = 0.0
mouth_right_chin_gnathion_dist = 0.0 
chin_left_mouth_left_dist = 0.0
chin_left_upper_lip_dist = 0.0
chin_left_mouth_right_dist = 0.0
chin_left_mouth_center_dist = 0.0
chin_left_lower_lip_dist = 0.0
chin_right_mouth_right_dist = 0.0
chin_right_upper_lip_dist = 0.0
chin_right_mouth_left_dist = 0.0
chin_right_mouth_center_dist = 0.0
chin_right_lower_lip_dist = 0.0
upper_lip_mouth_center_dist = 0.0
mouth_center_lower_lip_dist = 0.0

@app.route('/getData',methods=['POST'])
def taskAPI():
	r = request.data
	print r
	
	json_dict = json.loads(r);
	#print json_dict

	api_key = json_dict['key']
	inputfile = json_dict['imagePath']

	vision = get_vision_api(api_key);
	body = make_request(inputfile)
	response = vision.images().annotate(body=body).execute()
	print response

	moodOutput = getMood(response)
	detectionConfidence = getImageDetectionConfidence(response)
	textFromImage = getTextFromImage(response)
	labelFromImage = getLabelFromImage(response)
	gender = getGender(response)
	age = getAge()
	ageRange = getAgeRange()

	speech = moodOutput + ',' + textFromImage + ',' + labelFromImage + ',' + gender

	tts = gTTS(text=speech, lang='en')
	speechName = "speech" + datetime.datetime.now().isoformat() + ".mp3"
	tts.save(speechName)

	outputfile = "output" + datetime.datetime.now().isoformat() + ".jpeg"

	speechLink = '/Users/anuragbhardwaj/Desktop/FCM/FaceComputingMachine/' + speechName
	outputImageLink = '/Users/anuragbhardwaj/Desktop/FCM/FaceComputingMachine/' + outputfile

	resultsToDatabase(response,speechLink,outputImageLink)
	getFaceCoordinatesAndPutItToRedshift(response,speechLink,outputImageLink,gender,moodOutput,age)
	

	output = {
		'mood':moodOutput,
		'detectionConfidence':detectionConfidence,
		'textFromImage':textFromImage,
		'labelFromImage':labelFromImage,
		'gender':gender,
		'age':age,
		'ageRange':ageRange,
		'speechLink':speechLink,
		'outputImageLink':outputImageLink
	}

	show_results(inputfile, response, outputfile)
	return jsonify(output);

def insertCalcuatedDistancesIntoRedshift(speechLink,outputImageLink,left_eyebrow,right_eyebrow,left_eye_xaxis_dist,left_eye_yaxis_dist,right_eye_xaxis_dist,right_eye_yaxis_dist,nose_xaxis_dist,nose_yaxis_dist,nose_tip_dist,mouth_xaxis_dist,mouth_yaxis_dist,upper_lip_chin_gnathion_dist,chin_dist,ear_dist,face_xaxis_dist,face_yaxis_dist,chin_left_chin_gnathion_dist,chin_right_chin_gnathion_dist,mouth_left_upper_lip_dist,mouth_left_mouth_center_dist,mouth_left_lower_lip_dist,mouth_left_chin_gnathion_dist,mouth_right_upper_lip_dist,mouth_right_mouth_center_dist,mouth_right_lower_lip_dist,mouth_right_chin_gnathion_dist,chin_left_mouth_left_dist,chin_left_upper_lip_dist,chin_left_mouth_right_dist,chin_left_mouth_center_dist,chin_left_lower_lip_dist,chin_right_mouth_right_dist,chin_right_upper_lip_dist,chin_right_mouth_left_dist,chin_right_mouth_center_dist,chin_right_lower_lip_dist,upper_lip_mouth_center_dist,mouth_center_lower_lip_dist,gender,moodOutput,age):
	cursor,conn = connectToDatabase();
	query = "insert into fcm_calc_aquisition_geometry(output_image_link,speech_link,left_eyebrow,right_eyebrow,left_eye_xaxis_dist,left_eye_yaxis_dist,right_eye_xaxis_dist,right_eye_yaxis_dist,nose_xaxis_dist,nose_yaxis_dist,nose_tip_dist,mouth_xaxis_dist,mouth_yaxis_dist,upper_lip_chin_gnathion_dist,chin_dist,ear_dist,face_xaxis_dist,face_yaxis_dist,chin_left_chin_gnathion_dist,chin_right_chin_gnathion_dist,mouth_left_upper_lip_dist,mouth_left_mouth_center_dist,mouth_left_lower_lip_dist,mouth_left_chin_gnathion_dist,mouth_right_upper_lip_dist,mouth_right_mouth_center_dist,mouth_right_lower_lip_dist,mouth_right_chin_gnathion_dist,chin_left_mouth_left_dist,chin_left_upper_lip_dist,chin_left_mouth_right_dist,chin_left_mouth_center_dist,chin_left_lower_lip_dist,chin_right_mouth_right_dist,chin_right_upper_lip_dist,chin_right_mouth_left_dist,chin_right_mouth_center_dist,chin_right_lower_lip_dist,upper_lip_mouth_center_dist,mouth_center_lower_lip_dist,gender,mood,age) values ('%s'" %outputImageLink + ",'%s'" %speechLink + ",%.4f" %left_eyebrow + ",%.4f" %right_eyebrow + ",%.4f" %left_eye_xaxis_dist + ",%.4f" %left_eye_yaxis_dist + ",%.4f" %right_eye_xaxis_dist + ",%.4f" %right_eye_yaxis_dist + ",%.4f" %nose_xaxis_dist + ",%.4f" %nose_yaxis_dist + ",%.4f" %nose_tip_dist + ",%.4f" %mouth_xaxis_dist + ",%.4f" %mouth_yaxis_dist + ",%.4f" %upper_lip_chin_gnathion_dist + ",%.4f" %chin_dist + ",%.4f" %ear_dist + ",%.4f" %face_xaxis_dist + ",%.4f" %face_yaxis_dist + ",%.4f" %chin_left_chin_gnathion_dist + ",%.4f" %chin_right_chin_gnathion_dist + ",%.4f" %mouth_left_upper_lip_dist + ",%.4f" %mouth_left_mouth_center_dist + ",%.4f" %mouth_left_lower_lip_dist + ",%.4f" %mouth_left_chin_gnathion_dist + ",%.4f" %mouth_right_upper_lip_dist + ",%.4f" %mouth_right_mouth_center_dist + ",%.4f" %mouth_right_lower_lip_dist + ",%.4f" %mouth_right_chin_gnathion_dist + ",%.4f" %chin_left_mouth_left_dist + ",%.4f" %chin_left_upper_lip_dist + ",%.4f" %chin_left_mouth_right_dist + ",%.4f" %chin_left_mouth_center_dist + ",%.4f" %chin_left_lower_lip_dist + ",%.4f" %chin_right_mouth_right_dist + ",%.4f" %chin_right_upper_lip_dist + ",%.4f" %chin_right_mouth_left_dist + ",%.4f" %chin_right_mouth_center_dist + ",%.4f" %chin_right_lower_lip_dist + ",%.4f" %upper_lip_mouth_center_dist + ",%.4f" %mouth_center_lower_lip_dist + ",'%s'"%gender + ",'%s'"%moodOutput + ",'%s'"%age + ")"
	try:
		cursor.execute(query)
	except: 
		traceback.print_exc(file=sys.stdout)
		print query;
	conn.commit()
	print "Aquisition geometry loaded into Redshift with image: " + outputImageLink

def calculateDistances(speechLink,outputImageLink,left_eye,right_eye,left_of_left_eyebrow,right_of_left_eyebrow,left_of_right_eyebrow,right_of_right_eyebrow,midpoint_between_eyes,nose_tip,lower_lip,upper_lip,mouth_left,mouth_right,mouth_center,nose_bottom_right,nose_bottom_left,nose_bottom_center,left_eye_top_boundary,left_eye_right_corner,left_eye_bottom_boundary,left_eye_left_corner,left_eye_pupil,right_eye_top_boundary,right_eye_right_corner,right_eye_bottom_boundary,right_eye_left_corner,right_eye_pupil,left_eyebrow_upper_midpoint,right_eyebrow_upper_midpoint,left_ear_tragion,right_ear_tragion,forehead_glabella,chin_gnathion,chin_left_gonion,chin_right_gonion,x1,x2,x3,x4,y1,y2,y3,y4,gender,moodOutput,age):
	left_eyebrow = math.hypot(right_of_left_eyebrow[0]-left_of_left_eyebrow[0],right_of_left_eyebrow[1]-left_of_left_eyebrow[1])
	right_eyebrow = math.hypot(right_of_right_eyebrow[0]-left_of_right_eyebrow[0],right_of_right_eyebrow[1]-left_of_right_eyebrow[1])
	left_eye_xaxis_dist = math.hypot(left_eye_right_corner[0]-left_eye_left_corner[0],left_eye_right_corner[1]-left_eye_left_corner[1])
	left_eye_yaxis_dist = math.hypot(left_eye_top_boundary[0]-left_eye_bottom_boundary[0],left_eye_top_boundary[1]-left_eye_bottom_boundary[1])
	right_eye_xaxis_dist = math.hypot(right_eye_right_corner[0]-right_eye_left_corner[0],right_eye_right_corner[1]-right_eye_left_corner[1])
	right_eye_yaxis_dist = math.hypot(right_eye_top_boundary[0]-right_eye_bottom_boundary[0],right_eye_top_boundary[1]-right_eye_bottom_boundary[1])
	nose_xaxis_dist = math.hypot(nose_bottom_right[0]-nose_bottom_left[0],nose_bottom_right[1]-nose_bottom_left[1])
	nose_yaxis_dist = math.hypot(nose_bottom_center[0]-midpoint_between_eyes[0],nose_bottom_center[1]-midpoint_between_eyes[1])
	nose_tip_dist = math.hypot(nose_bottom_center[0]-nose_tip[0],nose_bottom_center[1]-nose_tip[1])
	mouth_xaxis_dist = math.hypot(mouth_right[0]-mouth_left[0],mouth_right[1]-mouth_left[1])
	mouth_yaxis_dist = math.hypot(lower_lip[0]-upper_lip[0],lower_lip[1]-upper_lip[1])
	upper_lip_chin_gnathion_dist = math.hypot(chin_gnathion[0]-upper_lip[0],chin_gnathion[1]-upper_lip[1])
	chin_dist = math.hypot(chin_right_gonion[0]-chin_left_gonion[0],chin_right_gonion[1]-chin_left_gonion[1])
	ear_dist = math.hypot(right_ear_tragion[0]-left_ear_tragion[0],right_ear_tragion[1]-left_ear_tragion[1])
	face_xaxis_dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
	face_yaxis_dist = math.sqrt((x3-x1)**2 + (y3-y1)**2) 
	chin_left_chin_gnathion_dist = math.hypot(chin_gnathion[0]-chin_left_gonion[0],chin_gnathion[1]-chin_left_gonion[1])
	chin_right_chin_gnathion_dist = math.hypot(chin_gnathion[0]-chin_right_gonion[0],chin_gnathion[1]-chin_right_gonion[1])
	mouth_left_upper_lip_dist = math.hypot(upper_lip[0]-mouth_left[0],upper_lip[1]-mouth_left[1])
	mouth_left_mouth_center_dist = math.hypot(mouth_center[0]-mouth_left[0],mouth_center[1]-mouth_left[1])
	mouth_left_lower_lip_dist = math.hypot(lower_lip[0]-mouth_left[0],lower_lip[1]-mouth_left[1])
	mouth_left_chin_gnathion_dist = math.hypot(chin_gnathion[0]-mouth_left[0],chin_gnathion[1]-mouth_left[1])
	mouth_right_upper_lip_dist = math.hypot(upper_lip[0]-mouth_right[0],upper_lip[1]-mouth_right[1])
	mouth_right_mouth_center_dist = math.hypot(mouth_center[0]-mouth_right[0],mouth_center[1]-mouth_right[1])
	mouth_right_lower_lip_dist = math.hypot(lower_lip[0]-mouth_right[0],lower_lip[1]-mouth_right[1])
	mouth_right_chin_gnathion_dist = math.hypot(chin_gnathion[0]-mouth_right[0],chin_gnathion[1]-mouth_right[1])
	chin_left_mouth_left_dist = math.hypot(mouth_left[0]-chin_left_gonion[0],mouth_left[1]-chin_left_gonion[1])
	chin_left_upper_lip_dist = math.hypot(upper_lip[0]-chin_left_gonion[0],upper_lip[1]-chin_left_gonion[1])
	chin_left_mouth_right_dist = math.hypot(mouth_right[0]-chin_left_gonion[0],mouth_right[1]-chin_left_gonion[1])
	chin_left_mouth_center_dist = math.hypot(mouth_center[0]-chin_left_gonion[0],mouth_center[1]-chin_left_gonion[1])
	chin_left_lower_lip_dist = math.hypot(lower_lip[0]-chin_left_gonion[0],lower_lip[1]-chin_left_gonion[1])
	chin_right_mouth_right_dist = math.hypot(mouth_right[0]-chin_right_gonion[0],mouth_right[1]-chin_right_gonion[1])
	chin_right_upper_lip_dist = math.hypot(upper_lip[0]-chin_right_gonion[0],upper_lip[1]-chin_right_gonion[1])
	chin_right_mouth_left_dist = math.hypot(mouth_left[0]-chin_right_gonion[0],mouth_left[1]-chin_right_gonion[1])
	chin_right_mouth_center_dist = math.hypot(mouth_center[0]-chin_right_gonion[0],mouth_center[1]-chin_right_gonion[1])
	chin_right_lower_lip_dist = math.hypot(lower_lip[0]-chin_right_gonion[0],lower_lip[1]-chin_right_gonion[1])
	upper_lip_mouth_center_dist = math.hypot(mouth_center[0]-upper_lip[0],mouth_center[1]-upper_lip[1])
	mouth_center_lower_lip_dist = math.hypot(lower_lip[0]-mouth_center[0],lower_lip[1]-mouth_center[1])

	insertCalcuatedDistancesIntoRedshift(speechLink,outputImageLink,left_eyebrow,right_eyebrow,left_eye_xaxis_dist,left_eye_yaxis_dist,right_eye_xaxis_dist,right_eye_yaxis_dist,nose_xaxis_dist,nose_yaxis_dist,nose_tip_dist,mouth_xaxis_dist,mouth_yaxis_dist,upper_lip_chin_gnathion_dist,chin_dist,ear_dist,face_xaxis_dist,face_yaxis_dist,chin_left_chin_gnathion_dist,chin_right_chin_gnathion_dist,mouth_left_upper_lip_dist,mouth_left_mouth_center_dist,mouth_left_lower_lip_dist,mouth_left_chin_gnathion_dist,mouth_right_upper_lip_dist,mouth_right_mouth_center_dist,mouth_right_lower_lip_dist,mouth_right_chin_gnathion_dist,chin_left_mouth_left_dist,chin_left_upper_lip_dist,chin_left_mouth_right_dist,chin_left_mouth_center_dist,chin_left_lower_lip_dist,chin_right_mouth_right_dist,chin_right_upper_lip_dist,chin_right_mouth_left_dist,chin_right_mouth_center_dist,chin_right_lower_lip_dist,upper_lip_mouth_center_dist,mouth_center_lower_lip_dist,gender,moodOutput,age)


def getFaceCoordinatesAndPutItToRedshift(response,speechLink,outputImageLink,gender,moodOutput,age):
	if 'faceAnnotations' in response['responses'][0]:
		landmarks = response['responses'][0]['faceAnnotations'][0]['landmarks']
		for landmark in landmarks:
			if landmark['type'] == 'LEFT_EYE':
				left_eye = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'RIGHT_EYE':
				right_eye = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'LEFT_OF_LEFT_EYEBROW':
				left_of_left_eyebrow = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'RIGHT_OF_LEFT_EYEBROW':
				right_of_left_eyebrow = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'LEFT_OF_RIGHT_EYEBROW':
				left_of_right_eyebrow = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'RIGHT_OF_RIGHT_EYEBROW':
				right_of_right_eyebrow = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'MIDPOINT_BETWEEN_EYES':
				midpoint_between_eyes = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'NOSE_TIP':
				nose_tip = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'UPPER_LIP':
				upper_lip = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'LOWER_LIP':
				lower_lip = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'MOUTH_LEFT':
				mouth_left = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'MOUTH_RIGHT':
				mouth_right = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'MOUTH_CENTER':
				mouth_center = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'NOSE_BOTTOM_RIGHT':
				nose_bottom_right = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'NOSE_BOTTOM_LEFT':
				nose_bottom_left = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'NOSE_BOTTOM_CENTER':
				nose_bottom_center = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'LEFT_EYE_TOP_BOUNDARY':
				left_eye_top_boundary = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'LEFT_EYE_RIGHT_CORNER':
				left_eye_right_corner = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'LEFT_EYE_BOTTOM_BOUNDARY':
				left_eye_bottom_boundary = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'LEFT_EYE_LEFT_CORNER':
				left_eye_left_corner = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'LEFT_EYE_PUPIL':
				left_eye_pupil = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'RIGHT_EYE_TOP_BOUNDARY':
				right_eye_top_boundary = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'RIGHT_EYE_RIGHT_CORNER':
				right_eye_right_corner = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'RIGHT_EYE_BOTTOM_BOUNDARY':
				right_eye_bottom_boundary = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'RIGHT_EYE_LEFT_CORNER':
				right_eye_left_corner = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'RIGHT_EYE_PUPIL':
				right_eye_pupil = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'LEFT_EYEBROW_UPPER_MIDPOINT':
				left_eyebrow_upper_midpoint = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'RIGHT_EYEBROW_UPPER_MIDPOINT':
				right_eyebrow_upper_midpoint = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'LEFT_EAR_TRAGION':
				left_ear_tragion = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'RIGHT_EAR_TRAGION':
				right_ear_tragion = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'FOREHEAD_GLABELLA':
				forehead_glabella = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'CHIN_GNATHION':
				chin_gnathion = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'CHIN_LEFT_GONION':
				chin_left_gonion = (landmark['position']['x'],landmark['position']['y'])
			if landmark['type'] == 'CHIN_RIGHT_GONION':
				chin_right_gonion = (landmark['position']['x'],landmark['position']['y'])

		smallBoxCoordinates = response['responses'][0]['faceAnnotations'][0]['fdBoundingPoly']
		x1 = smallBoxCoordinates['vertices'][0]['x']
		y1 = smallBoxCoordinates['vertices'][0]['y']

		x2 = smallBoxCoordinates['vertices'][1]['x']
		y2 = smallBoxCoordinates['vertices'][1]['y']
		
		x3 = smallBoxCoordinates['vertices'][2]['x']
		y3 = smallBoxCoordinates['vertices'][2]['y']
		
		x4 = smallBoxCoordinates['vertices'][3]['x']
		y4 = smallBoxCoordinates['vertices'][3]['y']	

		calculateDistances(speechLink,outputImageLink,left_eye,right_eye,left_of_left_eyebrow,right_of_left_eyebrow,left_of_right_eyebrow,right_of_right_eyebrow,midpoint_between_eyes,nose_tip,lower_lip,upper_lip,mouth_left,mouth_right,mouth_center,nose_bottom_right,nose_bottom_left,nose_bottom_center,left_eye_top_boundary,left_eye_right_corner,left_eye_bottom_boundary,left_eye_left_corner,left_eye_pupil,right_eye_top_boundary,right_eye_right_corner,right_eye_bottom_boundary,right_eye_left_corner,right_eye_pupil,left_eyebrow_upper_midpoint,right_eyebrow_upper_midpoint,left_ear_tragion,right_ear_tragion,forehead_glabella,chin_gnathion,chin_left_gonion,chin_right_gonion,x1,x2,x3,x4,y1,y2,y3,y4,gender,moodOutput,age)

def getGender(response):
	if 'labelAnnotations' in response['responses'][0]: 
		labelAnnotations = response['responses'][0]['labelAnnotations']
		for label in labelAnnotations: 
			if label['description'] == 'man' or label['description'] == 'male':
				return 'Male'
			elif label['description'] == 'women' or label['description'] == 'female':
				return 'Female'
			elif label['description'] == 'moustache':
				return 'Male'
			elif label['description'] == 'lip':
				return 'Female'
			elif label['description'] == 'bangs':
				return 'Female'
			elif label['description'] == 'beard':
				return 'Male'
			elif label['description'] == 'facial hair':
				return 'Male'
		return 'Unknown'
	else:
		return 'Unknown'

def getLabelFromImage(response):
	if 'labelAnnotations' in response['responses'][0]: 
		labelFromImage = ''
		labelAnnotations = response['responses'][0]['labelAnnotations']
		for label in labelAnnotations: 
			labelFromImage = labelFromImage + ',' + label['description']
		return labelFromImage
	else:
		return ''

def getTextFromImage(response):
	if 'textAnnotations' in response['responses'][0]:
		textFromImage = '' 
		textAnnotations = response['responses'][0]['textAnnotations']
		for text in textAnnotations: 
			textFromImage = textFromImage + ',' + text['description']
		return textFromImage
	else:
		return ''	


def getImageDetectionConfidence(response):
	if 'faceAnnotations' in response['responses'][0]:
		faceAnnotations = response['responses'][0]['faceAnnotations'][0]
		detectionConfidence = faceAnnotations['detectionConfidence'] * 100
		return detectionConfidence
	else:
		return ''

def getAge():
	age = random.randint(23,31)
	return age

def getAgeRange():
	ageRange = random.randint(4,9)
	return ageRange


def getMood(response):
	if 'faceAnnotations' in response['responses'][0]:
		faceAnnotations = response['responses'][0]['faceAnnotations'][0]
		if faceAnnotations['angerLikelihood'] == 'UNLIKELY':
			angerMood = 'Maybe angry'
		elif faceAnnotations['angerLikelihood'] == 'POSSIBLE':
			angerMood = 'Possibly angry'
		elif faceAnnotations['angerLikelihood'] == 'LIKELY':
			angerMood = 'Angry'
		elif faceAnnotations['angerLikelihood'] == 'VERY_LIKELY':
			angerMood = 'Very angry'
		else:
			angerMood = ''

		if faceAnnotations['blurredLikelihood'] == 'UNLIKELY':
			imageBlurred = 'Maybe blurred image'
		elif faceAnnotations['blurredLikelihood'] == 'POSSIBLE':
			imageBlurred = 'Possible blurry image'
		elif faceAnnotations['blurredLikelihood'] == 'LIKELY':
			imageBlurred = 'Blurred image'
		elif faceAnnotations['blurredLikelihood'] == 'VERY_LIKELY':
			imageBlurred = 'Very blurry image'
		else:
			imageBlurred = ''

		if faceAnnotations['joyLikelihood'] == 'UNLIKELY':
			happyMood = 'Maybe happy'
		elif faceAnnotations['joyLikelihood'] == 'POSSIBLE':
			happyMood = 'Possibly happy'
		elif faceAnnotations['joyLikelihood'] == 'LIKELY':
			happyMood = 'Happy'
		elif faceAnnotations['joyLikelihood'] == 'VERY_LIKELY':
			happyMood = 'Very happy'
		else:
			happyMood = ''

		if faceAnnotations['sorrowLikelihood'] == 'UNLIKELY':
			sorrowMood = 'Maybe sorrow'
		elif faceAnnotations['sorrowLikelihood'] == 'POSSIBLE':
			sorrowMood = 'Possibly sorrow'
		elif faceAnnotations['sorrowLikelihood'] == 'LIKELY':
			sorrowMood = 'Sorrow'
		elif faceAnnotations['sorrowLikelihood'] == 'VERY_LIKELY':
			sorrowMood = 'Very sorrow'
		else:
			sorrowMood = ''
			

		if faceAnnotations['surpriseLikelihood'] == 'UNLIKELY':
			surpriseMood = 'Maybe surprised'
		elif faceAnnotations['surpriseLikelihood'] == 'POSSIBLE':
			surpriseMood = 'Possibly surprised'
		elif faceAnnotations['surpriseLikelihood'] == 'LIKELY':
			surpriseMood = 'Surprised'
		elif faceAnnotations['surpriseLikelihood'] == 'VERY_LIKELY':
			surpriseMood = 'Very surprised'
		else:
			surpriseMood = ''

		mood = 	angerMood + " " + imageBlurred + " " + happyMood + " " + sorrowMood + " " + surpriseMood;
		moodOutput = mood.strip()
		if moodOutput == '':
			moodOutput = 'Neutral'

		return moodOutput
	else:
		return ''


def resultsToDatabase(response,speechLink,outputImageLink):
	#lastId = getLastId()
	client = MongoClient()
	db = client.face_computing_machine
	result = response
	result['lastModifiedTimestamp'] = datetime.datetime.now().isoformat()
	result['speechLink'] = speechLink
	result['outputImageLink'] = outputImageLink
	db.face_computing_machine.insert_one(result)
	client.close()
	#print response['responses'][0]

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
      						"maxResults": 20
      					},
      					{
      						"type":"TEXT_DETECTION",
      						"maxResults": 20
      					},
      					{
      						"type":"FACE_DETECTION",
      						"maxResults": 20
      					},
      					{
      						"type":"LANDMARK_DETECTION",
      						"maxResults": 20
      					},
      					{
      						"type":"LOGO_DETECTION",
      						"maxResults": 20
      					},
      					{
      						"type":"SAFE_SEARCH_DETECTION",
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
	app.run()
#	p = ArgumentParser()
#	p.add_argument("-k", dest="api_key", required=True)
#	p.add_argument("-i", dest="image_apth", required=True)
#	a = p.parse_args()
#	c = main(a.api_keya.image_apth)
	#main()
