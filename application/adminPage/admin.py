from flask import Blueprint, render_template, request, jsonify
from flask import current_app as app

from ..forms import LoginForm

from flask import request, make_response
from datetime import datetime
from ..models import db, User

from flask import redirect, url_for
from flask_login import current_user, login_required

from .. import dbconn
from .. import customFunctions

import os

import datetime

#---------------- config data-------------------------------------
import sys
sys.path.append("...")
from config import tablesToFilterWholeName
from config import tablesToFilterPartialName

selectedUserData = None

admin_bp = Blueprint(
    'admin_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@admin_bp.route('/admin', methods=['GET'])
@login_required
def admin():
	"""Records list"""
	if current_user.isAdmin == False:
		return render_template('notAdmin.html')
	

	return render_template(
		'adminHome.html'
    )
	
@admin_bp.route('/manageUsers', methods=['GET','POST'])
@login_required
def manageUsers():
	"""Records list"""
	if current_user.isAdmin == False:
		return render_template('notAdmin.html')
		#userConnected = dbconn.user('tester')
	
	#request collumns to send to browser
	columnNames = ['id','username','email','name','isActive','created','lastLogin','database']
	userConnected = dbconn.user()
	#print("username------------>",userConnected.username)
	userConnected.connectToDB('userList')
	databaseData = userConnected.selectData('flaskloginUsers', listColumnNames = columnNames, specificColumnsOnly = True, printOnConsole = False)
	data = [loop[1] for loop in databaseData]
	info = customFunctions.unique(data)
	userConnected.conn.close()
	
	dataExport = []
	loopNr = 1
	for row in databaseData:
		cellsDict = {name:cell for (cell,name) in zip(row,columnNames)}
		loopNr += 1
		dataExport.append(cellsDict)
	
	columnNamesWithoutSpaces = []
	for word in columnNames:
		columnNamesWithoutSpaces.append(word.replace(" ",""))
	colNamesExport = []
	for (titleName,fieldName) in zip(columnNames,columnNamesWithoutSpaces):
		colNamesExport.append({'title':titleName, 'field':fieldName})
	userConnected.conn.close()#close sqlite connection
	if request.method == "POST":
		v = request.get_json()
		if v != None:#check if not None - this is case when page loads it somehow triger POST event once
			if len(v) != 0:#check if is not empty list - this would be case if user is not selected a row
				#print("------------->recieve row info at /editUser function<-------------")
				#print(v)
				#print(type(v[0]))#liste kas sast??v no dictionary elementiem
				global selectedUserData
				selectedUserData = v[0]
				#print('selected data is: ', selectedUserData)
				return render_template(
					'editUser.html'
				)
	#textColIndex = [1]
	#usrLang = current_user.language
	#userConnected.connectToDB('lang')
	#texts = userConnected.selectData('texts', listColumnNames = textColIndex, listSearchValues = [usrLang], listOperators =['='], specificColumnsOnly = True)
	#print('-------------------------->recieved texts from data base: ', texts)
	return render_template(
		'manageUsers.html', tableData = dataExport, colNamesExport = colNamesExport, username = current_user.username
    )
	
@admin_bp.route('/editUser', methods=['GET','POST'])
@login_required
def editUser():
	if current_user.isAdmin == False:
		return render_template('notAdmin.html')
	username = request.args.get('username')
	if username == None:
		return ('', 204)#HTTP 'empty response
	userToEdit = User.query.filter_by(username=username).first()
	databaseTables = None
	tableDataUrl = [None] * 2
	
	if userToEdit.database != None:
		userConnected = dbconn.user()
		userConnected.connectToDB(userToEdit.database)
		databaseTables = userConnected.getDatabaseTables()
		databaseTables.remove('usrUrl')#remove from list as we dont want to interct with this table, this is static table where save table url sites
		#databaseTables = customFunctions.filterIfContain(databaseTables,'_graphics')
		
		#get count of records for log file before they are updated
		userConnected.cur.execute('SELECT COUNT(*) FROM usrUrl;')
		countRaw = userConnected.cur.fetchall()
		#print(countRaw)
		#print('-------------->overall count is: ', countRaw[0][0])
		tableDataUrl[0] = countRaw[0][0]
		tableDataUrl[1] = len(databaseTables)
		
		selectedData = userConnected.selectData('usrUrl', selectAll = True, printOnConsole = False)
		urlDataExport = []
		for item in selectedData:
			urlDataExport.append({'tableName':item[0], 'webUrl':item[1]})
		userConnected.conn.close()#close sqlite connection
	return render_template(
			'editUser.html',
			#data = selectedUserData,
			username = userToEdit.username,#user to edit username
			usernameAdmin = current_user.username,#admin who edit username
			database = userToEdit.database,
			created = userToEdit.created,
			lastLogin = userToEdit.lastLogin,
			databaseTables = databaseTables,
			tableDataUrl = tableDataUrl,
			urlDataExport = urlDataExport
		)
@app.route("/editUserCreateTable", methods=['GET','POST'])
def createTable():

	recievedData = request.get_json()
	#retrieve table name, cause it is last added value and delete it from list
	tableName = recievedData[(len(recievedData)-1)]
	recievedData.pop()
	#retrieve username and delete it from list
	username = recievedData[(len(recievedData)-1)]
	recievedData.pop()
	userToEdit = User.query.filter_by(username=username).first()
	database = userToEdit.database
	
	userConnected = dbconn.user()
	userConnected.connectToDB(database)
	tables = userConnected.getDatabaseTables()
	#check if new table name is not same with existing
	for currTable in tables:
		if currTable == tableName:
			return jsonify({
			"info"   :  "Table with this name already exists!",
			})
	if any(item == tableName for item in tablesToFilterWholeName) or any(item in tableName for item in tablesToFilterPartialName):
		phrases = ', '.join(tablesToFilterPartialName)
		tableNames = ', '.join(tablesToFilterWholeName)
		reportString = "Table name can not have following phrases: (" + phrases + ") or whole names: (" + tableNames + ")"
		return jsonify({
		"info"   :  reportString,
		})
	#generate two lists - column names and datatypes to pass to createTable function
	columnNames = [item['columnName'] for item in recievedData]
	datatypes = [item['datatype'] for item in recievedData]
	
	#print('--------columnNames_admin------>',columnNames)
	
	userConnected.createTable(tableName, columnNames, datatypes, listType = True)
	#-----------------------------------------------Create headers table------------------------------------------------------------------------
	headerTableName = tableName + '_headers'
	newDataTypes = ["TEXT" for item in datatypes]
	userConnected.createTable(headerTableName, columnNames, newDataTypes, listType = True)
	#userConnected.cur.execute(commandToExecute)
	#------------------------------------------------Create pdf text table ---------------------------------------------------------------------
	TextTableName = tableName + '_texts'
	IdNrList = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43] #0 iet virsrakst?? un faila nosaukum?? cikla nr. #30 vai grafiku vajag true/false #31 grafika lielums #32 grafika lieluma mervieniba
	IdNrListStr = [str(item) for item in IdNrList]
	newDataTypes2 = ["TEXT" for item in IdNrListStr]
	userConnected.createTable(TextTableName, IdNrListStr, newDataTypes2, listType = True)
	#-----------------------------------------------Create graphics table------------------------------------------------------------------------
	#CREATE TABLE  test_graphics( id INTEGER PRIMARY KEY,username STRING UNIQUE NOT NULL);
	graphTableName = tableName + '_graphics'
	commandToExecute = "CREATE TABLE " + graphTableName + " (Record INTEGER, Date STRING, 'UTC Time' STRING, '' INTEGER)"
	userConnected.cur.execute(commandToExecute)
	#---------------------------------------------------------add record to actionLog.db--------------------------------------------------------------------
	currentActionInput = " Created new table with name:  " + tableName
	dbconn.addRecordToActionLogDB(current_user.username, currentActionInput, userToEdit.database, "-newTable-")
	
	
	userConnected.conn.close()#close sqlite connection

	return jsonify({
		"info"   :  "Table created succesfully",
		})

@app.route("/editUserRequestInfo", methods=['GET','POST'])
def returnData():
	#data = request.get_json()
	username = request.args.get('username')#username to identify database
	table = request.args.get('table')
	recordAmount = request.args.get('recordAmount')
	#print('username: ',username)
	#print('table: ',table)
	#print('recordAmount: ',recordAmount)
	#print('record amount ----------->', recordAmount)
	userToEdit = User.query.filter_by(username=username).first()
	userConnected = dbconn.user()
	userConnected.connectToDB(userToEdit.database)
	requestedData = userConnected.selectData(table, listColumnNames = ['rowid'], listSearchValues = [recordAmount], listOperators = ['<'], selectCustomFromAllColumns = True, printOnConsole = False)
	columnNamesRaw = userConnected.getTableInfo(table)
	columnNames = []
	for loop in range(len(columnNamesRaw)):
		columnNames.append(columnNamesRaw[loop][1])
	userConnected.conn.close()#close sqlite connection
	#print("--------------------requestedData------------------------>", requestedData)
	#print("--------------------columnNames------------------------>", requestedData)
	return jsonify({
		"info"   :  requestedData,
		"columnNames"   :  columnNames,
	})
@app.route("/editUserUpdateTable", methods=['GET','POST'])
def addRecords():
	data = request.get_json()
	username = request.args.get('username')#username to identify database
	table = request.args.get('table')
	userToEdit = User.query.filter_by(username=username).first()
	userConnected = dbconn.user()
	userConnected.connectToDB(userToEdit.database)
	tableInfo = userConnected.getTableInfo(table)#get table info
	keyList = list(data[0].keys())
	if len(tableInfo) != len(keyList):
		userConnected.conn.close()#close sqlite connection
		return jsonify({
		"info"   :  "Number of columns does not match with database!",
		})
	
	valueList = []
	for loop in range(len(keyList)):
		itemToAppendRaw = data[0][keyList[loop]]
		if isinstance(itemToAppendRaw, str) == True:
			#remove all whitespaces from string
			itemToAppend = itemToAppendRaw.strip()#remove leading and ending whitespaces
			valueList.append(itemToAppend)
		else: valueList.append(itemToAppendRaw)
	
	#------------------------------------------------Remove leading and ending whitespaces-------------------------------------------
	dataLenght = len(data[0])
	valueListExport = []
	for loop in range(len(data)):
		currentDict = data[loop]
		valueListRaw = list(currentDict.values())
		valueList = []
		for item in range(len(valueListRaw)):
			if isinstance(valueListRaw[item], str) == True:
				#remove all whitespaces from string
				itemToAppend = valueListRaw[item].strip()#remove leading and ending whitespaces
				valueList.append(itemToAppend)
			else: valueList.append(valueListRaw[item])
		valueListExport.append(valueList)
	
	#change date format from /%m/%Y to %Y-%m-%d 
	newValueListExport = customFunctions.changeDateFormat(valueListExport)
	
	isUpdated, recordUploadCount = userConnected.updateTableUniqueRecords(table, newValueListExport, reportUpdateCount = True, specificKeyList = keyList)#perform data update

	if isUpdated == False:
		userConnected.conn.close()#close sqlite connection
		return jsonify({
		"info"   :  "All data are same, nothing was updated.",
		})
	#---------------------------------------------------------add record to actionLog.db--------------------------------------------------------------------
	userConnected.cur.execute('SELECT COUNT(*) FROM ' + str(table) +';')
	countRaw = userConnected.cur.fetchall()
	startedFromRow = countRaw[0][0] - recordUploadCount
	currentActionInput = "Add " + str(recordUploadCount) + " records. Starting from rowid > " + str(startedFromRow)
	dbconn.addRecordToActionLogDB(current_user.username, currentActionInput, userToEdit.database, table)
	
	
	userConnected.conn.close()#close sqlite connection
	return jsonify({
		"info"   :  "Data uploaded succesfully!",
	})

@app.route("/editUserRequestFromURL", methods=['GET','POST'])
def requestFromUrl():
	url = request.get_json()
	tableData, columnNames = dbconn.downloadCSV(url)
	return jsonify({
		"info"   :  "Data got succesfully!",
		"tableData" : tableData,
		"columnNames" : columnNames
	})
	
@app.route("/editUserUpdateTableUrl", methods=['GET','POST'])
def updateTableUrl():
	targetDatabase = request.args.get('targetDatabase')# None type if not existing
	username = request.args.get('username')#username to identify database
	table = request.args.get('table')
	if targetDatabase != None:
		recordNames = request.get_json()
		userConnected = dbconn.user()
		userConnected.connectToDB(targetDatabase)
		#print('--------recordNames-------->', recordNames)
		userConnected.deleteRecords('usrUrl', specificRecords = recordNames, specificColumns = ["tableName"])
		
		return jsonify({
			"info"   :  "Data got succesfully!"
		})
	elif username != None and table == None: # download data from specified urls and update table
		userToEdit = User.query.filter_by(username=username).first()
		userConnected = dbconn.user()
		userConnected.connectToDB(userToEdit.database)
		selectedData = userConnected.selectData('usrUrl', selectAll = True, printOnConsole = False)
		tablesUpdated = 0
		for item in selectedData:
			currentTableData, currentTableNames = dbconn.downloadCSV(item[1])
			#print(currentTableData)
			#change date formats
			newValueListExport = customFunctions.changeDateFormat(currentTableData)
			#print(newValueListExport)
			isUpdated = False
			#if any(name in item[0] for name in tablesToFilterPartialName):
			#	isUpdated = userConnected.updateTableUniqueRecords(item[0], newValueListExport, specificCase1 = 0)
			#else:
			#	isUpdated = userConnected.updateTableUniqueRecords(item[0], newValueListExport) #perform data update
			newValueListExport = dbconn.faultyDataCheck(newValueListExport, currentTableNames, userConnected.getTableInfo(item[0]))
			isUpdated = userConnected.updateTableUniqueRecords(item[0], newValueListExport, specificCase1 = 0)
			if isUpdated == True: tablesUpdated += 1
		reportString = str(tablesUpdated) + " tables updated. "
		return jsonify({
			"info"   :  reportString
		})

	url = request.get_json()
	#url = request.args.get('url')
	userToEdit = User.query.filter_by(username=username).first()
	userConnected = dbconn.user()
	userConnected.connectToDB(userToEdit.database)
	selectedData = userConnected.selectData('usrUrl', listColumnNames = ['tableName'], listSearchValues = [table], listOperators = ['='], specificColumnsOnly = False, printOnConsole = False)
	#print(len(selectedData))
	
	if len(selectedData) > 0:
		userConnected.updateData('usrUrl', 'webUrl', url, 'tableName', table)
	else:
		userConnected.insertData('usrUrl', [table,url], ['tableName','webUrl'])
	
	return jsonify({
			"info"   :  "Data got succesfully!"
		})
	userConnected.conn.close()#close sqlite connection
	
@app.route("/editUserDeleteUserData", methods=['GET','POST'])
def deleteUserData():
	targetDatabase = request.args.get('targetDatabase')# None type if not existing
	username = request.args.get('username')#username to identify database
	table = request.args.get('table')
	print('----deleteUserData function--------')
	if table == None:#delete user if table not present
		#---delete user from user list
		print('----username--->', username)
		print('----targetDatabase--->', targetDatabase)
		userConnected = dbconn.user()
		userConnected.connectToDB('userList')
		userConnected.deleteRecords('flaskloginUsers', specificRecords = [username], specificColumns = ['username'])
		userConnected.conn.close()
		#---delete database
		os.chdir("./application/databases")
		databaseFullName = targetDatabase + ".db"
		if os.path.exists(databaseFullName):
			os.remove(databaseFullName)
			print('--user database removed--')
		else: print('--there is no database with this name--')
		os.chdir("../..")
		#print('-------------user delete is complete-----------')
		currentActionInput = 'User with name ->' + username + '<- is deleted, with following database: ' + targetDatabase + '.db'
		dbconn.addRecordToActionLogDB(current_user.username, currentActionInput, targetDatabase, '--DELETED DATABASE--')
	else:
		userConnected = dbconn.user()
		userConnected.connectToDB(targetDatabase)
		
		clonePartialNameList = tablesToFilterPartialName
		coreTableName = None #if recieved table name is base name then this varianle will be with none value
		for loop in range(len(tablesToFilterPartialName)):
			if clonePartialNameList[loop] in table:
				table = table.replace(clonePartialNameList[loop],'')
				break

		#perform table delete process
		# all data about additional subtables are taken from list: tablesToFilterPartialName from config file
		commandToExecute = 'DROP TABLE ' + table
		userConnected.cur.execute(commandToExecute)
		for item in clonePartialNameList:
			commandToExecute = 'DROP TABLE ' + table + item
			userConnected.cur.execute(commandToExecute)

		currentActionInput = 'Table with name ->' + table + '<- is deleted, including _graphics & _headers table'
		dbconn.addRecordToActionLogDB(current_user.username, currentActionInput, targetDatabase, table)
	return jsonify({
			"info"   :  "Data got succesfully!"
		})

@app.route("/editUserChangeUserStatus", methods=['GET','POST'])
def changeUsrStatus():
	username = request.args.get('username')#username to identify database
	currStatus = request.args.get('currStatus')
	nextStatus = None
	if currStatus == "1": nextStatus = 0
	else: nextStatus = 1
	print('----------------username------------->',username)
	print('----------------currStatus------------->',currStatus)
	print('----------------nextStatus------------->',nextStatus)
	userToEdit = User.query.filter_by(username=username).first()
	userConnected = dbconn.user()
	userConnected.connectToDB('userList')
	commandToExecute = "UPDATE flaskloginUsers SET isActive = " + str(nextStatus) + " WHERE username = " + "'" + username + "'"
	userConnected.cur.execute(commandToExecute)
	userConnected.conn.commit()
	userConnected.conn.close()#close sqlite connection
	return jsonify({
		"info"   :  "Status changed!",
	})


