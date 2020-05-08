# -*- coding:utf-8 -*-

__all__ = ['Base']

import re, sys, os, codecs,urllib,urllib3,threading,time,shutil,glob,json,platform,math,traceback,gc,platform
from configobj import ConfigObj
import requests
import linecache

#handle error
def saveError(v):
    #save
    s = '['+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']\n' + v + '\n'
    p = os.path.dirname(os.path.realpath(sys.argv[0])) + '/error.log'
    with open(p, "a+", encoding="utf-8") as f:
        f.write(s)
def errorHandler(type, value, trace):  
    v = 'Main Error: \n%s' % (''.join(traceback.format_exception(type, value, trace)))
    print(v)
    saveError(v)
    sys.__excepthook__(type, value, trace) 
sys.excepthook = errorHandler


class Base():
    rootPath = os.path.dirname(os.path.realpath(sys.argv[0]))
    tmpPath = rootPath + '/tmp'
    configFilePath = rootPath + '/config.ini'
    errorLogPath = None
    dataInfoDir = None
    dataInfoPath = None
    taskInfoPath = None

    config = {}
    cachedDictData = {}

    threadLock = None
    taskFinished = 0
    taskStatus = 0
    taskFileList = [
        rootPath + '/tmp/export-data/page-{line}.xlsx',
        rootPath + '/tmp/export-data/page-{line}.csv',
        rootPath + '/tmp/export-info/page-{line}.json',
        rootPath + '/tmp/import-info/page-{line}.json',
    ]

    def __init__(self, inited=True):
        #print('base __init__' + ('true' if inited else 'false'))
        if inited:
            self.init()
        
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def init(self):
        #print('base init')
        self.loadConfig()

        try:
            #tmp path
            if not os.path.exists(self.tmpPath):
                os.mkdir(self.tmpPath)
        except:
            traceback.print_exc()
            self.log('Can not create [/tmp] path.', ['exit', None])

    def log(self, str, extra=None):
        print('----------------------', end="\n")
        print(str, end="\n")
    
    def isEmpty(self, key, data):
        if isinstance(data, dict):
            if key in data.keys() and data[key]:
                return False
        elif isinstance(data, list):
            if len(data) > key and data[key]:
                return False
        
        return True

    
    def isWindows(self):
        return platform.system() == 'Windows'

    def clearDir(self, path, delSelf=False):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        
        if delSelf:
            os.rmdir(path)

    def toInt(self, str):
        if isinstance(str, int):
            return str
        else:
            str = re.sub(r'([^\d]+)', '', str)
            return int(str) if str != '' else 0

    def loadConfig(self):
        if not os.path.exists(self.configFilePath):
            self.log("The [config.ini] file does not exist", ['exit', None])
            return None
        
        try:
            self.config = ConfigObj(self.configFilePath, encoding='utf-8')
            
            for(sec, obj) in self.config.items():
                for (k, v) in obj.items():
                    
                    if isinstance(v, str):
                        if re.match(r'^-?[\d]+$', v):
                            self.config[sec][k] = int(v)
                        else:
                            self.config[sec][k] = str(v).replace(r"\n", "\n")
                    else:
                        for (k2, v2) in v.items():
                            if re.match(r'^-?[\d]+$', v2):
                                self.config[sec][k][k2] = int(v2)
                            else:
                                self.config[sec][k][k2] = str(v2).replace(r"\n", "\n")
                        
            
            return self.config
        except:
            self.log('The [config.ini] file can not been parsed.', ['exit', None])
            return None

    def getTotalPage(self):
        cfg = self.getExportConfig()
        #print(cfg)

        if cfg['totalPage'] != 'auto' and cfg['totalPage'] > 0:
            return cfg['totalPage']

        if cfg['pageSize']>0:
            if cfg['endLine'] > cfg['startLine']:
                pageNum = math.ceil((cfg['endLine'] - cfg['startLine']) / cfg['pageSize'])
            else:
                pageNum = 0
            
            #forever
            if cfg['endLine'] < 0:
                #pageNum = len(glob.glob(self.dataInfoDir + "/page-*.json")) + 1
                pageNum = self.getTaskInfo()['page'] + 1

        else:
            pageNum = 0

        if cfg['endLine'] < 0 and 'lineField' not in cfg.keys():
            self.log('if [endLine] less than 0 then [lineField] should be set.', ['exit', None])
            return 0

        if cfg['endLine'] < 0 and cfg['maxThreadNum']>1:
            self.log('if [endLine] less than 0 then [maxThreadNum] should be set 1.', ['exit', None])
            return 0

        if pageNum<=0:
            self.log('[endLine] should be greater than [startLine] and [pageSize] should be greater than 0.', ['exit', None])
            return 0
        else:
            return pageNum
    
    def getProgress(self, type):
        totalPage = self.getTotalPage()
        p = int(self.taskFinished / totalPage * 100) if totalPage>0 else 0
        p = min(p, 99 if type == 'progress' else 100)

        if self.taskFinished > 0 and p <= 0:
            p = 1
        
        #print('%d%%' % p)

        return p

    def saveError(self, str):
        with open(self.errorLogPath, "a+", encoding="utf-8") as f:
            f.write(str + '\n')

    def filterData(self, pattern, v, key='none'):
        if v == None:
            return v

        v = str(v)
        
        if self.cachedDictData and key in self.cachedDictData.keys() and pattern == self.cachedDictData[key]['raw']:
            p = self.cachedDictData[key]['json']
        else:
            self.cachedDictData[key] = {'raw':pattern}

            pattern = pattern.replace('\n', '\\n') 
            p = json.loads(pattern)
            self.cachedDictData[key]['json'] = p

        for i in p:
            #v = re.sub(i['p'], i['r'], v)
            v = v.replace(i['p'], i['r'])

        #print(v)
        return v

    def taskExists(self):
        total = len(glob.glob(self.dataInfoDir + "/page-*.json"))
        if total > 0:
            return True
        else:
            return False

    def isLoopTask(self):
        if self.getExportConfig('endLine') < 0:
            return True
        else:
            return False

    def getTaskInfo(self):
        ret = {'page':0, 'start':0, 'end':0, 'total':0, 'error':0, 'process':0}

        if self.isLoopTask():
            if os.path.exists(self.taskInfoPath):
                with open(self.taskInfoPath, 'r') as f:
                    try:
                        ret = json.load(f)
                    except:
                        self.log('The task info parse json data failure', ['error', None])
                        return ret

            if ret['total'] > 0:
                ret['process'] = 1
        else:
            totalPage = self.getTotalPage()
            for i in range(1, totalPage + 1):
                path = self.dataInfoPath.format(page=str(i))
                if os.path.exists(path):
                    self.taskFinished += 1
                    with open(path, 'r') as f:
                        try:
                            d = json.load(f)
                            ret['total'] += d['total']
                            ret['error'] += d['error']
                        except:
                            self.taskFinished -= 1
                            self.log('The page-%d info parse json data failure' % i, ['error', None])

            ret['process'] = self.getProgress('end')
        
        return ret

    def saveTaskInfo(self, page, startLine, endLine, total, error):
        ret = {'page':0, 'start':0, 'end':0, 'total':0, 'error':error}
        if os.path.exists(self.taskInfoPath):
            with open(self.taskInfoPath, 'r') as f:
                try:
                    ret = json.load(f)
                except:
                    self.log('The task info parse json data failure', ['error', None])
                    return False

        ret['page'] = page
        ret['start'] = startLine
        ret['end'] = endLine
        ret['total'] += total
        ret['error'] += error

        try:
            with open(self.taskInfoPath, 'w') as f:
                json.dump(ret, f)

            return True
        except:
            return False

    def deleteTaskInfo(self, page):
        for i in self.taskFileList:
            path = i.format(line=str(page))
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    self.log('Delete task file [%s] failure, Error: %s.' % (path, e.__str__()), ['error', None])
    
        return True

    def getExportConfig(self, key=None):
        cfg = self.config['Export']
        if cfg['extractSection']:
            for k, v in cfg[cfg['extractSection']].items():
                cfg[k] = v

        return cfg[key] if key else cfg
    
    def getImportConfig(self, key=None):
        cfg = self.config['Import']
        if cfg['extractSection']:
            for k, v in cfg[cfg['extractSection']].items():
                cfg[k] = v

        return cfg[key] if key else cfg

    def getFileContent(self, path, startLine, num):
        if not os.path.exists(path):
            return None

        ret = ''
        for i in range(0, num):
            ret += linecache.getline(path, startLine+i)

        linecache.clearcache()
        
        return ret
    