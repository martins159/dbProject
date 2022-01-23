import sys
sys.path.append("..")

from application import dbconn

while True:
	print('modes: 1 - update existing columns text  2 - add new column with text,  3 - add new language 4 - test functions')
	print('choose coresponding modes number: ')
	mode = input()

	userConnected = dbconn.user()
	userConnected.connectToDB('lang')
	if mode == '1':
		langColumn = userConnected.selectData('texts', listColumnNames = ['lang'], specificColumnsOnly = True)
		print('first mode - update existing text')
		print('choose language from these (write it with word): ', langColumn)
		selectedLang = input()
		while True:
			print('next column name to change: ')
			colName = input()
			print('new text: ')
			colText = input()
			stringsToJoin = ("UPDATE texts SET '", colName, "' = '", colText, "'", ' WHERE lang = ', "'",selectedLang, "'")
			commandToExecute = "".join(stringsToJoin)
			#print(commandToExecute)
			userConnected.cur.execute(commandToExecute)
			userConnected.conn.commit()

	if mode == '2':
		langColumn = userConnected.selectData('texts', listColumnNames = ['lang'], specificColumnsOnly = True)
		
		print('second mode - add new text')
		print('choose language from these (write it with word): ', langColumn)
		selectedLang = input()
		
		while True:
			print('next text to append: ')
			text = input()
		#
			tableInfo = userConnected.getTableInfo('texts')
			print(tableInfo)
			lastColNr = int(tableInfo.pop()[1])
			nextColNr = lastColNr + 1
			nextColNr = "'" + str(nextColNr) + "'"
			print(lastColNr, nextColNr)
			userConnected.addColumn('texts', nextColNr, 'STRING') # add new column
			stringsToJoin = ("UPDATE texts SET ", nextColNr, " = '", text, "'", ' WHERE lang = ', "'",selectedLang, "'")
			commandToExecute = "".join(stringsToJoin)
			userConnected.cur.execute(commandToExecute)
			userConnected.conn.commit()

	if mode == '3':
		print('third mode - add new language')
		print('enter name of language: ')
		lang = input()
		stringsToJoin = ('INSERT INTO texts(lang) VALUES (',"'", lang ,"'",')')
		commandToExecute = "".join(stringsToJoin)
		userConnected.cur.execute(commandToExecute)
		userConnected.conn.commit()
	if mode == '4':
		from collections import defaultdict
		textFromCols = ['1','5']
		userConnected.connectToDB('lang')
		textsRaw = userConnected.selectData('texts', listColumnNames = ['lang'], listColsToRecieve = textFromCols,
								listSearchValues = ['latvian'], listOperators = ['='])
		#texts = {}
		#for loop in range(len(textFromCols)):
		texts = {'%s'%textFromCols[n] : '%s'%textsRaw[0][n] for n in range(len(textFromCols))} #textFromCols[loop]] = textsRaw[0][loop]
		
		print('-------------------------->recieved texts from data base: ', textsRaw)
		print(texts)
		print('from first col: ', texts['1'])

