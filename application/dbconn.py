#importCSV function is not done yet


import sqlite3
import csv
import requests #for download function
import re #for string char filtering #res = "".join(re.split(",", row)) ---------neizmantoju patreiz
import ast #for string conversion to possible other types
from pathlib import Path
import string
import random
import os
import subprocess
import platform
from datetime import datetime
from datetime import timedelta
from application import customFunctions

class user(object):
	def __init__(self):
		#self.username = usernameInput
		self.username = self.randomName(6)
		self.conn = None
		self.cur = None
		self.databaseFolderPath = Path(__file__).parent / "databases/" #this is <class 'pathlib.WindowsPath'> object

	def createDB(self, name):
		databaseName = name + '.db'
		#check if database with this name exists
		#database is safe to check by its header, but had to remember that database is valid (exists) if it is not empty, if empty there will be no header info etc., BUT file by itself could exist (if empty)
		#https://www.sqlite.org/fileformat.html
		from os import listdir
		from os.path import isfile, join
		files = [f for f in listdir(self.databaseFolderPath) if isfile(join(self.databaseFolderPath, f))]
		print(files)
		for file in files:
			filePath = self.databaseFolderPath / file
			print(file)
			print(filePath)
			if file == databaseName:
				if isSQLite3(filePath):
					print('Active database with this name already exists! Skipping function ..')
					return False
			else: print('does not match')
		path = self.databaseFolderPath / databaseName
		conn = sqlite3.connect(path)
		conn.commit()
		conn.close()
		return True

	def connectToDB(self, dbName):
		databaseName = dbName + '.db'
		path = self.databaseFolderPath / databaseName
		self.conn = sqlite3.connect(path)
		self.cur = self.conn.cursor()

	def createTable(self, tableName, columnNames, datatypes, listType = True):
		#by default column names and datatypes are imported as lists
		#column descriptions must be imported as string and with "(", ")"

		columnNamesCorrected = []
		for loop in range(len(columnNames)):
			columnNameToApend = columnNames[loop]
			if columnNameToApend[(len(columnNameToApend)-2):] == '\r': columnNameToApend = columnNameToApend[:(len(columnNameToApend))]#šo vēl jāizskata vai ir nepieciešams
			if "'" in columnNameToApend:
				coreName = columnNameToApend.replace("'","")
				newName = "'" + coreName + "'"
				columnNamesCorrected.append(newName)
			else:
				newName = "'" + columnNameToApend + "'"
				columnNamesCorrected.append(newName)
			datatypes.append(datatypes[loop])

		if self.conn == None:
			print("you are not connected to database!")
			return
		if listType == True:
			#print('--------columnNamesCorrected---------->',columnNamesCorrected)
			columnDescriptions = '('
			for loop in range(len(columnNamesCorrected)):
				columnDescriptions += (' ' + columnNamesCorrected[loop] + ' ' + datatypes[loop] + ',')
			columnDescriptions = columnDescriptions[:-1]
			columnDescriptions += ')'
			stringsToJoin = ("CREATE TABLE ", tableName, " ", columnDescriptions)
			commandToExecute = "".join(stringsToJoin)
			print('----------->',commandToExecute)
			self.cur.execute(commandToExecute)
		#self.c.execute('''CREATE TABLE rsTrade (date date, item text, quantity integer, price1 integer, price2 integer, gainGP integer, gainMIL real)''')
		self.conn.commit()
		print("done!")

	def getTableInfo(self, nameOfTable):
		#https://stackoverflow.com/questions/11753871/getting-the-type-of-a-column-in-sqlite
		stringsToJoin = ("PRAGMA table_info(", nameOfTable, ")")
		commandToExecute = "".join(stringsToJoin)
		self.cur.execute(commandToExecute)
		rows = self.cur.fetchall()
		#print(rows)
		return rows
	def getDatabaseTables(self):
		# raw format recieved example: [('flaskloginUsers',), ('cc',)]
		self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
		tableListRaw = self.cur.fetchall()
		tableListExport = []
		for loop in range(len(tableListRaw)):
			tableListExport.append(tableListRaw[loop][0])
		return tableListExport
	def addColumn(self, nameOfTable, newColumnName, dataType):
		# get column name list
		stringsToJoin = ("select * from ", nameOfTable)
		commandToExecute = "".join(stringsToJoin)
		cursor = self.conn.execute(commandToExecute)
		names = [description[0] for description in cursor.description]
		#check if new colun name is not same as existing
		for columnName in names:
			if columnName == newColumnName:
				print('Column with this name already exists! Choose another name.')
				return
		stringsToJoin = ("ALTER TABLE ", nameOfTable, " ADD COLUMN ", newColumnName, " ", dataType)
		commandToExecute = "".join(stringsToJoin)
		self.conn.execute(commandToExecute)
		self.conn.commit()
	def renameColumn(self, nameOfTable, currentColumnName, newColumnName):
		stringsToJoin = ("ALTER TABLE ", nameOfTable, " RENAME COLUMN ", currentColumnName, " TO ", newColumnName)
		commandToExecute = "".join(stringsToJoin)
		self.conn.execute(commandToExecute)
		self.conn.commit()
	def removeColumn(self, nameOfTable, deletableColumnName):
		#in sqlite there are no function that support rename column, instead of that table must be recreated with modifications to it
		#at this moment funtion only copy names and data type of columns, there are 3 additional variables after datatype, if these would be needed, then dictionary must be created cause sqlite doesnt accept '0' whitch are there
		#get column descriptions in old table ------> info returned: (rowid, nameOfColumn, datatype, 0, None, 0) last three are unknown at the moment(0, None, 0), cant be feeded back straight forward
		stringsToJoin = ("PRAGMA table_info(rsTrade)")
		commandToExecute = "".join(stringsToJoin)
		self.cur.execute(commandToExecute)
		#rows = [description[0] for description in cursor.description]
		rows = self.cur.fetchall()
		# check if there are column with this name, if not then skip
		for loop in range(len(rows)):
			if rows[loop][1] == deletableColumnName: break
			if loop == (len(rows) - 1):
				print('table doesnt contain any column with this name')
				return False

		#get column descriptions but skipping the deleatable column
		newColumnDescriptions = ['( ',]
		for loop in range(len(rows)):
			columnDescription = rows[loop]
			if columnDescription[1] == deletableColumnName: continue #check if it is deletable column, then skip it
			columnDescriptionList = []
			for item in range(len(columnDescription)):
				if item == 0: continue
				elif item > 2: break
				if isinstance(columnDescription[item], str) == True: columnDescriptionList.append(columnDescription[item])
				else:
					stringToAppend = str(columnDescription[item])
					columnDescriptionList.append(stringToAppend)
				columnDescriptionList.append(' ')
			if loop == (len(rows) - 1): pass
			else: columnDescriptionList.append(', ')
			newColumnDescriptions.append("".join(columnDescriptionList))
		newColumnDescriptions.append(' )')
		columnDescriptions = "".join(newColumnDescriptions)

		newTableName = 'newTable'
		self.createTable(newTableName, columnDescriptions)

		#copy info from old table to new one
		columnsToCopy = []
		for column in rows:
			if column[1] == deletableColumnName: continue
			else:
				columnsToCopy.append(column[1])
				columnsToCopy.append(', ')
		columnsToCopy = columnsToCopy[:(len(columnsToCopy) -1)]
		columnsToCopy = "".join(columnsToCopy)
		stringsToJoin = ("INSERT INTO ", newTableName, ' (', columnsToCopy, ') SELECT ', columnsToCopy, ' FROM ', nameOfTable)
		commandToExecute = "".join(stringsToJoin)
		self.cur.execute(commandToExecute)
		self.conn.commit()
		#drop old table
		stringsToJoin = ("DROP TABLE ", nameOfTable)
		commandToExecute = "".join(stringsToJoin)
		self.cur.execute(commandToExecute)

		#rename new table to old table name
		stringsToJoin = ("ALTER TABLE ", newTableName, " RENAME TO ", nameOfTable)
		commandToExecute = "".join(stringsToJoin)
		self.cur.execute(commandToExecute)

		#just for check info can be removed later
		self.selectData(nameOfTable, selectAll = True)
		self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
		print(self.cur.fetchall())

		return True

	def insertData(self, nameOfTable, dataList, keysList):
		#dataList variable is list of values, these are unpacked and passed to command
		if self.conn == None:
			print("you are not connected to database!")
			return

		colNamesToExport = ""

		colNamesToExport += "("
		for loop in range(len(keysList)):
			colNamesToExport += "'"
			colNamesToExport += str(keysList[loop])
			colNamesToExport += "'"
			colNamesToExport += ","
		colNamesToExport = colNamesToExport[:-1] #remove last char
		colNamesToExport += ")"

		#get table info
		tableInfo = self.getTableInfo(nameOfTable)
		#print('-------------------tablInfo------------------->',tableInfo)
		#print('-------------------keysList------------------->',keysList)
		#assemble string for sqlite, table info is needed for datatypes, text items must be in: ''
		dataToExport = ""
		for loop in range(len(dataList)):
			#print('datalist data loop: ',loop,'  ', dataList[loop])
			#currentColData = [(tableInfo[loop]) for x in keysList[loop] for y in tableInfo if str(x) == str(y[1])]

			#find right column data, to know if '' had to be used
			currentColData = None
			for item in tableInfo:
				if item[1] == keysList[loop]: currentColData = item
			#print('----------------currentColData------------->',currentColData)
			if currentColData[2] == 'text' or currentColData[2] == 'STRING' or currentColData[2] == 'TEXT':
				quotes = "'"
				if quotes in dataList[loop]: dataList[loop] = dataList[loop].replace(quotes, "")
				dataToExport += "'"
				dataToExport += str(dataList[loop])
				dataToExport += "'"
				dataToExport += ","
			else:
				dataToExport += str(dataList[loop])
				dataToExport += ","
		dataToExport = dataToExport[:-1] #remove last char
		#print(dataToExport)
		stringsToJoin = ("INSERT INTO ", nameOfTable, " ", colNamesToExport , " VALUES (", dataToExport, " )")
		commandToExecute = "".join(stringsToJoin)
		#print(commandToExecute)
		self.cur.execute(commandToExecute)
		#print('line writtent to ', nameOfTable)
		#self.cur.execute("INSERT INTO rsTrade VALUES ('28.07.2019','Cannonballs',29999,471,496,749975,0.7499)")
		self.conn.commit()

	def updateData(self, nameOfTable, column1, column1_RecordToChange, column2_refference, column2_RecordAsReference):
		if self.conn == None:
			print("you are not connected to database!")
			return
		stringsToJoin = ("UPDATE ", nameOfTable, " SET ", column1, " = '", column1_RecordToChange, "' WHERE ", column2_refference, " = '", column2_RecordAsReference, "'")
		commandToExecute = "".join(stringsToJoin)
		print(commandToExecute)
		self.cur.execute(commandToExecute)
		self.conn.commit()

	def deleteRecords(self, nameOfTable, specificRecords = [], specificColumns = []):
		if specificRecords != None:
			tableNames = '('
			#print("---------specific columns----------->", specificColumns)
			for loop in range(len(specificRecords)):
				tableNames += specificColumns[loop] + " = " + "'" + specificRecords[loop] + "'" + ' or'
			tableNames = tableNames[:-2]
			tableNames += ')'
			stringsToJoin = ("DELETE FROM ", nameOfTable, " WHERE ", tableNames)
			commandToExecute = "".join(stringsToJoin)
			print(commandToExecute)
			self.cur.execute(commandToExecute)
			self.conn.commit()
		else:
			stringsToJoin = ("DELETE FROM ", nameOfTable)
			commandToExecute = "".join(stringsToJoin)
			self.cur.execute(commandToExecute)
			self.conn.commit()



	def selectData(self, nameOfTable, listColumnNames = [None], listSearchValues = [None], listOperators = [None], specificColumnsOnly = False, selectCustomFromAllColumns = False, selectDescending = False, recordsLimit = None, selectAll = False, printOnConsole = True):
	#example for specific: userConnected.selectData('rsTrade', ['item', 'quantity'], ['testEntry', 1], ['=', '>'])
	#or for all: userConnected.selectData('rsTrade', selectAll = True)
	#For selectAll - by default it return all data, but if recordsLimit is present it will constrain it
	#if selectAll == True: selectCustomFromAllColumns = False#just for override - if select all then ignore all other options
		if self.conn == None:
			print("you are not connected to database!")
			return
		#selectDescending
			#code here
		if selectAll == False and selectCustomFromAllColumns == False:
			if specificColumnsOnly == True:
				lenght = len(listColumnNames)
				columnNamesTuple = ()
				for loop in range(lenght):
					if loop != (lenght -1):
						columnNamesTuple += (listColumnNames[loop], ',')
					else:
						columnNamesTuple += (listColumnNames[loop],)

				#print(columnNamesTuple)
				stringsToJoin = ("SELECT", " ".join(columnNamesTuple), "FROM", nameOfTable)
				commandToExecute = " ".join(stringsToJoin)
				#can print command to see how it looks
				#print(commandToExecute)
				self.cur.execute(commandToExecute)
			else:
				if len(listColumnNames) != len(listSearchValues) or len(listColumnNames) != len(listOperators):
					print("value lists are not same lenght!")
					return
				#select specific
				lenght = len(listColumnNames)
				columnNamesTuple, columnNamesAndOperatorsTuple  = (), ()
				for loop in range(lenght):
					if loop != (lenght -1):
						columnNamesAndOperatorsTuple += (listColumnNames[loop],listOperators[loop], '?', 'AND',)
						columnNamesTuple += (listColumnNames[loop], ',')
					else:
						columnNamesAndOperatorsTuple += (listColumnNames[loop],listOperators[loop], '?',)
						columnNamesTuple += (listColumnNames[loop],)

				#print(columnNamesTuple)
				extraConstraints = ""
				if selectDescending == True or recordsLimit != None:
					extraConstraints = extraConstraints + "ORDER BY rowid "
					if selectDescending == True:
						extraConstraints = extraConstraints + "DESC "
					if recordsLimit != None:
						extraConstraints = extraConstraints + "LIMIT " + str(recordsLimit)
				stringsToJoin = ("SELECT", " ".join(columnNamesTuple), "FROM", nameOfTable, "WHERE", " ".join(columnNamesAndOperatorsTuple), extraConstraints)
				commandToExecute = " ".join(stringsToJoin)
				#print(commandToExecute)
				self.cur.execute(commandToExecute, listSearchValues)
		elif selectCustomFromAllColumns == True:
			if isinstance(listColumnNames[0], list):
				listColumnNames = listColumnNames[0]
			if isinstance(listOperators[0], list):
				listOperators = listOperators[0]
			if isinstance(listSearchValues[0], list):
				listSearchValues = listSearchValues[0]
			#print('im in function!!------------------')
			#print('listSearchValues--------------->', listSearchValues)
			tableInfo = self.getTableInfo(nameOfTable)#get table info    <<<-----------------------------------------------
			dataToExport = ""
			colNamesToExport = ""
			for loop in range(len(listSearchValues)):
				#find right column data, to know if '' had to be used
				currentColData = None
				if listColumnNames[loop] == 'rowid':
					currentColData = [" "," "," "]#just assign something as we want just to skip text part and to not cause error of NONE type
				else:
					for item in tableInfo:
						if item[1] == listColumnNames[loop]:
							currentColData = item
							break
					if currentColData == None: currentColData = [" "," "," "]

				if currentColData[2] == 'text':
					dataToExport += "'"
					dataToExport += str(listSearchValues[loop])
					dataToExport += "'"
					dataToExport += ","
				else:
					dataToExport += str(listSearchValues[loop])
					dataToExport += ","
				dataToSearch = dataToExport[:-1] #remove last char

			lenght = len(listColumnNames)
			columnNamesTuple, columnNamesAndOperatorsTuple  = (), ()
			#print('---------------->',listColumnNames)
			for loop in range(lenght):
				if loop != (lenght -1):
					columnNamesAndOperatorsTuple += ('"' + listColumnNames[loop] + '"',listOperators[loop], '?', 'AND',)
				else:
					columnNamesAndOperatorsTuple += ('"' + listColumnNames[loop] + '"',listOperators[loop], '?',)

			#print(columnNamesTuple)
			#stringsToJoin = ("SELECT * FROM", nameOfTable, "WHERE", " ".join(columnNamesAndOperatorsTuple))
			extraConstraints = ""
			if selectDescending == True or recordsLimit != None:
				extraConstraints = extraConstraints + "ORDER BY rowid "
				if selectDescending == True:
					extraConstraints = extraConstraints + "DESC "
				if recordsLimit != None:
					extraConstraints = extraConstraints + "LIMIT " + str(recordsLimit)
			stringsToJoin = ("SELECT * FROM", nameOfTable, "WHERE", " ".join(columnNamesAndOperatorsTuple), extraConstraints)


			commandToExecute = " ".join(stringsToJoin)
			#can print command to see how it looks
			#print(commandToExecute)
			self.cur.execute(commandToExecute, listSearchValues)
		else:
			#select all
			extraConstraints = ""
			if selectDescending == True or recordsLimit != None:
				extraConstraints = extraConstraints + "ORDER BY rowid "
				if selectDescending == True:
					extraConstraints = extraConstraints + "DESC "
				if recordsLimit != None:
					extraConstraints = extraConstraints + "LIMIT " + str(recordsLimit)
			stringsToJoin = ("SELECT *", "FROM", nameOfTable, extraConstraints)
			commandToExecute =  " ".join(stringsToJoin)
			self.cur.execute(commandToExecute)
		rows = self.cur.fetchall()
		rowsForReturn = rows
		if printOnConsole == True:
			if len(rows) == 0: print('no data was selected')
			else:
				for row in rows:
					print(row)
		return rowsForReturn

	def importCSV(self, pathToCSV, nameOfTable):
		csvHasColumnHeaders = False
		numberOfColumns = None
		overlapUntil = 0 #overlap value is value which holds number of lines where info is overlaping
		if self.conn == None:
			print("you are not connected to database!")
			return

		#read data
		csvReader = csv.reader(open(pathToCSV), delimiter=',', quotechar='"')

		#get numberOfColumns from csv file
		rowsForcolumns = csvReader
		for row in rowsForcolumns:
			numberOfColumns = len(row)
			break
		#-------------------------------------> must ad column comparison by count cause csv could have more ore less columns than expected
		#-------------------------------------> or ad additional function variables:
		#																		boolean for if it have exact number of columns in right order
		#																		dictionary for columns to show which columns need to be imported in specific columns

		#check if csv has headers
		sniffer = csv.Sniffer()
		sample_bytes = 2048
		csvHasColumnHeaders = sniffer.has_header(open(pathToCSV).read(sample_bytes))

		#read current data
		tableData = self.selectData(nameOfTable, selectAll = True, printOnConsole = False)
		#check if data are not same, but the data must be with condition - from older to younger, in for loop func. check in which row data is not overlaping any more

		#read data
		csvReader = csv.reader(open(pathToCSV), delimiter=',', quotechar='"')
		#convert to list
		currentData = []
		firstRow = True
		for loop in csvReader:
			if firstRow == True:
				firstRow = False
			else: currentData.append(loop)

		found = False
		if len(tableData) == 0:#if table is empty then skip check part
			found = True
		#print('table data len: ', len(tableData))
		#print('current data len', len(currentData))
		for importRow in range(len(currentData)):
			for tableRow in range(len(tableData)):
				if ''.join([str(item) for item in tableData[tableRow] ]) == ''.join(currentData[importRow]):
					print('sakrit')#table data converted to string and compared to inport data string
					if importRow == (len(currentData)-1): #check if not end of list
						print('table has no new data, so no new records was added')
						return
					break
				if tableRow == (len(tableData)-1): found = True
			if found == True: break
			overlapUntil += 1

		print('start from: ', overlapUntil)
		#-------------> japabeidz funkcija - columns to import must be created with variable

		#there starts data importation part
		valuesString = (("?,"),) * numberOfColumns
		valuesString = " ".join(valuesString)
		valuesString = valuesString[:(len(valuesString)-1)]# <--- remove last comma
		valuesString = " ".join(valuesString)
		#"stringsToJoin" - string for command to execute in sqlite3 ----> example with full string: "insert into nameOfTable (date, item, quantity, price1, price2, gainGP, gainMIL) values (?, ?, ?, ?, ?, ?, ?)"
		stringsToJoin = ("insert into", nameOfTable, "(date, item, quantity, price1, price2, gainGP, gainMIL)", "values", "(", valuesString, ")")
		commandToExecute = " ".join(stringsToJoin)
		#print(commandToExecute)
		csvReader = csv.reader(open(pathToCSV), delimiter=',', quotechar='"')
		firstRow = True
		rowsToSkip = 0
		for row in csvReader:
			#check if first row is headers, if yes then skip it and set "firstRow" flag to False
			if firstRow == True and csvHasColumnHeaders == True:
				firstRow = False
				continue
			else:
				if rowsToSkip < overlapUntil:
					rowsToSkip += 1
				else:
					try:
						self.conn.execute(commandToExecute, row)
					except Error as e:
						print(e)
						return
		#cur = self.conn.cursor()
		#cur.execute('select * from rsTrade')
		#print(cur.fetchall())
		self.conn.commit()

	def updateTableUniqueRecords(self, nameOfTable, dataList, reportUpdateCount = False, specificKeyList = None):
		#  - if 'reportUpdateCount' option is true then return how much rows are written
		#  - 'specificKeyList' is ment for cases when column order is not same as in database
		#this function check how many records from begining of list are unique - are not present in current table, then this number is used to shrink orginal recieved data list
		#after that records are uploaded to table
		#Counting is performed until first line with same data is detected
	
		tableInfo = self.getTableInfo(nameOfTable)#get table info
		#print("-------------------------------------tableInfo---->",tableInfo)
		keyList = [None] * len(tableInfo)
		for loop in range(len(tableInfo)):
			keyList[loop] = tableInfo[loop][1]
		#print("-----------------------------------------keyList--->",keyList)
		dataToUpload = 0
		for rowData in dataList:#in this loop check for first row whitch is not found in database
			if specificKeyList != None:
				dbData = self.selectData(nameOfTable, listColumnNames = [specificKeyList], listSearchValues = [rowData], listOperators = ['='] * len(specificKeyList), printOnConsole = False, selectCustomFromAllColumns = True)
			else:
				dbData = self.selectData(nameOfTable, listColumnNames = [keyList], listSearchValues = [rowData], listOperators = ['='] * len(keyList), printOnConsole = False, selectCustomFromAllColumns = True)
			if not dbData:
				dataToUpload += 1
			else: break
		dataToInsert = dataList[:dataToUpload]

		#counter = 1
		if len(dataToInsert) < 1:
			if reportUpdateCount == True:
				return False, dataToUpload
			else:
				return False
		else:
			for rowData in dataToInsert:
				if specificKeyList != None:
					self.insertData(nameOfTable, rowData, specificKeyList)
				else:
					self.insertData(nameOfTable, rowData, keyList)
				#print(counter)
				#counter += 1
				#print('--------------INSERTING---------------')
			if reportUpdateCount == True:
				return True, dataToUpload
			else:
				return True
	def randomName(self, letterCount):
		#this function requests imported libraries: string, random
		#name returned is in: ''
		name = "'"
		for loop in range(letterCount):
			name += random.choice(string.ascii_letters)
		name += "'"
		return name
	def countAllRecords(self, nameOfTable, operator = '', value = None):
		self.cur.execute('SELECT COUNT(*) FROM ' + str(nameOfTable) +';')
		countRaw = self.cur.fetchall()
		if operator == '-':
			startedFromRow = countRaw[0][0] - value
			return startedFromRow
		return countRaw[0][0]


def downloadCSV(url):
	#this function download csv and seperate headers if such are there
	rawData = []

	extractedIP = url.replace('https://', "")#remove set of char's before ip
	frstForwSlashID = extractedIP.index('/')
	extractedIP = extractedIP[:frstForwSlashID]#remove char's after ip
	workingDirectory = './application/wgetFile' #directory where to execute
	wgetExe = 'wget.exe'
	argument1 = '--no-check-certificate'
	argument2 = '-t1'
	argument3 = '--referer=https://' + extractedIP + '/Portal/Portal.mwsl?PriNav=FileBrowser'

	#-------------check for additional csv files in directory and create new unique name----------------------------------------
	randIdentificator = ""
	csvFileList = []
	for file in os.listdir(workingDirectory):
		if file.endswith(".csv"):
			csvFileList.append(file)
	if len(csvFileList) > 0:
		while True:
			#create potential name
			potentialName = 'DataLog_'
			randIdentificatorPotential = ""
			for loop in range(4):
				randIdentificatorPotential += random.choice(string.ascii_letters)
			potentialName += randIdentificatorPotential
			potentialName += '.csv'
			nameIsSame = False #by default flag is false
			for name in csvFileList:
				if name == potentialName:
					nameIsSame = True
					break
			if nameIsSame == False:
				randIdentificator = randIdentificatorPotential
				break
	else:
		for loop in range(4):
				randIdentificator += random.choice(string.ascii_letters)
	outputName = 'DataLog_' + randIdentificator + '.csv'
	#print('--------------->output name: ', outputName)
	#--------------------------------------------------------------Download file--------------------------------------------------------------------------
	#executed command should be as follows:
	#wget.exe --no-check-certificate -t1 --referer=http://192.168.0.7/Portal/Portal.mwsl?PriNav=FileBrowser https://192.168.0.7/FileBrowser/Download?Path=%2FDataLogs%2FpH_lvl_logg.csv
	#every argument seperated by space should be given seperately for supbrocess.run() function
	if platform.system() == 'Windows':
		subprocess.run([wgetExe, argument1, argument2, argument3, url, '-O', outputName], cwd=workingDirectory, shell=True)
	elif platform.system() == 'Linux':
		subprocess.run(['wget', argument1, argument2, argument3, url, '-O', outputName], cwd=workingDirectory)
		
		#subprocess.Popen(['wget', url])
		#print('---------------This is Linux!!!!!!!!!!!!!')
		#return
	else: print('---------------> something went wrong with Operating system detection <--------------')
	#-------------------------------------------------------Open, read and delete file -------------------------------------------------------------------
	#print('-------------------------------->',os.getcwd())
	pathToCSV = workingDirectory + "/" + outputName
	rawData = []
	with open(pathToCSV) as f:# cvs reader object must be created inside with statement to succesfully delete the file after it
		csvReader = csv.reader(f, delimiter=',', quotechar='"')
		for loop in csvReader:
			rawData.append(loop)
	#csvReader = csv.reader(open(pathToCSV), delimiter=',', quotechar='"')
	if os.path.exists(pathToCSV):#remove file
		os.remove(pathToCSV)

	#with requests.get(url, stream=True) as r:
	#	lines = (line.decode('windows-1252') for line in r.iter_lines())
	#	for row in csv.reader(lines):
	#		rawData.append(row)
	#-----------------------------------------------------clear data from white spaces------------------------------------------------------------------------------
	clearedData = []
	for row in rawData:
		rowValues = []
		for cell in row:
			rowValues.append(cell.strip())
		clearedData.append(rowValues)

	#-----------------------------------------------------------------check if data has column names-------------------------------------------------------------------
	if not clearedData:#check if list is empty
		return None,None
	frstLine = clearedData[0]
	scndLine = clearedData[1]

	tableData = None
	columnNames = None
	#check if first line is colnames
	for loop in range(len(clearedData[0])):
		#filter could be updated with date filtering e.c
		if frstLine[loop][0] == '-' and frstLine[loop][1:].isnumeric() == True:	#check if int
			if scndLine[loop][0] == '-' and scndLine[loop][1:].isnumeric() == True:
				continue#just continue to test other columns
		elif frstLine[loop].isnumeric() and scndLine[loop].isnumeric():
			continue#continue to test other columns
		elif frstLine[loop].replace('.','',1).isdigit() and scndLine[loop].replace('.','',1).isdigit():#check if float
			continue#data same continue
		else:#lines are not same type - first is column names, assign data and brake out of loop, cause other columns doesnt matter
			tableData = clearedData[1:]
			#columnNames = rawData[0]
			columnNames = frstLine
			break
		if loop == (len(clearedData[0])-1):#if all column names are same then assign all data to table data
			tableData = clearedData
		#tableData always will have data, columnNames will have '' text if there is no headers present

	#print(tableData)
	#return "", ""
	return tableData, columnNames



#----------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------!!! Don't call this function - it is infinite loop function for auto update as a paralel process !!! -------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------
# 2021-04-09 22:11:54.579366
# 2021-03-09 20:11:54.579366
from time import sleep
def autoUpdateDatabases():
	randIdentificator = ''
	for loop in range(4):
				randIdentificator += random.choice(string.ascii_letters)
	timeNow = str(datetime.now())
	first_timeRaw = timeNow[:10] + ' 06:00:00.579366'#data will be updated at 22:00
	
	#first_timeRaw = timeNow + timedelta(seconds=10) #for testing, to set update after 10s
	#first_time = datetime.now() + timedelta(seconds=10) #for testing  

	first_timeRaw = datetime.strptime(str(first_timeRaw), '%Y-%m-%d %H:%M:%S.%f')#convert string to datetime object
	first_time = first_timeRaw - timedelta(days=1)
	#checkAllUserDatabases()#---<<-------izdzest so pec tam
	print('--------Starting autoUpdateDatabases paralel process -----------')
	while True:
		#print('-------PAralel process------', randIdentificator) 0				1
		if customFunctions.compareTimeDifference(first_time, timePeriodSeconds = 0, timePeriodDays = 1) == True:
			print('-----------Performing auto update----------------')
			#perform update and reset timer
			checkAllUserDatabases()
			timeNow = str(datetime.now())
			first_timeRaw = timeNow[:10] + ' 22:00:00.579366'
			first_timeRaw = datetime.strptime(str(first_timeRaw), '%Y-%m-%d %H:%M:%S.%f')#convert string to datetime object
			first_time = first_timeRaw
			#first_time = datetime.now() + timedelta(seconds=10) #for testing
		sleep(2)
#----------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------------------------

#--------------------This function is to launch "autoUpdateDatabases" -----------------------------------------------------
def paralelAutoUpdateProcess():
        import multiprocessing
        new_process = multiprocessing.Process(target=autoUpdateDatabases)
        new_process.daemon=True
        new_process.start()
#--------------------------------------------------------------------------------------------------------------------------



def checkAllUserDatabases():
	columnNames = ['username','database']
	userConnected = user()
	#print("username------------>",userConnected.username)
	userConnected.connectToDB('userList')
	databaseData = userConnected.selectData('flaskloginUsers', listColumnNames = columnNames, specificColumnsOnly = True, printOnConsole = False)
	for row in databaseData:
		username = row[0]
		usrDBname = row[1]
		if usrDBname == None: continue#if there is no db attached then skip this user
		userConnected.connectToDB(usrDBname)
		databaseTables = userConnected.getDatabaseTables()
		if 'usrUrl' in databaseTables:
			databaseData_usrUrl = userConnected.selectData('usrUrl', listColumnNames = ['tableName','webUrl'], specificColumnsOnly = True, printOnConsole = False)
			if len(databaseData_usrUrl) < 0: continue#if no url is attached for tables then skip
			print(username, usrDBname)
			#---------perform update for all registered tables--------------
			# ---------------->>-seit iespejams vajag noteikt vai download nefeilo un tada gadijuma pie recordiem norada kura tabula nav updeitojusies--<<<<---
			for tableUrlRaw in databaseData_usrUrl:
				table = tableUrlRaw[0]
				url = tableUrlRaw[1]
				print(print(table, url))
				currentTableData, currentTableNames = downloadCSV(url)
				if currentTableData == None:
					#print('------Download has failed-----',usrDBname, table )
					addRecordToActionLogDB('--Auto update--', '--Download has failed--', usrDBname, table)
					continue
				#change date format from /%m/%Y to %Y-%m-%d 
				newValueListExport = customFunctions.changeDateFormat(currentTableData)
				isUpdated, updateCount = userConnected.updateTableUniqueRecords(table, newValueListExport,  reportUpdateCount = True)#perform data update
				if isUpdated == True:
					userConnected.countAllRecords(table, operator = '-', value = updateCount)
					report = 'Add ' + str(updateCount) + ' records. ' + 'Starting from rowid > ' + str(userConnected.countAllRecords(table, operator = '-', value = updateCount))
					addRecordToActionLogDB('--Auto update--', report, usrDBname, table)
					print(('------> Data updated!'))
				else: print('------> Data is up to date already!')
			#addRecordToActionLogDB(currentUserInput, currentActionInput, usrDBname, interactedTable)

		else:
			report = "Database does not have ->usrUrl<- table!"
			addRecordToActionLogDB('--WARNING!--', report, usrDBname, '--WARNING!--')
			continue
	userConnected.conn.close()#close sqlite connection

#--------------------This function is to launch "updateUserTables" as seperate process and not block main app--------------
def paralelUpdate(usrDBname):
	import multiprocessing
	new_process = multiprocessing.Process(target=updateUserTables, args=(usrDBname,))
	new_process.daemon=True
	new_process.start()
#--------------------------------------------------------------------------------------------------------------------------


def updateUserTables(usrDBname):
	print('---------------Login table update-------------------------------------')
	userConnected = user()
	userConnected.connectToDB(usrDBname)
	databaseTables = userConnected.getDatabaseTables()
	if 'usrUrl' in databaseTables:
		databaseData_usrUrl = userConnected.selectData('usrUrl', listColumnNames = ['tableName','webUrl'], specificColumnsOnly = True, printOnConsole = False)
		if len(databaseData_usrUrl) < 0: return#if no url is attached for tables then skip
		#---------perform update for all registered tables--------------
		# ---------------->>-seit iespejams vajag noteikt vai download nefeilo un tada gadijuma pie recordiem norada kura tabula nav updeitojusies--<<<<---
		for tableUrlRaw in databaseData_usrUrl:
			table = tableUrlRaw[0]
			url = tableUrlRaw[1]
			print(print(table, url))
			currentTableData, currentTableNames = downloadCSV(url)
			if currentTableData == None:
				#print('------Download has failed-----',usrDBname, table )
				addRecordToActionLogDB('--Auto update--', '--Download has failed--', usrDBname, table)
				continue
			#change date format from /%m/%Y to %Y-%m-%d 
			newValueListExport = customFunctions.changeDateFormat(currentTableData)
			isUpdated, updateCount = userConnected.updateTableUniqueRecords(table, newValueListExport,  reportUpdateCount = True)#perform data update
			if isUpdated == True:
				userConnected.countAllRecords(table, operator = '-', value = updateCount)
				report = 'Add ' + str(updateCount) + ' records. ' + 'Starting from rowid > ' + str(userConnected.countAllRecords(table, operator = '-', value = updateCount))
				addRecordToActionLogDB('--Auto update--', report, usrDBname, table)
				print(('------> Data updated!'))
			else: print('------> Data is up to date already!')

def addRecordToActionLogDB(currentUserInput, currentActionInput, interactedDatabase, interactedTable):
	#currentAction = "'" + "Add " + str(recordUploadCount) + " records. Starting from rowid > " + str(startedFromRow) + "'"
	userConnected = user()
	userConnected.connectToDB('actionLog')
	keyList = ['date','username','isAdmin','databaseName','tableName','action']
	currentUser = "'" + str(currentUserInput) + "'"
	currentAction = "'" + str(currentActionInput)  + "'"
	date = "'" + str(datetime.now()) + "'"
	databaseExport = "'" + str(interactedDatabase) + "'"
	tableExport = "'" + interactedTable + "'"
	valueList = [date,currentUser,1,databaseExport,tableExport,currentAction]
	userConnected.insertData('userActions',valueList,keyList)
	userConnected.conn.close()#close sqlite connection


def createUser(dbName, nameOfTable, userDataList):
	conn = sqlite3.connect(rsinfo.db)
	c = conn.cursor()
	nameOfTable = 'userInfo'
	#----------------- funkcija jāpabeidz (nočekot vai user jau nav reģistrēts; info ievietošana string no list variable)
	valuesString = 'testuser, password, yes, testUserTable1'
	stringsToJoin = ("insert into", nameOfTable, "(username, pasword, license, userTables)", "values", "(", valuesString, ")")
	commandToExecute = " ".join(stringsToJoin)
	c.execute(commandToExecute)
	conn.commit()
	print('hello')

def downloadFile(url):
	try:
		#url = 'https://fv9-2.failiem.lv/down.php?i=kfvhttsn&n=testCSV.csv'
		r = requests.get(url)
		#print(r.content)
		#with open('/Users/Martins/Downloads/downloadedTestCSV.csv', 'wb') as f:
		with open('./downloads/downloadedTestCSV.csv', 'wb') as f:
			f.write(r.content)
		print('download done')
	except Error as e:
		print(e)
		return
# functions to donload from google drive, these need "request" module
def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

def isSQLite3(filename):
	from os.path import isfile, getsize

	if not isfile(filename):
		return False
	if getsize(filename) < 100: # SQLite database file header is 100 bytes
		return False

	with open(filename, 'rb') as fd:
		header = fd.read(100)
	#print('------->  ', header[:16])
	return header[:16] == b'SQLite format 3\x00'
