from application import create_app
#from application import createAutoUpdateProcess
import multiprocessing
from application import dbconn# from application subdirectory import dbconn library
from waitress import serve


def createAutoUpdateProcess():
	# Create the process, and connect it to the worker function
	#new_process = multiprocessing.Process(target=dbconn.autoUpdateDatabases)#args=(process_name,tasks,results)
	new_process = multiprocessing.Process(target=dbconn.autoUpdateDatabases)#args=(process_name,tasks,results)
	# set 'daemon' to true, to terminate child process if app is terminated
	new_process.daemon=True
	# Start the process
	new_process.start()

app = create_app()
if __name__ == "__main__":
	createAutoUpdateProcess()
	#app.run(use_reloader=False)
	app.run(host='0.0.0.0', port="5000",use_reloader=False)# --------- testešanai ar flaska softu
	#serve(app, host='0.0.0.0', port=5000)# ---------------------------- production use
	
