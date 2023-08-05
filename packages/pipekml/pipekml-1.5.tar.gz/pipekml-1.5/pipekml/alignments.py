#Routing alignment kml maker
'''
Module: alignments.py 

Purpose: To parse csv files containing geospatial alignment data into a path with the data associated with that specific alignment into a KML file. 
(i.e. a simple csv file to alignment module)

What this module assumes you have or can produce quite easily:
	-A csv file with the alignment cordinates in either 2 points per row format or 1 point per row format
	-The points headers must contain the letters 'lat', 'long', or 'elev' (elevation not needed though)
	-All duplicate information in the rows will be assumed to be information one wants to carry into the routes data

Note: Due to the fact 'lat', 'long', or 'elev' may exist in a header that does not contain that data it may
pick up data that may not actually be point data to the header containing one of the above text. I may require 
more explicit headers (i.e. 'latitude','longitude', and 'elevation') later on.
	
List of functions within this module:
1) read(location)-reads csv and returns it as a list
2) **get_header()**-gets header for the locations that holds the segment attributes list 
3) **gen_segment()**-generator for segment id table generator nexts segment in list 
4) get_segment_info(objectid)-given an object id returns alist with each header value and then value associated with each header
5) simple_data(info)-takes a list of info with rows [headerval,segmentval] and returns block of simpledata to be inserted into kml
6) get_segment_info_block(objectid)-returns the block of rows that can be directly inserted into simple data blocks (combines 4 & 5 equations)
7) get_cords(objectid)-for a given objectid returns the block that goes into a kml file for the cordintes associated with it
8) get_start_block()-returns the start block of text 
9) get_placemark_settings_block(objectid,kwargs) eventually will be able to throw in color arguments and other alignment arguments
10) get3_block()-gets 2nd block of segment construction per segment
11) get4_block()-gets 3rd block of segment construction per segment
12) get5_block()-gets the final block of kml lines after the segment construction
13) make_route(segments,**kwargs)-input list of csv file paths in a list to corresponding kml file **see kwargs**
14) package_routes(list)-given newly exited list from make_route removes framing that makes it ready to be inserted into folder or with other kml structures
15) packagefinal(name,list)-given name of outer kml file and a list of kml folder/object structures returns kml lines ready to be written into file
16) folder(foldername,description,list)-given a name, a description and a list of kml object lines or subfolders wraps lines around inputted list for the desired folder.
17) parselist(list,location_name)-given list of kml lines ready to be parsed, and a file location of the file to be writtens name, writes file

created by Bennett Murphy
Github link: https://github.com/murphy214
'''

#1
#reads a csv file to memory 
def read(location):
	import csv
	List=[]
	f=csv.reader(open(location,'rb'),delimiter=',',quotechar="\"")
	for row in f:
		List.append(row)
	return List	

#2 **change this functions directory**
#returns header of the segment databases attributes
def get_header(csvfile,list):
	#checking to see if the kwarg condition of inputting a list is given if so will evuate the var csvfile as if it is the list
	if list==False:
		segment=read(csvfile)
	else:
		segment=csvfile

	header=segment[0]
	return header

#3 **change this functions directory**
#generator for the next value in a segment database
def gen_segment(csvfile,list):
	#checking to see if the kwarg condition of inputting a list is given if so will evuate the var csvfile as if it is the list
	if list==False:
		segment=read(csvfile)
	else:
		segment=csvfile

	for row in segment[1:]:
		yield row
#4	
#given a csv file and any unique identifier within a row will get data to be added in a format ready to go into akml
#assumes the field name will be the corresponding title int he first (i.e. the header row)
def get_segment_info(csvfile,uniqueindex,cordfile,list):
	#checking to see if the kwarg condition of inputting a list is given if so will evuate the var csvfile as if it is the list
	if list==False:
		segment=read(cordfile)
	else:
		segment=cordfile

	import itertools
	info=[]
	#getting segmentinfo if csv file is equal to '' and csvfile is equal to ''
	#this indictes that the segment info shouild be all likek values within the cordinate csv file
	if csvfile=='' and uniqueindex=='':
		header=segment[0]
		firstrow=segment[1]
		lastrow=segment[-1]

		for firstval,lastval,headerval in itertools.izip(firstrow,lastrow,header):
			if firstval==lastval:
				info.append([headerval,firstval])

	else:
		#setting up generators and getting header
		header=get_header(csvfile,list)
		next_row=gen_segment(csvfile,list)
		genuniqueindex=0
		
		#while statement that iterates through generator
		while not str(uniqueindex)==str(genuniqueindex):
			segmentrow=next(next_row)
			if str(uniqueindex) in segmentrow:
				for row in segmentrow:
					if str(row)==str(uniqueindex):
						genuniqueindex=str(row)
		
		#iterating through both header info and segment info to yield a list of both
		info=[]
		for headerval,segmentval in itertools.izip(header,segmentrow):
			info.append([headerval,segmentval])
		
	return info

#5	
#takes simple data input information i.e. a list with [headerval,segmentval] in each row and returns the block of simple_data rows taht need to be inserted into a kml file
def simple_data(info):
	simpledatarow='				<SimpleData name="XXX">YYY</SimpleData>'
	simpleblock=[]
	for row in info:
		xxx=row[0]
		yyy=row[1]
		newrow=simpledatarow.replace('XXX',xxx)
		newrow=newrow.replace('YYY',yyy)
		simpleblock.append(newrow)
	return simpleblock

#6	
#combines equation get_segment_info and simple_data to only return the values inserted into a kml file row assocatiated with simple data
def get_segment_info_block(csvinfofile,uniqueindex,cordfile,list):
	if list==True:
		segment=cordfile
	info=get_segment_info(csvinfofile,uniqueindex,cordfile,list)
	block=simple_data(info)
	return block

#7	
#insert file name to get cordinates from
#fault tolerant attempts to look at header in first row to get lat long structure within rows
def get_cords(csvfile,list):
	#checking to see if the kwarg condition of inputting a list is given if so will evuate the var csvfile as if it is the list
	if list==False:
		segment=read(csvfile)
	else:
		segment=csvfile
	cordblock=[]
	ind=0

	#getting header
	header=segment[0]

	#looking for lats, long and elevations within file
	#supports two points per line the most you would find for a path generally
	lats=[]
	longs=[]
	elevations=[]
	count=0
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
	if len(lats)==1 and len(longs)==1 and len(elevations)==0:
		count=0
		cordrows=[]
		#getting the row numbers the latitude and longitude occur in
		rowlat1=lats[0]
		rowlong1=longs[0]

		#getting point to point rows for a flat (1 point row) csv file
		for row in segment[1:]: 
			if count==0:
				point=[row[rowlat1],row[rowlong1]]
				count=1
				newrow=point
			elif count==1:
				point=[row[rowlat1],row[rowlong1]]
				count=0
				newrow=newrow+point
				cordrows.append(newrow)

		#now going back through new list to parseinto connection points
		for row in cordrows:
			lat1=str(row[0])
			long1=str(row[1])
			lat2=str(row[2])
			long2=str(row[3])

			#making kml ready row to be appended into kml
			newrow=long1+','+lat1+',0'+' '+long2+','+lat2+',0'
			cordblock.append(newrow)

	#FILETYPE OPTION: 1 LAT, 1 LONG, AND 1 ELEVATION
	elif len(lats)==1 and len(longs)==1 and len(elevations)==1:
		count=0
		cordrows=[]

		#getting the row numbers the latitude and longitude occur in
		rowlat1=lats[0]
		rowlong1=longs[0]
		rowele1=elevations[0]

		#getting point to point rows for a flat (1 point row) csv file
		for row in segment[1:]: 
			if count==0:
				point=[row[rowlat1],row[rowlong1],row[rowele1]] #lat,long,elevation
				count=1
				newrow=point
			elif count==1:
				point=[row[rowlat1],row[rowlong1],row[rowele1]] #lat,long,elevatioin
				count=0
				newrow=newrow+point
				cordrows.append(newrow)

		#now going back through new list to parseinto connection points
		for row in cordrows:
			lat1=str(row[0])
			long1=str(row[1])
			ele1=str(row[2])
			lat2=str(row[3])
			long2=str(row[4])
			ele2=str(row[5])

			newrow=long1+','+lat1+','+ele1+' '+long2+','+lat2+','+ele2
			cordblock.append(newrow)

	#FILETYPE OPTION: 2 LAT, 2 LONG, AND 0 ELEVATION
	elif len(lats)==2 and len(longs)==2 and len(elevations)==0:
		count=0
		cordrows=[]

		#geting the row numbers for the lats, longs, and elevations
		rowlat1=lats[0]
		rowlong1=longs[0]
		rowlat2=lats[1]
		rowlong2=longs[1]

		for row in segment[1:]:
			lat1=row[rowlat1]
			long1=row[rowlong2]
			lat2=row[rowlat2]
			long2=row[rowlong2]

			#assembling row that will go into kml file
			newrow=long1+','+lat1+',0'+' '+long2+','+lat2+',0'
			cordblock.append(newrow)

	#FILETYPE OPTION: 2 LAT, 2 LONG, AND 2 ELEVATIONS
	elif len(lats)==2 and len(longs)==2 and len(elevations)==2:
		count=0
		cordrows=[]

		#getting the row numbers for the lats,longs and elevations
		rowlat1=lats[0]
		rowlong1=longs[0]
		rowele1=elevations[0]
		rowlat2=lats[1]
		rowlong2=longs[1]
		rowele2=elevations[1]


		for row in segment[1:]:
			lat1=row[rowlat1]
			long1=row[rowlong1]
			ele1=row[rowele1]
			lat2=row[rowlat2]
			long2=row[rowlong2]
			ele2=row[rowele2]

			#making into rows that will go directly into kml
			newrow=long1+','+lat1+','+ele1+' '+long2+','+lat2+','+ele2
			cordblock.append(newrow)

	return cordblock



#8
#returns the block of text if the proper kwargs are not given in the get_start functions (i.e. a default get start)
def get_start_block(folder,description):
	template=['<?xml version="1.0" encoding="UTF-8"?>', '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">', '<Document>', '\t<name>Routed Path between Nodes</name>', '\t<open>1</open>', "\t<description>Via Python Scipt</description>"]
	if folder=='':
		template=['<?xml version="1.0" encoding="UTF-8"?>', '<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">', '<Document>', '\t<name>Routed Path between Nodes</name>', '\t<open>1</open>', "\t<description>Via Python Scipt</description>"]
	else:
		if description=='':
			template=template+['\t<Folder>','\t<name>'+folder+'</name>']
		else:
			template=template+['\t<Folder>','\t<name>'+folder+'</name>','\t<description>'+description+'</description>']
	return template

#9
#returns block of lines for kml pertaining to placemark settings
def get_placemark_settings_block(name,**kwargs):
	#tmeplate for placemark block of settings within kml
	template=['\t<Placemark>', '\t\t<name>XXX</name>', '\t\t<styleUrl>#style9</styleUrl>', '\t\t<Style id="inline">', '\t\t\t<IconStyle>', '\t\t\t\t<color>colorid</color>', '\t\t\t\t<colorMode>normal</colorMode>', '\t\t\t</IconStyle>', '\t\t\t<LineStyle>', '\t\t\t\t<color>colorid</color>', '\t\t\t\t<width>scaleid</width>\t\t\t\t', '\t\t\t\t<colorMode>normal</colorMode>', '\t\t\t</LineStyle>', '\t\t\t<PolyStyle>', '\t\t\t\t<color>ffececec</color>', '\t\t\t\t<colorMode>normal</colorMode>', '\t\t\t</PolyStyle>', '\t\t</Style>', '\t\t<ExtendedData>', '\t\t\t<SchemaData schemaUrl="#S_Export_Output_IDSDSSSSSDSSSDSDSSSSSDS">']
	
	#if no nameis input setting default name to alignment
	if name=='':
		name='Alignment'


	if kwargs is not None:
		scaleid=1
		for key,value in kwargs.iteritems():
			if key=='color':
				if value=='red':
					colorid='ff0a00fc'
				elif value=='orange':
					colorid='ff0177fc'
				elif value=='dark blue':
					colorid='ffff4010'
				elif value=='light green':
					colorid='ff06ff3b'
				elif value=='yellow':
					colorid='ff48ffff'
				elif value=='white':
					colorid='ffececec'
			if key=='scale':
				scaleid=str(value)
		block=[]
		for row in template:
			value=row
			if 'XXX' in value:
				value=value.replace('XXX',str(name))
			elif 'colorid' in value:
				value=value.replace('colorid',colorid)
			elif 'scaleid' in value:
				value=value.replace('scaleid',scaleid)
			block.append(value)
	else:
		block=[]
		for row in template:
			value=row
			if 'XXX' in value:
				value=value.replace('XXX',str(name))
			block.append(value)
	return block

#10
#returns the glue lines between start of placemark and cords
def get3_block():
	template=['\t\t\t</SchemaData>', '\t\t</ExtendedData>', '\t\t<gx:balloonVisibility>1</gx:balloonVisibility>', '\t\t<LineString>', '\t\t\t<coordinates>']
	return template
#11
#returns the glue lines betweeen cords and start a new placemark
def get4_block():
	template=['\t\t\t</coordinates>', '\t\t</LineString>', '\t</Placemark>']
	return template
#12
#returns the final two rows require to finish a kmls parsing
def get5_block(folder):
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

#13
#Given a list of csv file locations will ingest each and parse geometric data into kml along with its respective extended data
'''
Kwargs in format color-[options]:
	color-["white","red","orange","light green","yellow"]
	scale-Any integer I suggest 5 for alignment kmls (1 is default)
	folder-typer folder name here if you want to have a sub folder
'''
def make_route(cordfiles,**kwargs):
	import itertools
	if kwargs is not None:
		scale=1
		color='white'
		folder=''
		description=''
		seginfocsv=''
		indexs=[]
		list=False
		for key,value in kwargs.iteritems():
			if key=='scale':
				scale=value
			elif key=='color':
				color=value
			elif key=='folder':
				folder=value	
			elif key=='description':
				description=value
			elif key=='seginfocsv':
				seginfocsv=value
			elif key=='indexs':
				indexs=value
			elif key=='list':
				list=value

		part1=get_start_block(folder,description)
		part2=[]
		count=0


		if list==True: 
			datalist=cordfiles
			cordfiles=['Onelist']
		#takign care of an empty indexs list (assumes to use liek values in each file for segment info)
		if indexs==[] or seginfocsv=='':
			newindexs=[]
			while not len(newindexs)==len(cordfiles):
				newindexs.append('')

		#setting the size of indexs into size of each of segment files and passing into segment block info where it wont matter
		indexs=newindexs

		
		ind=0
		for uniqueindex,cordfile in itertools.izip(indexs,cordfiles):
			if list==True and ind==0:
				if isinstance(slicedtable, pd.DataFrame):
					seginfocsv=seginfocsv.values.tolist()

				ind=1
				name='Alignment'
				p1=get_placemark_settings_block(name,color=color,scale=scale) 
				p2=get_segment_info_block(seginfocsv,uniqueindex,datalist,list)
				p3=get3_block()
				p4=get_cords(datalist,list)
				p5=get4_block()
				segblock=p1+p2+p3+p4+p5
				part2=part2+segblock
			else:
				if '/' in str(cordfile):
					name=str.split(cordfile[:-4],'/')[-1]
				else:
					name=cordfile[:-4]
				p1=get_placemark_settings_block(name,color=color,scale=scale) 
				p2=get_segment_info_block(seginfocsv,uniqueindex,cordfile,list)
				p3=get3_block()
				p4=get_cords(cordfile,list)
				p5=get4_block()
				segblock=p1+p2+p3+p4+p5
				part2=part2+segblock
		part3=get5_block(folder)
		route=part1+part2+part3
	else:
		part1=get_start_block()
		part2=[]
		count=0
		for row in cordfiles:
			cordfile=row
			if '/' in str(cordfile):
				name=str.split(cordfile[:-4],'/')[-1]
			else:
				name=cordfile[:-4]
			p1=get_placemark_settings_block(uniqueindex) 
			p2=get_segment_info_block(list)
			p3=get3_block()
			p4=get_cords(cordfile)
			p5=get4_block()
			segblock=p1+p2+p3+p4+p5
			part2=part2+segblock
		part3=get5_block()
		route=part1+part2+part3
	return route

#13
#given the input startnode, endnode, and segments between will return list of lines to written to kml file
'''
Kwargs in format color-[options]:
	color-["white","red","orange","light green","yellow"]
	scale-Any integer I suggest 5 for alignment kmls (1 is default)
	folder-typer folder name here if you want to have a sub folder
'''

#given folder and description returns preceding rows to start said older
def startfolder(folder,description):
	return ['\t<Folder>','\t<name>'+folder+'</name>']+['\t<description>'+str(description)+'\t</description>']

#returns row to end folder.
def endfolder():
	return ['\t</Folder>']
#meant to package up the routes (i.e. grab the routes with just the folder)
def packageroutes(a):
	return a[6:-2]

#making frame around elements and subdirectories that will return a list ready to be exported into a kml file
def packagefinal(name,list):
	a=start(name)
	b=end('')
	final=a+list+b
	return final

#making folder to package elements list is the list of the element kml files
def folder(folder,description,list):
	a=startfolder(folder,description)
	b=endfolder()
	list=a+list+b
	return list

#appends a list of lines to a kml file
def parselist(list,location):
	f=open(location,'w')
	for row in list:
		f.writelines(row+'\n')
	f.close()
	print 'Kml file written to location: %s' % location
	
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

'''
TESTING
a=make_route(['test4_fusion_data.csv','test.csv','test2.csv'],color='light green',scale=5)
parse_list_tokml(a,'test.kml')

'''

