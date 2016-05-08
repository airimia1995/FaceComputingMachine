import psycopg2
import pprint
import requests
import xmltodict, json
import urllib
import datetime
import csv
import threading
from threading import Thread
import sys, traceback

reload(sys);
sys.setdefaultencoding("utf-8");

def connectToDatabase():
	conn_string = "dbname='sunedison' port='5439' user='abhardwaj' password='Master12' host='sunedisondatawarehouse.cgnr3c8sn1sz.us-west-2.redshift.amazonaws.com'";
	print "Connecting to Redshift";
	conn = psycopg2.connect(conn_string);
	print "Connected to Redshift";
	cursor = conn.cursor();
	return cursor,conn
