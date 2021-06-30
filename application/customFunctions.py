from datetime import datetime
from dateutil.parser import parse

def compareTimeDifference(first_timeRaw, timePeriodSeconds = 0, timePeriodDays = 0):
	#first_timeRaw - first time
	#timePeriod - time period witch need to be passed in order to return True
	#Function is true if time has past margin
	first_time = first_timeRaw
	second_time = datetime.now()
	first_time = datetime.strptime(str(first_time), '%Y-%m-%d %H:%M:%S.%f')#convert string to datetime object
	difference = second_time - first_time
	#print(difference.seconds, '    ', difference.days)
	if timePeriodDays != 0:
		if difference.seconds > timePeriodSeconds and difference.days >= timePeriodDays:
			return True
	else: 
		if difference.seconds > timePeriodSeconds:
			return True
	return False
	
def unique(it):#filter unique data - entry will be registered only once all other same values will be discarded
#filter out only unique data, example: [1,1,4,3,6,3] --> [1,4,3,6]
	s = []
	for el in it:
		if el not in s:
			s.append(el)
	return s
	
def filterIfContain(dataList,keyWord):
	#print('--------keyWord--------->', keyWord)
	filteredTableNames = [table for table in dataList if not keyWord in table]
	print(filteredTableNames)
	return filteredTableNames

def is_date(string, fuzzy=False):
	#this is not reliable for date detection
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

def validateDate(date_text):
	#detect date based on provided format
	try:
		#datetime.strptime(date_text, '%Y-%m-%d')
		#28/6/2021
		datetime.strptime(date_text, '%d/%m/%Y')
		return True
	except ValueError:
		return False
	
def changeDateFormat(itemList):
	dateItemsIndexes = []
	for item in range(len(itemList[0])):
		if validateDate(itemList[0][item]) == True: dateItemsIndexes.append(item)
	newList = itemList
	
	for currlist in range(len(itemList)):
		for index in dateItemsIndexes:
			#print("------------------itemList[currlist][index]----------------->",itemList[currlist][index])
			item = datetime.strptime(itemList[currlist][index], '%d/%m/%Y')
			
			newList[currlist][index] = item.strftime('%Y-%m-%d')
		
	return newList