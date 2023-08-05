#This module is designed to handle href image overlays for blocks
import pandas as pd
import numpy as np
import itertools
'''
Module: blocks.py

Purpose: Designed to construct simple (generally block) href image overlays in KML structure

What this module assumes you have or can produce quite easily:
	-A csv file with point data and data to be associated with in in the same row.
	-The points headers must contain the letters 'lat', 'long', or 'elev' (elevation not needed though)

General function structure:
	-all functions tier up to make_blocks()/block() 
		*these are the ONLY functions intended for use specifically make_blocks()
	-syntax for constituent functions has two general types
		*getx-gets a piece of data from a the table or given block row
		*returnx-returns a kml line that has usualy a piece of the retrieved getx function

In other words "return" outputs are going straight into the kml file as a line and "get" functions are retrieving values 
from the table referenced.


List of functions within this module:
1) read(file)-given file directory 
2) getcolor(color)-given a color returns an href id to be placed in KML
3) readtxt(filelocation)-reads text file and parses into list
4) getlatlongs(data)-for a header and list row of values gets the lats/longs out of the row
5) getextremas(data)-from the output of getlatlongs() returns a list of the extrema in [E,W,N,S] order
6) getsimpledata(rows)-given a set of block rows returns the simple data found within them
7) returnsimpledata(rows)-given a set of block rows returns lines of kml for simple data
8) returnoverlaystart()-returns the beginning of an overlay object
9) returnoverlayend()-returns the end of an overlay object
10) returniconschema()-returns the glue lines between the end of icons and  simple data 
11) returnsimpledatatoextrema-returns the glue from simpledata to extrema
12) return_start(name)-returns the start block of kml file to the overlay object
13) returncolorline(color)-given a color returns the line of href corresponding to color
14) returnextremaline(rows)-given a set of rows returns the extrema line to line up block image
15) block(rows,color)-given a set of lines and a color of block image returns lines for image overlay object
16) make_blocks-given either a list of 5 rows with poitns on each row or a table with x rows with each corner in every row i.e. 4 points per row returns a kml line block for said table (must have color field)
17) parselist(listofkmllines,name)-given list of kml lines and name (hopefully with ".kml" extensions) writes kml lines to file
18) packageblocks(list)-returns a list of kml lines from a make_blocks output to only have block objects
19) folder(name,description,list)-Given a list of packaged lines returns folder with lines to be packaged with the name and description
20) packagefinal(name,list)-given a list of lines and a name to be given for the inner kml returns list of lines ready to be written to kml file


created by: Bennett Murphy
'''

#function that reads csv file to memory
def read(file):
	data=[]
	import csv
	f=csv.reader(open(file,'rb'),delimiter=',',quotechar="\"")
	for row in f:
		data.append(row)
	return data

#given a color returns an href id to be placed in KML
def getcolor(color,**kwargs):
	if kwargs is not None:
		heatmap=False
		for key,value in kwargs.iteritems():
			if key=='heatmap':
				if value==True:
					heatmap=True

	href=''
	if not heatmap==True:
		colors=[['Color', 'Link'], ['yellow', 'https://cloud.githubusercontent.com/assets/10904982/11331552/68ee910a-918a-11e5-951f-66895e8bb8c4.png'], ['white', 'https://cloud.githubusercontent.com/assets/10904982/11331550/68e9a424-918a-11e5-89f3-1deac24394d8.png'], ['red', 'https://cloud.githubusercontent.com/assets/10904982/11331551/68eab378-918a-11e5-9b24-8df334742ad6.png'], ['pink', 'https://cloud.githubusercontent.com/assets/10904982/11331549/68e92dc8-918a-11e5-8cf3-9bcbbd983173.png'], ['orange', 'https://cloud.githubusercontent.com/assets/10904982/11331548/68e5df06-918a-11e5-93a3-820457d90bdd.png'], ['blue', 'https://cloud.githubusercontent.com/assets/10904982/11331547/68e109ea-918a-11e5-999a-60fc994b3b18.png'], ['light green', 'https://cloud.githubusercontent.com/assets/10904982/11331546/68dba34c-918a-11e5-9d3c-2da2fae161da.png'], ['blue', 'https://cloud.githubusercontent.com/assets/10904982/11331545/68d37cbc-918a-11e5-884d-24532d8c213c.png'], ['light blue', 'https://cloud.githubusercontent.com/assets/10904982/11331544/68d11828-918a-11e5-8c1b-9823e1a6a5be.png']]
	elif heatmap==True:
		colors=[['block', 'href'], ['block1', 'https://cloud.githubusercontent.com/assets/10904982/12028704/dc262c9c-ada9-11e5-823c-099ead474dff.png'], ['block2', 'https://cloud.githubusercontent.com/assets/10904982/12028705/dc32662e-ada9-11e5-89c9-f868dd3ab115.png'], ['block3', 'https://cloud.githubusercontent.com/assets/10904982/12028706/dc34e25a-ada9-11e5-873a-202b57baed66.png'], ['block4', 'https://cloud.githubusercontent.com/assets/10904982/12028707/dc376cd2-ada9-11e5-81c1-104efb98226a.png'], ['block5', 'https://cloud.githubusercontent.com/assets/10904982/12028708/dc394976-ada9-11e5-9ba2-14432dd23faa.png'], ['block6', 'https://cloud.githubusercontent.com/assets/10904982/12028709/dc3aa8a2-ada9-11e5-9ca2-2005b5a7fbf2.png'], ['block7', 'https://cloud.githubusercontent.com/assets/10904982/12028710/dc3d684e-ada9-11e5-9030-facd65079b70.png']]

	for row in colors[1:]:
		if row[0]==str(color):
			href=str(row[1])
	return href


#function to read text file into me
def readtxt(filelocation):
	f=open(filelocation,'r')
	f=f.read()
	f=str.split(f,'\n')
	return f


#given a set of table data returns the lat and longs associated with said tables
def getlatlongs(data):
	file=data

	#taking the following snippet from alignments.py
	#looking for lats, long and elevations within file
	#supports two points per line the most you would find for a path generally
	lats=[]
	longs=[]
	elevations=[]
	cordblock=[]
	count=0
	header=file[0]
	for row in header:
		row=str(row).upper()
		if 'LAT' in str(row):
			lats.append(count)
		elif 'LONG' in str(row):
			longs.append(count)
		elif 'ELEV' in str(row):
			elevations.append(count)
		count+=1


	#if one lat and per row
	#FILETYPE OPTION: 1 LATITUDE, 1 LONGITUDE
	if len(lats)==1 and len(longs)==1:
		count=0
		cordrows=[]
		#getting the row numbers the latitude and longitude occur in
		rowlat1=lats[0]
		rowlong1=longs[0]

		#getting point to point rows for a flat (1 point row) csv file
		for row in file[1:]: 
			point=[float(row[rowlat1]),float(row[rowlong1])]
			cordrows.append(point)
		return [['Lat','Long']]+cordrows
	elif len(lats)==4 and len(longs)==4:
		cordrows=[]
		cordrows2=[]
		for row in file[1:]:
			cordrows=[]
			for lat,long in itertools.izip(lats,longs):
				point=[float(row[lat]),float(row[long])]
				cordrows.append(point)
			cordrows2+=[cordrows]
		return [['Lat','Long']]+cordrows2

#given a set of data points from getlatlongs output returns north south east and west barrings to go into kml
def getextremas(data):
	points=getlatlongs(data)
	points2=points[1:]
	if len(points2)==1:
		points=pd.DataFrame(points2[0],columns=points[0])	
		south=points['Lat'].min()
		north=points['Lat'].max()
		west=points['Long'].min()
		east=points['Long'].max()
		return [east,west,south,north]
	return []

#input a complete file list or just the row and the header to return packaged header,val pairs
def getsimpledata(rows):
	info=[]
	if len(rows)==5:
		header=rows[0]
		firstrow=rows[1]
		lastrow=rows[-1]

		for firstval,lastval,headerval in itertools.izip(firstrow,lastrow,header):
			if firstval==lastval:
				info.append([headerval,firstval])
	elif len(rows)==2:
		header=rows[0]
		row=rows[1]
		for a,b in itertools.izip(header,row):
			if not 'LAT' in str(a).upper() and not 'LONG' in str(a).upper():
				info.append([a,b])
	return info

#given output of get simpledata returns a block of kml lines correspoinding to each simple data field
def returnsimpledata(rows):
	info=getsimpledata(rows)
	simpleblock=[]
	line='        <SimpleData name="'
	line2='">'
	line3='</SimpleData>'
	for row in info:
		megaline=line+str(row[0])+line2+str(row[1])+line3
		simpleblock.append(megaline)
	return simpleblock

#returns start of ground overlay block
def returnoverlaystart():
	return ['  <GroundOverlay>', '    <Icon>']

#returns end of ground overlay block
def returnoverlayend():
	return ['    </LatLonBox>','  </GroundOverlay>']

#returns the kml lines between the href line and simpledata block lines
def returniconschema():
	return ['    </Icon>', '    <ExtendedData>', '      <SchemaData schemaUrl="#S_Export_Output_IDSDSSSSSDSSSDSDSSSSSDS">']


#end of schema data to the line in which extrema are inserted
def returnsimpledatatoextrema():
	return ['      </SchemaData>', '    </ExtendedData>', '    <LatLonBox>']

#gets the start of the block kml with syntatic header
def return_start(name):
	templatelist=['<?xml version="1.0" encoding="UTF-8"?>', '<kml xmlns="http://earth.google.com/kml/2.2">', '<Document>', '  <name>Block</name>', '  <open>0</open>']
	if name=='':
		return templatelist
	else:
		newlist=[]
		for row in templatelist:
			val=row
			if 'Block' in row:
				val=row.replace('Block',name)
			newlist.append(val)
		return newlist

#given a color returns line in kml file to grab corresponding blocks
def returncolorline(color,**kwargs):
	if kwargs is not None:
		heatmap=False
		for key,value in kwargs.iteritems():
			if key=='heatmap':
				if value==True:
					heatmap=True
	line=['      <href>XXX</href>']
	href=getcolor(str(color),heatmap=heatmap)
	return [line[0].replace('XXX',href)]


#given a list of output extrema [east,west,south,north] returns lines correstpoind lines
def returnextremaline(rows):
	extremas=getextremas(rows)
	extrema=extremas
	if len(extrema)==4:
		row=extrema
		north=float(row[3])
		south=float(row[2])
		west=float(row[1])
		east=float(row[0])
		line='      <north>'+str(north)+'</north><south>'+str(south)+'</south><east>'+str(east)+'</east><west>'+str(west)+'</west>'
	if not extrema==[]:
		return [line]

#given a list of 5 rows with a point correspoinding to each corner on each row
#or a  list of two rows with 8 header fields corresponding to each corner lats/longs
def block(rows,color,heatmap):
	p1=returnoverlaystart()
	p2=returncolorline(color,heatmap=heatmap)
	p3=returniconschema()
	p4=returnsimpledata(rows)
	p5=returnsimpledatatoextrema()
	p6=returnextremaline(rows)
	p7=returnoverlayend()
	return p1+p2+p3+p4+p5+p6+p7


#given a filenameorlist and optional kwargs will return a kml file list with the blocks present
'''
color=Color of block
list=if inputing list in filenamorlist then list=True boolean
name=name of kml file
colorfield=row position in each row that a color is given
'''
def make_blocks(filenameorlist,**kwargs):
	if kwargs is not None:
		color='White'
		heatmap=False
		list=False
		name=''
		colorfield=None
		for key,value in kwargs.iteritems():
			if key=='color':
				color=value
			elif key=='list':
				list=value
			elif key=='name':
				name=value
			elif key=='colorfield':
				colorfield=int(value)
			if key=='heatmap':
				if value==False:
					heatmap=False
	
	#getting the proper list (table) from the input list operator
	if list==False:
		file=read(filenameorlist)
	elif list==True:
		if isinstance(filenameorlist, pd.DataFrame):
			filenameorlist=filenameorlist.values.tolist()
		file=filenameorlist

	#if no colorfield attribute is present the script currently expects you to have a 2 row table or 5 row table
	if colorfield==None:
		#stuff for single block make here
		header=file[0]
		innerblock=[]
		for row in file[1:]:
			part=block([header]+[row],color,heatmap)
			innerblock+=part
			
	else:
		#stuff for multiple block make here
		header=file[0]
		innerblock=[]
		for row in file[1:]:
			color=row[int(colorfield)]
			part=block([header]+[row],color,heatmap)
			innerblock+=part
	final=return_start(name)+innerblock+['</Document>','</kml>']		
	return final


#parses list into kml file by giving a list of kml lines then giving the kml file name
#appends a list of lines to a kml file
def parselist(list,location):
	f=open(location,'w')
	for row in list:
		f.writelines(row+'\n')
	f.close()
	print 'Kml file written to location: %s' % location

#packages blocks into package files
def packageblocks(list):
	return list[5:-2]

#making folder to package elements list is the list of the element kml files
def folder(folder,description,list):
	a=startfolder(folder,description)
	b=endfolder()
	list=a+list+b
	return list

#making frame around elements and subdirectories that will return a list ready to be exported into a kml file
def packagefinal(name,list):
	a=start(name)
	b=end('')
	final=a+list+b
	return final



