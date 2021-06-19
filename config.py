import os
import platform
from pathlib import Path
class Config:
	TESTING = True
	DEBUG = True
	FLASK_ENV = 'development'
	SECRET_KEY = 'GDtfDCFYjD'

	# Database
	#SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
	if platform.system() == 'Windows':
		SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(Path(__file__).parent / 'application\databases', 'userList.db' )
	elif platform.system() == 'Linux':
		SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(Path(__file__).parent / 'application/databases', 'userList.db' )
	#print(SQLALCHEMY_DATABASE_URI)
	#print(type(SQLALCHEMY_DATABASE_URI))
	#extra ja neiet: https://stackoverflow.com/questions/56230626/why-is-sqlalchemy-database-uri-set-to-sqlite-memory-when-i-set-it-to-a-pa
	#print(SQLALCHEMY_DATABASE_URI)
	SQLALCHEMY_ECHO = False
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	#Path(__file__).parent / "databases/"

#-------------------------------------------Liste ar filtrejamajam tabulam----------------------------------------
#---------------------------Tabulas kuras filtrēt, ja ir sekojošs tabulas nosaukums-------------------------------
tablesToFilterWholeName = [
'usrUrl'
]
#----------------------------Tabulas kuras filtrēt, ja satur sekojošas frāzes -------------------------------------
tablesToFilterPartialName = [
'_graphics',
'_headers',
'_texts'
]
