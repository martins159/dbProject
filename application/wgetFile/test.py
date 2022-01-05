import csv

rawData = []
with open("./Download?Path=%2FDataLogs%2Fdatalog1.csv") as f:# cvs reader object must be created inside with statement to succesfully delete the file after it
	csvReader = csv.reader(f, delimiter=',', quotechar='"')
	for loop in csvReader:
		rawData.append(loop)
print(rawData[1])
print(len(rawData))

clearedData = []
for row in rawData:
	rowValues = []
	for cell in row:
		rowValues.append(cell.strip())
	clearedData.append(rowValues)

print(len(clearedData))

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
print(tableData)
print(len(tableData))
#print()
