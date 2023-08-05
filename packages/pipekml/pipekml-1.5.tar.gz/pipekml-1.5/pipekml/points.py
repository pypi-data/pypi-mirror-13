


'''
Module: points.py

Purpose: Designed to construct kml for points and/or for large kmls files with multiple data types.

What this module assumes you have or can produce quite easily:
	-A csv file with point data and data to be associated with in in the same row.
	-The points headers must contain the letters 'lat', 'long', or 'elev' (elevation not needed though)
	

List of functions within this module:
1) writecsv(data,location)-writes csv file with given data to given location
2) read(location)-reads csv file to memory
3) get_start_block(name,folder,description)-given the name of kml file, the name of the folder and the description gets the first slab of lines to be parsed (for reach folder or object)
4) options(name,scale,icon)-retrieves the kml block of lines for most of the optionsin the beginning. (see MUTCD icon table for more info)
5) start(name)-given name of kml file returns very start of kml file
6) get_icon(icond)-for a given icon id places image to be icon in folder that will soon be parsed to kml
7) dataforpoint(data)-given a list with syntax ['FIELD HEADER','VALUE'] for x amount of rows in data returns lines that hold said data 
8) endp(lat,long)-for a given lat long parses into kml syntax and makes into applicable rows for combination later
9) end(folder)-gets ending block of lines
10) placemark(name,scale,data,point,icon)-given all theinputs for a placemark point returns a list of lines from <Folder> to </Folder> or <Placemark> to </Placemark>
11) makedatas([x1,x2,x3],[y1,y2,y3])-formats data to be used for dataforpoint(data) resulting transformation [[x1,y1],[x2,y2],[x3,y3]] (where x is generally your field headers in a table)
12) parselist(list,location)-writes list of lines to kml file in a given location
13) gen_row(list)-generator for a List
14) getlatlong(row,header)-gets lat and long from a given header by iterating through iterating
15) make_points(pointcsvfile,**kwargs)-makes csv file for every row in file if no index is given
16) startfolder(folder,description)-given folder and description returns preceding two lines related to it
17) endfolder()-returns ending line for folder
18) folder(name,description,list)-Given a list of packaged lines returns folder with lines to be packaged with the name and description
19) packagefinal(name,list)-given a list of lines and a name to be given for the inner kml returns list of lines ready to be written to kml file

created by Bennett Murphy
'''

#function that reads csv file to memory
def read(file):
	data=[]
	import csv
	f=csv.reader(open(file,'rb'),delimiter=',',quotechar="\"")
	for row in f:
		data.append(row)
	return data


#getting the starting block including the entire kml name
def get_start_block(name,folder,description):
	list=[]
	start=['<?xml version="1.0" encoding="UTF-8"?>', '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">', '<Document>', '\t<name>XXX</name>\t']
	if folder=='':
		start=['<?xml version="1.0" encoding="UTF-8"?>', '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">', '<Document>', '\t<name>XXX</name>\t']
	else:
		start=start+['\t<Folder>','\t<name>'+folder+'</name>']
	if not description=='':
		start=start+['\t<description>'+description+'\t</description>']
	for row in start:
		val=row
		if 'XXX' in row:
			val=row.replace('XXX',name)
		list.append(val)
	return list

#get options for the scale and name of point eventually the type and color of poitn
def options(name,scale,icon):
	list=[]
	if '&' in str(name):
		name=name.replace('&','and')
	a=['\t<Placemark>', '\t\t<name>NAME</name>', '\t\t<Style id="s_ylw-pushpin">', '\t\t<IconStyle>','\t\t\t<scale>SCALE</scale>', '\t\t\t<Icon>', '\t\t\t\t<href>ICON</href>', '\t\t\t</Icon>', '\t\t\t<hotSpot x="0.5" y="0" xunits="fraction" yunits="fraction"/>', '\t\t</IconStyle>','\t\t<LabelStyle>','\t\t\t<scale>0</scale>','\t\t</LabelStyle>','\t\t<ListStyle>', '\t\t</ListStyle>', '\t</Style>', '\t<StyleMap id="m_ylw-pushpin">', '\t\t<Pair>', '\t\t\t<key>normal</key>', '\t\t\t<styleUrl>#s_ylw-pushpin</styleUrl>', '\t\t</Pair>', '\t\t<Pair>', '\t\t\t<key>highlight</key>', '\t\t\t<styleUrl>#s_ylw-pushpin_hl</styleUrl>', '\t\t</Pair>', '\t</StyleMap>', '\t\t<ExtendedData>', '\t\t\t<SchemaData schemaUrl="#S_id2014_ISSSDDSSSDDDDID">']
	for row in a:
		val=row
		if 'NAME' in row:
			val=row.replace('NAME',name)
		elif 'SCALE' in row:
			val=row.replace('SCALE',str(scale))
		elif 'ICON' in row:
			val=row.replace('ICON',icon[:])
		list.append(val)
	return list

#getting starting block for combined routes and points
def start(name):
	list=[]
	start=['<?xml version="1.0" encoding="UTF-8"?>', '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">', '<Document>', '\t<name>XXX</name>\t']
	if name=='':
		for row in start:
			val=row
			if 'XXX' in row:
				if '&' in str(name):
					name=name.replace('&','and')
				val=row.replace('XXX',str(name))
			list.append(val)
	else:
		for row in start:
			val=row
			if 'XXX' in row:
				if '&' in str(name):
					name=name.replace('&','and')
				val=row.replace('XXX',str(name))
			list.append(val)
		list.append('\t<description>https://github.com/murphy214</description>')
	return list



#place icon in temporary directory from the given icon id
def get_icon(iconid):
	url=iconid
	return url
	
	
#returns the list with unique data associated with point
#data is a 2 column list with header and value associated with each
#example data row ['Route','WV 10']
def dataforpoint(data):
	list=[]
	for row in data:
		val='\t\t\t\t<SimpleData name="'+str(row[0])+'">'+str(row[1])+'</SimpleData>'
		list.append(val)
	return list


#getting end of the block for points
def endp(point):
	lat=str(point[0])
	long=str(point[1])
	coord=str(long)+', '+str(lat)
	a=['\t\t\t</SchemaData>', '\t\t</ExtendedData>', '\t\t<gx:balloonVisibility>1</gx:balloonVisibility>', '\t\t<Point>', '\t\t\t<coordinates>XXXX</coordinates>', '\t\t</Point>', '\t</Placemark>']
	list=[]
	for row in a:
		val=row
		if 'XXXX' in row:
			val=row.replace('XXXX',coord)
		list.append(val)
	return list

#creating end of actual kml file for placemarks
def end(folder):
	if folder=='':
		list=[]
		list.append('</Document>')
		list.append('</kml>')
	else:
		list=[]
		list.append('\t</Folder>')
		list.append('</Document>')
		list.append('</kml>')
	return list

#assembling placemark with given input data
#Name means given name for point
#scale given scale of icon
#data equal to given list of data see syntax above
#point means list with [lat,long] in string format
def placemark(name,scale,iconurl,data,point):
	p1=options(name,scale,iconurl)
	p2=dataforpoint(data)
	p3=endp(point)
	if not endp==', ':
		place=p1+p2+p3
	else:
		place=''
	return place

#tootl used for making datas with a given set of data and table ususally the header is the first row in the table
def makedatas(header,row):
	import itertools
	list=[]
	for a,b in itertools.izip(header,row):
		if '&' in str(b):
			b=b.replace('&','and')
		elif '&' in str(b):
			b=b.replace('&','and')
		list.append([a,b])
	return list

#appends a list of lines to a kml file
def parselist(list,location):
	f=open(location,'w')
	for row in list:
		f.writelines(row+'\n')
	f.close()
	print 'Kml file written to location: %s' % location

#yields a row from a list
def gen_row(list):
	for row in list:
		yield row




#from a row and a given header returns a point with a lat, elevation
def getlatlong(row,header):
	import itertools
	ind=0
	lat=''
	long=''
	for a,b in itertools.izip(row,header):
		if 'LAT' in str(b).upper():
			lat=str(a)
			ind=1
		elif 'LONG' in str(b).upper():
			long=str(a)
			ind=1
		#this querries and parses the data for a 'location' string in the value position (i.e. lat and long with syntax '(lat, long)' or 'lat, long')
		elif 'LOCATION' in str(b).upper() and ind==0:
			val=str.split(str(a),',')
			if '(' in str(a) and ')' in str(a) and len(val)>2:
				lat=str(val[0])
				lat=lat[1:]
				long=str(val[1])
				long=long[1:-1]
			else:
				if len(val)==2:
					lat=str(val[0])
					long=str(val[1])
					if long[0]==' ':
						long=long[1:]
				else:
					lat=0
					long=0
	return [lat,long]















#makes points for entire module 
#pointcsv file is your basecsvfile that all point data is stored on
def make_points(pointcsvfile,**kwargs):
	import numpy as np
	import pandas as pd
	import itertools
	if kwargs is not None:
		scale=1
		folder=''
		description=''
		indexs=[]
		icons=[]
		list=False
		icon='http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png'
		#setting kwargs if any are givne
		for key,value in kwargs.iteritems():
			if key=='scale':
				scale=float(value)
			elif key=='folder':
				folder=str(value)
			elif key=='description':
				description=str(value)
			elif key=='pointinfocsv':
				pointinfocsv=str(value)
			elif key=='indexs':
				indexs=value
			elif key=='icons':
				icons=value
			elif key=='icon':
				icon=value
			elif key=='list':
				list=value


		#making place holder indexs to iterate through
		#making an adjustment if a list is entered and not a csv file
		if list==False:
			points=read(pointcsvfile)
		else:
			if isinstance(pointcsvfile, pd.DataFrame):
				pointcsvfile=[pointcsvfile.columns.values.tolist()]+pointcsvfile.values.tolist()
			points=pointcsvfile
		header=points[0]
		if indexs==[]:
			newindexs=[]
			while not len(newindexs)==len(points[1:]):
				newindexs.append('')
			indexs=newindexs
		total=[]
		for pointrow,index in itertools.izip(points[1:],indexs):
			#if no input indexs are given
			if index=='':
				datas=makedatas(header,pointrow)
				point=getlatlong(pointrow,header)
				name=str(pointrow[0]) #generally identifying name for most objects is in first row
				mark=placemark(name,scale,icon,datas,point)
				total=total+mark
			else:
				for row in indexs:
					index=str(row)
					gener=gen_row(points[1:])
					genrow=''
					while not index in str(genrow): 
						genrow=next(gener)
					datas=makedatas(header,genrow)
					point=getlatlong(genrow,header)
					name=str(gen_row[0])
					mark=placemark(name,scale,icon,datas,point)
					if not mark=='':
						total=total+mark
		a=start('')
		b=total
		c=end('')
		list=''
		return a+b+c

#packages placemarks to make two files independent of one another.
def packagepoints(total):
	return total[4:-2]

#sfsfsdf
#given folder and description returns preceding rows to start said older
def startfolder(folder,description):
	return ['\t<Folder>','\t<name>'+folder+'</name>']+['\t<description>'+str(description)+'\t</description>']

#returns row to end folder.
def endfolder():
	return ['\t</Folder>']

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

#given folder and description returns preceding rows to start said older
def startfolder(folder,description):
	return ['\t<Folder>','\t<name>'+folder+'</name>']+['\t<description>'+str(description)+'\t</description>']

#returns row to end folder.
def endfolder():
	return ['\t</Folder>']
