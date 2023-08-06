#coding:utf8
__author__ = 'root'
import traceback
from ObserverModel import Subject, Observer
import threading, time
from pyetc import load, reload, unload
import logging, os, sys

class LogSubject(Subject):
    timer_log = 0
    timer_interval = 3
    configuration = 0
    time_load_config = 0
    configurationFile = "log4p.py"
    t1 = 0
    config_all_default = {
        'monitorInterval' : 0,
        'loggers' :{
            'root' :{
                'level' : "ERROR",
                'AppenderRef' : 'console'
            }
        },
        'appenders' :{
            'console' :{
                'type' :"console",
                'target' :"console",
                'PatternLayout' :"[%(levelname)s] %(asctime)s %(message)s"
            }
        }
    }

    def __init__(self):
        #观察者列表
        super(LogSubject, self).__init__()
        self.data = 0
        self.start()

    def start(self):
        self.t1 = time.time()
        # check "configuration" file exist?
        #filename = getattr(sys.modules['__main__'], '__file__')  #when (python test.py),
        #MainPath = os.path.dirname(filename)
        MainPath = os.path.split(os.path.realpath( sys.argv[0]))[0]
        if os.path.exists(MainPath +"/"+ self.configurationFile):
            self.configuration = load(MainPath +"/"+ self.configurationFile)
            self.data = dict(self.config_all_default, **self.configuration.config)
        else:
            print("Configuration File Not Found!! Use default Configuration...")
            self.data = self.config_all_default
        # notification all observers
        self.notifyObservers()

        # check "monitorInterval" is set?
        if int(self.data['monitorInterval']) > 0:
            self.timer_log = threading.Timer(self.timer_interval, self.reload_config)
            self.timer_log.start()

    def check_threading_status(self):
        '''检测其他线程是否处于alive状态。如果其他全部进程处于stoped状态时，则退出当前日志记录进程'''
        cur_obj = threading.currentThread()
        obj_thread = threading.enumerate()

        error = True
        for item in obj_thread:
            if cur_obj.name == item.name:
                continue
            if item.isAlive():
                error = False

        if error:
            sys.exit()

    def reload_config(self):
        self.check_threading_status()
        if (self.time_load_config - int(time.time())) > 0:
            self.timer_log = threading.Timer(self.timer_interval, self.reload_config)
            self.timer_log.start()
            return

        try:
            # reload new log config
            self.configuration = reload(self.configuration)
            self.data = self.configuration.config

            # update ROOT-logger' configuration
            # do somethings

            # notification all observers
            self.notifyObservers()
            self.time_load_config = self.configuration.config['monitorInterval'] + int(time.time())
            self.timer_log = threading.Timer(self.timer_interval, self.reload_config)
            self.timer_log.start()
            self.t1 = time.time()
        except:
            error_info = "\n"
            error_info += traceback.format_exc()
            print(error_info)

    def update_root(self):
        g_logger = logging.getLogger("root")
        pass

if __name__ == '__main__':
    log = LogSubject()
    log.start()
