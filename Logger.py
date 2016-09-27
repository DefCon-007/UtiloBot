import threading
from datetime import datetime
class Logger:
    loggerName = None

    def __init__(self,name='default_logger'):
        global loggerName
        if name is not None:
            loggerName = name + '.log'
            return None
        return None

    def addLog(self,message,mob_no="None"):
        global loggerName
        var = "{}-{}-{}\n".format(str(datetime.now())[:-7],mob_no,message)
        with open(loggerName, "a") as myfile:
            myfile.write(var)
        return


    # Remember that this will not ensure order of events
    def addLog_NewThread(self,message):
        return threading.Thread(target=self.addLog, args=(message,)).start()


    def viewAllLogs(self):
        global loggerName
        with open(loggerName, "r") as myfile:
            data = myfile.readlines()
        return data


    def viewLastLog(self):
        global loggerName
        with open(loggerName, "r") as myfile:
            data = myfile.readlines()
        index = len(data) - 1
        return data[index]
