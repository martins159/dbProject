# coding: utf8

from flask import Blueprint, render_template, request, jsonify, send_file, session
from flask import current_app as app

from ..forms import LoginForm

from flask import request, make_response
from datetime import datetime as dt
from ..models import db, User

from flask import redirect, url_for
from flask_login import current_user, login_required

#-----------------for lastLogin time updating-----------------------
#from datetime import datetime
from .. import customFunctions#for datetime object comparison
from flask_login import current_user

from .. import dbconn


#---------------------pdf generatora library------------------------
import pandas as pd
import numpy as np
from fpdf import FPDF
import matplotlib.pyplot as plt
from PyPDF2 import PdfFileMerger
from matplotlib import rc, rcParams, dates
import os
import sys
import ast
import datetime
from datetime import timedelta

pdf_w = 210
pdf_h = 297
#---------------- config data-------------------------------------
sys.path.append("...")
from config import tablesToFilterWholeName
from config import tablesToFilterPartialName

#-----------------------pdf klase------------------------------------
class PDF(FPDF):
	def lines(self, height1):
		self.set_line_width(0.8)
		self.line(20,height1,190,height1)

	def titles(self,name):
		self.set_xy(0.0,0.0)
		self.set_font('Arial', 'B', 16)
		self.set_text_color(0,0,0)
		self.cell(w = 210.0, h = 40.0, align = 'C', txt = name, border = 0)

	def minititle(self,name, x_val, y_val, cell_w, cell_h):
		os.chdir("./application/pdfFormat")
		self.set_xy(x_val,y_val)
		self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
		self.set_font('DejaVu', '', 16)
		self.set_text_color(0,0,0)
		self.cell(w = cell_w, h = cell_h, align = 'R', txt = name, border = 0)
		os.chdir("../..")

	def texts(self, name, x_val, y_val, cell_w, cell_h):
		self.set_xy(x_val,y_val)
		self.set_font('DejaVu','', 12)
		self.set_text_color(0,0,0)
		self.cell(w = cell_w, h = cell_h, align = 'L', txt = name, border = 0)


msg = None
data = None
info = None

userDataSelectedData = {}
pdfParamsList = {}
pdfEditedDict = {}
graphXValList = []
graphYValList = []
x_dt = []

records_bp = Blueprint(
    'records_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

records_bp.secret_key = 'pdf'
	
@records_bp.route('/recordsTab', methods=['GET', "POST"])
@login_required
def recordsTab():
	"""Records list"""
	if current_user.isAdmin == True: print('user is admin')
	
	#----------------Check if amont of time has past, if is then register current time in db---------------------
	if customFunctions.compareTimeDifference(current_user.lastLogin,timePeriodSeconds = 3600) == True:
		current_user.lastLogin = datetime.datetime.now()#register login time
		db.session.commit()
	
	customPresent = request.args.get('customRecords')# None type if not existing
	if customPresent != None:
		try:
			userData = userDataSelectedData[customPresent]
			userDataSelectedData.pop(customPresent)#remove data from dict to save memory
			tableInfo = userData[0]
			selectedData = userData[1]
			
			import itertools
			columnNames = [loop[1] for loop in tableInfo]
			colNames = columnNames
			out = selectedData
			variable = []
			loopNr = 1
			for row in out:
				cellsDict = {name:cell for (cell,name) in zip(row,colNames)}
				cellsDict["id"] = loopNr
				loopNr += 1
				variable.append(cellsDict)
			
			columnNamesWithoutSpaces = []
			for word in columnNames:
				columnNamesWithoutSpaces.append(word.replace(" ",""))
			colNamesExport = []
			for (titleName,fieldName) in zip(columnNames,columnNamesWithoutSpaces):
				colNamesExport.append({'title':titleName, 'field':fieldName, 'minWidth':100})
			table =  request.args.get('table')
			session['currentTable'] = table
			return render_template(
			'recordsTab.html',
			tableData = variable, columnNames = columnNames, colNamesExport = colNamesExport,  currTable = table, username = current_user.username
			)
		except: print('customRecords is present but data not')
	
    #products = fetch_products(app)
	from .. import dbconn
	msg = None
	data = None
	info = None
	
	userToEdit = User.query.filter_by(username=current_user.username).first()
	userConnected = dbconn.user()
	userConnected.connectToDB(userToEdit.database)
	databaseTables = userConnected.getDatabaseTables()
	for item in tablesToFilterWholeName: databaseTables.remove(item)#remove unwanted tables
	#databaseTables.remove('usrUrl')
	for item in tablesToFilterPartialName: customFunctions.filterIfContain(databaseTables,item)#remove unwanted tables
	#databaseTables = customFunctions.filterIfContain(databaseTables,'_graphics')
	
	if len(databaseTables) > 0:
		databaseData = userConnected.selectData(databaseTables[0],listColumnNames = ['rowid'], listSearchValues = [50], listOperators = ['<'], selectCustomFromAllColumns = True, printOnConsole = False)
		data = [loop[0] for loop in databaseData]
		info = customFunctions.unique(data)
		tableData = userConnected.getTableInfo(databaseTables[0])
		columnNames = [loop[1] for loop in tableData]
		
		import itertools
		colNames = columnNames
		out = databaseData
		variable = []
		loopNr = 1
		for row in out:
			cellsDict = {name:cell for (cell,name) in zip(row,colNames)}
			cellsDict["id"] = loopNr
			loopNr += 1
			variable.append(cellsDict)
		
		columnNamesWithoutSpaces = []
		for word in columnNames:
			columnNamesWithoutSpaces.append(word.replace(" ",""))
		colNamesExport = []
		for (titleName,fieldName) in zip(columnNames,columnNamesWithoutSpaces):
			colNamesExport.append({'title':titleName, 'field':fieldName})
		
		userConnected.conn.close()

		if request.method == "POST":
			v = request.get_json()
			if v != None:#check if not None - this is case when page loads it somehow triger POST event once
				if len(v) != 0:#check if is not empty list - this would be case if user is not selected a row
					print("------------->recieve row info<-------------")
					print("--post no records tab--")
					print("----------> value of 'v': ", v)
					print(type(v[0]))#liste kas sastāv no dictionary elementiem
					session['dic']=v[0]
					#return redirect(url_for('records_bp.pdfConfig'))
					return jsonify({
						"info"   :  "success"
					})
		session['currentTable'] = databaseTables[0]
		return render_template(
		'recordsTab.html',
		tableData = variable, columnNames = columnNames, colNamesExport = colNamesExport, currTable = databaseTables[0], username = current_user.username
		)
	else: 
		userConnected.conn.close()#close sqlite connection
		return render_template(
		'recordsTab.html',
		tableData = [], columnNames = [], colNamesExport = [], currTable = "No table is created yet", username = current_user.username
		)
	
	
	


@records_bp.route('/searchNew', methods = ['POST', 'GET'])
@login_required
def search():
	userToEdit = User.query.filter_by(username=current_user.username).first()
	#print('-------usrnm------------------->',userToEdit)
	databaseTables = None
	userConnected = dbconn.user()
	userConnected.connectToDB(userToEdit.database)
	if userToEdit.database != None:
		databaseTables = userConnected.getDatabaseTables()
		for item in tablesToFilterWholeName: databaseTables.remove(item)#remove unwanted tables
		for item in tablesToFilterPartialName: databaseTables = customFunctions.filterIfContain(databaseTables,item)#remove unwanted tables
	
	#gather info about table decription (columns and datatype)
	tableData = []
	for table in databaseTables:
		colData = userConnected.getTableInfo(table)
		infoDict = {'table':table,'colData' : colData}
		tableData.append(infoDict)
	#tableDataExport = jsonify(tableData)
	userConnected.conn.close()#close sqlite connection
	return render_template('searchNew.html', tables = databaseTables, tableData = tableData, username = current_user.username)

@records_bp.route('/searchNewRequestData', methods = ['POST', 'GET'])
@login_required
def requesReturn():
	recievedData = request.get_json()
	username = request.args.get('username')#username to identify database
	table = request.args.get('table')
	
	#print(recievedData)
	if len(recievedData) > 0:
		colNamesList = []
		operatorList = []
		filterValueList = []
		for row in range(len(recievedData)):
			#if row == (len(recievedData) -1):
			#	continue
			#else:
			colNamesList.append(recievedData[row]['columnName'])
			operatorList.append(recievedData[row]['operator'])
			filterValueList.append(recievedData[row]['filterValue'])
		#print('colNamesList:		',colNamesList)
		#print('operatorList:		',operatorList)
		#print('filterValueList:		',filterValueList)
		
		userToEdit = User.query.filter_by(username=username).first()
		userConnected = dbconn.user()
		userConnected.connectToDB(userToEdit.database)
		
		selectedData = userConnected.selectData(table, listColumnNames = colNamesList, listSearchValues = filterValueList, listOperators = operatorList, selectCustomFromAllColumns = True, printOnConsole = False)
		tableData = userConnected.getTableInfo(table)
		global userDataSelectedData
		userDataSelectedData[username] = [tableData, selectedData]
		#print(userDataSelectedData)
	userConnected.conn.close()#close sqlite connection
	return jsonify({
			"info"   :  "no_errors",
			})
	
@records_bp.route('/settings', methods = ['POST', 'GET'])
@login_required
def settings():
	tableDataUrl = [None] * 2
	databaseTables = None
	#current_user = current_user.username
	userToEdit = User.query.filter_by(username=current_user.username).first()
	userConnected = dbconn.user()
	userConnected.connectToDB(userToEdit.database)
	databaseTables = userConnected.getDatabaseTables()
	for item in tablesToFilterWholeName: databaseTables.remove(item)#remove unwanted tables
	for item in tablesToFilterPartialName: databaseTables = customFunctions.filterIfContain(databaseTables,item)#remove unwanted tables
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
		'settings.html',
		database = userToEdit.database,
		databaseTables = databaseTables,
		tableDataUrl = tableDataUrl,
		urlDataExport = urlDataExport,
		username = userToEdit.username
		)

@app.route("/settingsUserUpdateTableUrl", methods=['GET','POST'])
@login_required
def userupdateTableUrl():
	targetDatabase = request.args.get('targetDatabase')# None type if not existing
	username = request.args.get('username')#username to identify database
	table = request.args.get('table')
	if targetDatabase != None:
		recordNames = request.get_json()
		userConnected = dbconn.user()
		userConnected.connectToDB(targetDatabase)
		userConnected.deleteRecords('usrUrl', specificRecords = recordNames)
		#print('---------------->', recordNames)
		return jsonify({
			"info"   :  "Data got succesfully!"
		})
	elif username != None and table == None:# download data from specified urls and update table
		#print('-------------------> table update')
		userToEdit = User.query.filter_by(username=username).first()
		userConnected = dbconn.user()
		userConnected.connectToDB(userToEdit.database)
		selectedData = userConnected.selectData('usrUrl', selectAll = True, printOnConsole = False)
		tablesUpdated = 0
		for item in selectedData:
			currentTableData, currentTableNames = dbconn.downloadCSV(item[1])
			#print(currentTableData)
			isUpdated = userConnected.updateTableUniqueRecords(item[0], currentTableData)#perform data update
			if isUpdated == True: tablesUpdated += 1
		reportString = str(tablesUpdated) + " tables updated. "
		return jsonify({
			"info"   :  reportString
		})
	
	url = request.args.get('url')
	userToEdit = User.query.filter_by(username=username).first()
	userConnected = dbconn.user()
	userConnected.connectToDB(userToEdit.database)
	selectedData = userConnected.selectData('usrUrl', listColumnNames = ['tableName'], listSearchValues = [table], listOperators = ['='], specificColumnsOnly = False, printOnConsole = False)
	#print(len(selectedData))
	if len(selectedData) > 0:
		userConnected.updateData('usrUrl', 'webUrl', url, 'tableName', table)
	else:
		userConnected.insertData('usrUrl', [table,url], ['tableName','webUrl'])
	userConnected.conn.close()#close sqlite connection
	return jsonify({
			"info"   :  "Data got succesfully!"
		})

#-------------------------------pdf edit un generators----------------------------
	

@records_bp.route('/pdfConfig', methods = ['POST', 'GET'])
@login_required
def pdfConfig():
	paramsListExport = []
	pdfEditedKeyList = []
	pdfEditedValueList = []
	pdfEditedIdList = []
	pdfEditedDictStr = []
	cycleTimeSum = 0
	cycleUTCTime = None
	cycleDate = None

	current_table_txt = session['currentTable']+'_texts'
	userToEdit_txt = User.query.filter_by(username=current_user.username).first()
	userConnected_txt = dbconn.user()
	userConnected_txt.connectToDB(userToEdit_txt.database)
	databaseTables_txt = userConnected_txt.getDatabaseTables()
	databaseData_txt = userConnected_txt.selectData(current_table_txt,selectAll = True,printOnConsole = False)
	print('/////////////////////////////////////SAKASDBTABULA????????????????????????????????????????????????')
	print(str(databaseData_txt[0][0]))
	print(str(databaseData_txt[0][1]))

	#print('-------------------esmute-----------------')
	pdfParamsDict = session['dic']
	#print(pdfParamsDict)
	for key,value in pdfParamsDict.items():
		if key == '1':
			key = str(databaseData_txt[-1][0]) #'Cikla Nr.:'
			session["TitlePDF"] = value
			idNumber = 1
		elif key == '2':
			key = str(databaseData_txt[-1][1]) #'Iekrautie m3:'
			idNumber = 2
		elif key == '3':
			key = str(databaseData_txt[-1][2]) #'Operators:'
			idNumber = 3
		elif key == '4':
			key = str(databaseData_txt[-1][3]) #'Koksnes parametrs 1:'
			idNumber = 4
		elif key == '5':
			key = str(databaseData_txt[-1][4]) #'Koksnes parametrs 2:'
			idNumber = 5
		elif key == '6':
			key = str(databaseData_txt[-1][5]) #'Izvēlētais režīms:'
			idNumber = 6
		elif key == '7':
			key = str(databaseData_txt[-1][6]) #'Sākuma vakuuma sasniegšanas laiks, min:'
			idNumber = 7
			cycleTimeSum = cycleTimeSum + int(value)
		elif key == '8':
			key = str(databaseData_txt[-1][7]) #'Sākuma vakuuma uzturēšanas vakuuma sākuma vērtība, bar:'
			idNumber = 8
		elif key == '9':
			key = str(databaseData_txt[-1][8]) #'Sākuma vakuuma uzturēšanas laiks, min:'
			idNumber = 9
			cycleTimeSum = cycleTimeSum + int(value)
		elif key == '10':
			key = str(databaseData_txt[-1][9]) #'Sākuma vakuuma uzturēšanas vakuuma beigu vērtība, bar:'
			idNumber = 10
		elif key == '11':
			key = str(databaseData_txt[-1][10]) #'Pildīšanas laiks, min:'
			idNumber = 11
			cycleTimeSum = cycleTimeSum + int(value)
		elif key == '12':
			key = str(databaseData_txt[-1][11]) #'Spiediena sasniegšanas laiks, min:'
			idNumber = 12
			cycleTimeSum = cycleTimeSum + int(value)
		elif key == '13':
			key = str(databaseData_txt[-1][12]) #'Spiediena režīma spiediena sākuma vērtība, bar:'
			idNumber = 13
		elif key == '14':
			key = str(databaseData_txt[-1][13]) #'Spiediena režīma laiks, min:'
			idNumber = 14
			cycleTimeSum = cycleTimeSum + int(value)
		elif key == '15':
			key = str(databaseData_txt[-1][14]) #'Spiediena režīma spiediens beigu vērtība, bar:'
			idNumber = 15
		elif key == '16':
			key = str(databaseData_txt[-1][15]) #'Spiediena nomešanas laiks, min:'
			idNumber = 16
			cycleTimeSum = cycleTimeSum + int(value)
		elif key == '17':
			key = str(databaseData_txt[-1][16]) #'Autoklāva izlādes laiks, min:'
			idNumber = 17
			cycleTimeSum = cycleTimeSum + int(value)
		elif key == '18':
			key = str(databaseData_txt[-1][17]) #'Beigu vakuuma sasniegšnas laiks, min:'
			idNumber = 18
			cycleTimeSum = cycleTimeSum + int(value)
		elif key == '19':
			key = str(databaseData_txt[-1][18]) #'Beigu vakuuma uzturēšanas vakuuma sākuma vērtība, bar:'
			idNumber = 19
		elif key == '20':
			key = str(databaseData_txt[-1][19]) #'Beigu vakuuma uzturēšanas laiks, min:'
			idNumber = 20
			cycleTimeSum = cycleTimeSum + int(value)
		elif key == '21':
			key = str(databaseData_txt[-1][20]) #'Beigu vakuuma uzturēšanas vakuuma beigu vērtība, bar:'
			idNumber = 21
		elif key == '22':
			key = str(databaseData_txt[-1][21]) #'Spiediena izlīdzināšanas laiks, min:'
			idNumber = 22
			cycleTimeSum = cycleTimeSum + int(value)
		elif key == '23':
			key = str(databaseData_txt[-1][22]) #'Spiediena izlīdzināšana, noturēšanas laiks, min:'
			idNumber = 23
			cycleTimeSum = cycleTimeSum + int(value)
		elif key == '24':
			key = str(databaseData_txt[-1][23]) #'Sākuma vakuums, sūkņa darbības reizes:'
			idNumber = 24
		elif key == '25':
			key = str(databaseData_txt[-1][24]) #'Beigu vakuums, sūkņa darbības reizes:'
			idNumber = 25
		elif key == 'Date':
			key = str(databaseData_txt[-1][25]) #'Datums:'
			idNumber = 26
			cycleDate = value
		elif key == 'Record':
			key = str(databaseData_txt[-1][26]) #'PLC ieraksta numurs:'
			idNumber = 27
		elif key == 'UTC Time':
			key = str(databaseData_txt[-1][27]) #'Cikla beigu laiks:'
			idNumber = 28
			cycleUTCTime = value
		elif key == 'id':
			key = str(databaseData_txt[-1][28]) #'Datubāzes id numurs:'
			idNumber = 29
		else:
			break
		strValue = str(value)
		strReplace = '"'
		if strReplace in strValue:
			strValue = strValue.replace('"','')
		paramsListExport.append({'1':key,'2':strValue,'3':idNumber})

	userConnected_txt.conn.close()
	print('--------------------export-------------------------')
	#print(paramsListExport)
#---------------------lielumi priekš grafika izveides---------------------------
	#print(cycleTimeSum)
	#print(cycleUTCTime)
	#print(cycleDate)
	

	if request.method == "POST":
		pdfListNames = request.get_json()
		if pdfListNames != None:#check if not None - this is case when page loads it somehow triger POST event once

			#--------------------------grafika datu atlase-----------------------------------------------

			cycleStartTimeMin = None
			cycleStartTimeHr = None

			current_table = session['currentTable']+'_graphics'
			userToEdit = User.query.filter_by(username=current_user.username).first()
			userConnected = dbconn.user()
			userConnected.connectToDB(userToEdit.database)
			databaseTables = userConnected.getDatabaseTables()
			databaseData = userConnected.selectData(current_table,selectAll = True,printOnConsole = False)
			cycleEndTimeAnalog = datetime.datetime.strptime(pdfParamsDict['UTC Time'], '%H:%M:%S')
			cycleTimeHr = (cycleTimeSum // 60)
			cycleTimeMin = int(((cycleTimeSum / 60) - cycleTimeHr) * 60)

			cycleStartTime = cycleEndTimeAnalog - timedelta(hours=cycleTimeHr, minutes=cycleTimeMin)

			#print(cycleStartTime)

			date_time_obj2 = cycleStartTime
			date_time_obj3 = datetime.datetime.strptime(pdfParamsDict['UTC Time'], '%H:%M:%S')
			for varVal in databaseData:
				if varVal[0] == 'Autoclave pressure scaled':
					if cycleDate in varVal[1]:
						date_time_obj1 = datetime.datetime.strptime(varVal[1], '%d/%m/%Y %H:%M')
						#print(date_time_obj1.date())
						#print(date_time_obj1.time())
						if date_time_obj1.time() >= date_time_obj2.time():  #obj1 jābūt mazākam par obj2
							graphXValList.append(date_time_obj1.time())
							graphYValList.append(varVal[2])
							if date_time_obj3.time() <= date_time_obj1.time():
								break

			#print('----------------> graphXValList lists:', graphXValList)
			userConnected.conn.close()#close sqlite connection

			session['startGraph'] = str(date_time_obj2.time())
			session['endGraph'] = str(date_time_obj3.time())

			#--------------------------grafika datu atlase-----------------------------------------------
			

			if len(pdfListNames) != 0:#check if is not empty list - this would be case if user is not selected a row
				#print("------------->recieve row info<-------------")
				for index_nr in pdfListNames:
					for key, value in index_nr.items():
						if key == '1':
							pdfEditedKeyList.append(value)
						elif key == '2':
							pdfEditedValueList.append(value)
						elif key == '3':
							pdfEditedIdList.append(value)
				pdfEditedzipobj = zip(pdfEditedKeyList,pdfEditedValueList)
				pdfEditedDict = dict(pdfEditedzipobj)
				for ek,ev in pdfEditedDict.items():
					pdfEditedDictStr.append(str('{'+'"'+ek+'"'+':'+'"'+str(ev)+'"'+'}'))
				pdfEditedDictIdObj = zip(pdfEditedIdList, pdfEditedDictStr)
				pdfEditedId = dict(pdfEditedDictIdObj)
				#print('------------------------edited-------------------')
				print("--post no pdf --")
				print('----------------------->pdfEditedId: ',pdfEditedId) 
				session['dict'] = pdfEditedId
				#return redirect(url_for('records_bp.autoclave_pdf'))
				print(graphYValList)
				return jsonify({
						"info"   :  "success"
					})

				
				
	return render_template('pdfConfig.html', pdfParams = paramsListExport, username = current_user.username)
	

	
	
	
	
#--------------------------------------pdf generators beidzas----------------------------
#-------------------------PDF generators autoklaavam---------------------------
@records_bp.route('/pdfview', methods = ['POST', 'GET'])
@login_required
def autoclave_pdf():
	userToEdit = User.query.filter_by(username=current_user.username).first()
	userToEditTit = str(userToEdit).replace('<','')
	userToEditTitl = userToEditTit.replace('>','')
	userToEditTitle = userToEditTitl.replace('User ','')
	userToEditTitleText = userToEditTitl.replace('User','Atskaiti sagatavoja:')
	print('------------------->',session)
	acParamsDict = session['dict']
	print(acParamsDict)
	pdf = PDF()
	pdf = PDF(orientation = 'P', unit = 'mm', format = 'A4')
	os.chdir("./application/pdfFormat")
	pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
	os.chdir("../..")
	pdf.set_font('DejaVu', '', 12)
	pdf.add_page()
	cycleValKey, CycleValVal = list(ast.literal_eval(acParamsDict['1']).items())[0]
	pdf.titles('Cikla atskaite Nr. - {}'.format(session["TitlePDF"]))
	pdf.texts(userToEditTitleText, 20,20,20,20)
	pdf.lines(25)
	pdf.lines(100)
	pdf.lines(229)
	pdf.lines(250)
	pdf.lines(258)
	pdf.lines(266)
	pdf.minititle('Cikla apraksts', 20, 20, 170, 20)
	pdf.minititle('Procesa lielumi', 20, 95, 172, 20)
	pdf.minititle('Komentāri', 20, 224, 172, 20)

	for pdfDataKey,pdfDataValue in acParamsDict.items():
		if pdfDataKey == '26':
			pdfDataValueDict = ast.literal_eval(pdfDataValue)
			dictKey, dictVal = list(pdfDataValueDict.items())[0]
			pdf.texts(dictKey,20,30,60,17)
			pdf.texts(dictVal,70,30,60,17)
		elif pdfDataKey == '28':
			pdfDataValueDict = ast.literal_eval(pdfDataValue)
			dictKey, dictVal = list(pdfDataValueDict.items())[0]
			pdf.texts(dictKey,20,36,60,17)
			pdf.texts(dictVal,70,36,60,17)
		elif pdfDataKey == '1':
			pdfDataValueDict = ast.literal_eval(pdfDataValue)
			dictKey, dictVal = list(pdfDataValueDict.items())[0]
			pdf.texts(dictKey,20,42,60,17)
			pdf.texts(dictVal,70,42,60,17)
		elif pdfDataKey == '27':
			pdfDataValueDict = ast.literal_eval(pdfDataValue)
			dictKey, dictVal = list(pdfDataValueDict.items())[0]
			pdf.texts(dictKey,20,48,60,17)
			pdf.texts(dictVal,70,48,60,17)
		elif pdfDataKey == '29':
			pdfDataValueDict = ast.literal_eval(pdfDataValue)
			dictKey, dictVal = list(pdfDataValueDict.items())[0]
			pdf.texts(dictKey,20,54,60,17)
			pdf.texts(dictVal,70,54,60,17)
		elif pdfDataKey == '2':
			pdfDataValueDict = ast.literal_eval(pdfDataValue)
			dictKey, dictVal = list(pdfDataValueDict.items())[0]
			pdf.texts(dictKey,20,60,60,17)
			pdf.texts(dictVal,70,60,60,17)
		elif pdfDataKey == '3':
			pdfDataValueDict = ast.literal_eval(pdfDataValue)
			dictKey, dictVal = list(pdfDataValueDict.items())[0]
			pdf.texts(dictKey,20,66,60,17)
			pdf.texts(dictVal,70,66,60,17)
		elif pdfDataKey == '4':
			pdfDataValueDict = ast.literal_eval(pdfDataValue)
			dictKey, dictVal = list(pdfDataValueDict.items())[0]
			pdf.texts(dictKey,20,72,60,17)
			pdf.texts(dictVal,70,72,60,17)
		elif pdfDataKey == '5':
			pdfDataValueDict = ast.literal_eval(pdfDataValue)
			dictKey, dictVal = list(pdfDataValueDict.items())[0]
			pdf.texts(dictKey,20,78,60,17)
			pdf.texts(dictVal,70,78,60,17)
		elif pdfDataKey == '6':
			pdfDataValueDict = ast.literal_eval(pdfDataValue)
			dictKey, dictVal = list(pdfDataValueDict.items())[0]
			pdf.texts(dictKey,20,84,60,17)
			pdf.texts(dictVal,70,84,60,17)
		else:
			if pdfDataKey == '7':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,105,60,17)
				pdf.texts(dictVal,160,105,60,17)
			elif pdfDataKey == '8':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,111,60,17)
				pdf.texts(dictVal,160,111,60,17)
			elif pdfDataKey == '9':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,117,60,17)
				pdf.texts(dictVal,160,117,60,17)
			elif pdfDataKey == '10':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,123,60,17)
				pdf.texts(dictVal,160,123,60,17)
			elif pdfDataKey == '11':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,129,60,17)
				pdf.texts(dictVal,160,129,60,17)
			elif pdfDataKey == '12':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,135,60,17)
				pdf.texts(dictVal,160,135,60,17)
			elif pdfDataKey == '13':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,141,60,17)
				pdf.texts(dictVal,160,141,60,17)
			elif pdfDataKey == '14':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,147,60,17)
				pdf.texts(dictVal,160,147,60,17)
			elif pdfDataKey == '15':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,153,60,17)
				pdf.texts(dictVal,160,153,60,17)
			elif pdfDataKey == '16':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,159,60,17)
				pdf.texts(dictVal,160,159,60,17)
			elif pdfDataKey == '17':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,165,60,17)
				pdf.texts(dictVal,160,165,60,17)
			elif pdfDataKey == '18':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,171,60,17)
				pdf.texts(dictVal,160,171,60,17)
			elif pdfDataKey == '19':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,177,60,17)
				pdf.texts(dictVal,160,177,60,17)
			elif pdfDataKey == '20':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,183,60,17)
				pdf.texts(dictVal,160,183,60,17)
			elif pdfDataKey == '21':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,189,60,17)
				pdf.texts(dictVal,160,189,60,17)
			elif pdfDataKey == '22':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,195,60,17)
				pdf.texts(dictVal,160,195,60,17)
			elif pdfDataKey == '23':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,201,60,17)
				pdf.texts(dictVal,160,201,60,17)
			elif pdfDataKey == '24':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,207,60,17)
				pdf.texts(dictVal,160,207,60,17)
			elif pdfDataKey == '25':
				pdfDataValueDict = ast.literal_eval(pdfDataValue)
				dictKey, dictVal = list(pdfDataValueDict.items())[0]
				pdf.texts(dictKey,20,213,60,17)
				pdf.texts(dictVal,160,213,60,17)
	
	current_table_pdf = session['currentTable']+'_texts'
	userToEdit_pdf = User.query.filter_by(username=current_user.username).first()
	userConnected_pdf = dbconn.user()
	userConnected_pdf.connectToDB(userToEdit_pdf.database)
	databaseTables_pdf = userConnected_pdf.getDatabaseTables()
	databaseData_pdf = userConnected_pdf.selectData(current_table_pdf,selectAll = True,printOnConsole = False)

	#-------------------------Grafika pievienošana--------------------------------
	if databaseData_pdf[-1][29] == 'true':
		pdf.add_page()
		pdf.titles('Cikla {} grafiks'.format(databaseData_pdf[-1][30]))
		pdf.lines(25)
		plt.rcParams['figure.figsize'] = (6,8.46)
		fig = plt.figure()
		ax = fig.add_subplot(111)

		#-------------šo pieliku klāt (Martins G.) -----------------------------
		my_day = datetime.date(2014, 7, 15)
		x_dt = [ datetime.datetime.combine(my_day, t) for t in graphXValList]
		convertedDates = dates.date2num(x_dt)#dates function are from mathplotlib

		ax.set_xlabel(convertedDates) # Tickmark + label at every plotted point
		ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))

		plt.plot_date(convertedDates, graphYValList, fmt=':k', tz=None, xdate=True, ydate=False)
		plt.xticks(rotation = 45)
		plt.ylabel('{}'.format(databaseData_pdf[-1][31]))
		plt.xlabel('Laiks')
		plt.yticks(np.arange(-1.5, 14, 0.5))
		
		#---------------------------------------------------------
		graphSaved = '{}_plot.png'.format(userToEditTitle)
		fig.savefig(graphSaved,bbox_inches = 'tight')
		pdf.image(graphSaved, x = 30, y = 40, w = 144, h = 203.04)
		#print('saglabats---------------------------------')

	#--------------------------faila ģenerēšana-----------------------------------
	
	pdfFileName = 'Cikla_atskaite_NR_{}'.format(session["TitlePDF"]) 
	os.chdir("./application/pdfFormat")
	response = make_response(pdf.output(dest='S').encode('latin-1'))
	os.chdir("../..")
	response.headers.set('Content-Disposition', 'attachment', filename=pdfFileName + '.pdf')
	response.headers.set('Content-Type', 'application/pdf')

	if databaseData_pdf[-1][29] == 'true':

		graphXValList.clear()
		graphYValList.clear()

		try:
			os.remove(graphSaved)
		except OSError:
			pass

	userConnected_pdf.conn.close()#close sqlite connection
	return response


	