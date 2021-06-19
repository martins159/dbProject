from datetime import datetime


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
	print('--------keyWord--------->', keyWord)
	filteredTableNames = [table for table in dataList if not keyWord in table]
	print(filteredTableNames)
	return filteredTableNames