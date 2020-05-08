# -*- coding:utf-8 -*-

__all__ = ['Importer']

import sys, os,threading,json,math,traceback,gc,time
import requests,xlrd,pymysql
from requests_toolbelt import MultipartEncoder
from pymysql.cursors import DictCursor

from lib.Base import Base

class Importer(Base):
    rootPath = os.path.dirname(os.path.realpath(sys.argv[0]))
    tmpPath = rootPath + '/tmp'

    exportPath = tmpPath + '/export-data/page-{page}.csv'

    dataInfoDir = tmpPath + '/import-info'
    dataInfoPath = dataInfoDir + '/page-{page}.json'
    taskInfoPath = dataInfoDir + '/task.json'

    errorPath = dataInfoDir + '/error.json'
    errorLogPath = dataInfoDir + '/error.log'

    threadList = []
    cfg = {}

    def __init__(self, inited=True):
        super().__init__(inited)

    def parent(self):
        return super()
        
    def init(self):
        super().init()

        try:
            if not os.path.exists(self.dataInfoDir):
                os.mkdir(self.dataInfoDir)
        except:
            traceback.print_exc()
            self.log('Can not create [/import-info] path.', ['exit', None])

    def loadConfig(self):
        super().loadConfig()
        self.cfg = self.config['Import'] if self.config else None
        
        #extract
        if self.cfg and self.cfg[self.cfg['extractSection']]:
            for k, v in self.cfg[self.cfg['extractSection']].items():
                self.cfg[k] = v

        return self.cfg

    def stopTask(self):
        self.taskStatus = -1
        gc.collect()

    def runTask(self, resumeRun=False, loopRun=False):
        self.loadConfig()
        
        if not resumeRun:
            self.log('Start clearing import info dir...')
            self.clearDir(self.dataInfoDir)

        gc.collect()
        self.threadList.clear()
        self.threadLock = threading.Semaphore(self.cfg['maxThreadNum'])
        self.taskStatus = 1
        self.taskFinished = -1 if self.isLoopTask() else 0

        totalPage = self.getTotalPage()
        
        self.log('Start running import task...')
        #init
        for i in range(1, totalPage + 1):
            #print('page-%d' % i)
            if not self.isLoopTask() and os.path.exists(self.dataInfoPath.format(page=i)):
                self.taskFinished += 1
            elif self.isLoopTask() and i <= self.getTaskInfo()['page']:
                self.taskFinished += 1
            else:
                t = threading.Thread(target=self.importData,args=(i, None))
                self.threadList.append(t)
        
        #start thread
        for v in self.threadList:
            k = v._args[0]
            if self.taskStatus < 0:
                self.log('Thread import-%d has been interrupted without starting' % k)
                break

            self.threadLock.acquire()
            v.start()
            self.log('Thread import-%d has started' % k, ['progress', self.getProgress('progress')])

        self.log('All %d threads have started' % len(self.threadList))

        for k, v in enumerate(self.threadList):
            if self.taskStatus < 0:
                self.log('Thread import-%d has been interrupted without ending' % (k+1))
                break

            v.join()
            self.log('Thread import-%d has finished' % (k+1), ['progress', self.getProgress('progress')])

        
        if self.taskStatus == 1:
            self.taskStatus = 0
        self.threadList.clear()
        gc.collect()

        #loop
        if loopRun and self.taskStatus>=0 and self.taskFinished<totalPage:
            self.log('Loop to run import task...')
            time.sleep(self.cfg['loopSleepTime'])

            if self.taskStatus>=0:
                self.runTask(True, True)
        else:
            self.log('Import task has finished', ['end', self.getProgress('end')])
        
    def getFileData(self, path, page):
        data = ''
        if path.endswith('.xlsx'):
            book = xlrd.open_workbook(path)
            table = book.sheet_by_index(0)
            importStartLine = 0

            if self.getExportConfig('exportPrefix'):
                importStartLine = 1

            for row_num in range(table.nrows):
                if row_num < importStartLine:
                    continue
                
                row_values = table.row_values(row_num)
                c = len(row_values)
                for i in range(0, c):
                    if row_values[i] == None:
                        data += self.cfg['importNullValue']
                    else:
                        data += '"%s"' % self.filterData(self.cfg['importFilterPattern'], row_values[i], 'import')
                    
                    if i < c-1:
                        data += ","
                    else:
                        data += '\r\n' if self.isWindows() else '\n'
            
            with open(self.exportPath.format(page=str(page)), "wb") as f:
                f.write(data.encode(self.cfg['importCharset'], 'ignore'))

            return data
        else:
            with open(path, "rb") as f:
                data = f.read()
            
            #data = '{ "index": {"_id":"0058adeea6c9ff1a9509c14c5d047939"}}\n{ "name":"上海歌绍企业管理中心" }\n{ "index": {"_id":"0058aedb3d9d828c16a9424aaa225036"}}\n{ "company_id": "0058aedb3d9d828c16a9424aaa225036", "company_name":"江西省祥和房地产营销有限公司" }\n'
            #data = data.encode('utf-8')

        return data

    def importData(self, page, extra=None):
        if self.taskStatus < 0:
            self.log('Thread import-%d has been interrupted' % page)
            self.threadLock and self.threadLock.release()
            return

        #get data
        path = self.exportPath.format(page=str(page))
        if self.getExportConfig('exportType') == 'excel':
            path = path.replace('.csv', '.xlsx')
        
        if not os.path.exists(path):
            self.threadLock and self.threadLock.release()
            self.log('The page %d exported data does not exist' % page)
            return False
        
        data = self.getFileData(path, page)
        
        #empty data
        if not data:
            with open(self.dataInfoPath.format(page=str(page)), "w", encoding="utf-8") as f:
                f.write('{"total":0,"error":0}')
            
            self.taskFinished += 1
            
            self.log('Thread import-%d data is empty' % page)
            self.threadLock and self.threadLock.release()
            return
        
        if self.taskStatus < 0:
            #gc
            del data
            gc.collect()

            self.log('Thread import-%d has been interrupted' % page)
            self.threadLock and self.threadLock.release()

            return


        if self.cfg['driver'] == 'mysql':
            self.uploadMysqlData(data, page)
        else:
            self.uploadHttpData(data, page)

        #gc
        del data
        gc.collect()

        self.threadLock and self.threadLock.release()

        return

    def uploadMysqlData(self, data, page):
        self.log('Start importing the page %d...' % page)
        
        if isinstance(data, bytes):
            data = data.decode(self.cfg['importCharset'], 'ignore')
        
        lines = data.strip().split('\n')
        if len(lines)<=0:
            self.log('The page %d has no any lines' % page, ['error', None])
            return False

        try:
            db = pymysql.connect(
                host=self.cfg['host'], 
                port=self.cfg['port'],
                user=self.cfg['user'], 
                password=self.cfg['password'], 
                database=self.cfg['database'], 
                charset=self.cfg['charset'], 
                connect_timeout=self.cfg['connectTimeout']
            )
            cursor = db.cursor(DictCursor)

            affected_rows = 0
            for sql in lines:
                affected_rows += cursor.execute(sql)
            
            db.commit()
            db.close()
            
            self.log('The page %d finished, total %d items, error %d items' % (page, affected_rows, 0))

            #save data
            try:
                with open(self.dataInfoPath.format(page=str(page)), "w", encoding="utf-8") as f:
                    f.write('{"total":%d,"error":%d}' % (affected_rows, 0))

                    self.taskFinished += 1

                    self.log('The page %d info has saved successfully' % page, ['update', self.getProgress('progress'), affected_rows, 0])
            except:
                self.log('The page %d info saved failure' % page, ['error', None])

            #save task
            if self.isLoopTask():
                if self.saveTaskInfo(page, 0, 0, affected_rows, 0):
                    self.deleteTaskInfo(page)


            #gc
            del db
            del cursor
            gc.collect()

            return True
        except Exception as e:
            self.log('The page %d mysql data can not been imported, Error: %s' % (page, e.__str__()), ['error', None])
            return False


    def uploadHttpData(self, data, page):
        self.log('Start uploading the page %d...' % page)

        path = self.exportPath.format(page=str(page))
        headers = json.loads(self.cfg['headers']) if self.cfg['headers'] else {}
        cookies = json.loads(self.cfg['cookies']) if self.cfg['cookies'] else {}
        
        try:
            if self.cfg['method'] == 'post':
                response = requests.post(self.cfg['url'], data=data, timeout=self.cfg['connectTimeout'], headers=headers, cookies=cookies, verify=False)
            else:
                boundary = '----------shiyaxiong1984----------'
                multipart_encoder = MultipartEncoder(fields={'file': (os.path.basename(path), data, 'text/plain')}, boundary=boundary)
                headers['Content-Type'] = multipart_encoder.content_type
                response = requests.post(self.cfg['url'], data=multipart_encoder, timeout=self.cfg['connectTimeout'], headers=headers, cookies=cookies, verify=False)
        except Exception as e:
            response = None
            self.log('The page %d upload failure, HTTP Error: %s' % (page, e.__str__()), ['error', None])
        
        if response == None or response.status_code != 200:
            self.log('The page %d upload failure, Error: %s' % (page,  'None' if response == None else response.text), ['error', None])

            return False
        
        #print(response.text)
        try:
            content = json.loads(response.text)
        except Exception as e:
            self.log('The page %d parse json data failure, Error: %s' % (page, e.__str__()), ['error', None])

            return False


        errors = 0
        if 'items' in content.keys():
            if content['errors']:
                for (k, v) in enumerate(content['items']):
                    d = v['index']
                    if d['status'] not in [200,201]:
                        errors += 1
                        self.log('The %d-%d upload failure, _id=%s, Error: %s' % (page, k+1, d['_id'], d['error']['reason'] if not self.isEmpty('error', d) else json.dumps(d)), ['error', None])

                        #save error
                        try:
                            with open(self.errorPath, "a+", encoding="utf-8") as f:
                                #f.write(d['_id'] + '\n')
                                f.write(self.getFileContent(path, (k+1) * 2 - 1, 2).strip() + '\n')
                        except:
                            self.log('The %d-%d error data saved failure, _id=%s' % (page, k+1, d['_id']), ['error', None])
                        

                self.log('The page %d finished, succee %d, error %d' % (page, len(content['items']), errors))
            else:
                self.log('The page %d finished, total %d items' % (page, len(content['items'])))

            #save data
            try:
                with open(self.dataInfoPath.format(page=str(page)), "w", encoding="utf-8") as f:
                    f.write('{"total":%d,"error":%d}' % (len(content['items']), errors))

                    self.taskFinished += 1
                        
                    self.log('The page %d info has saved successfully' % page, ['update', self.getProgress('progress'), len(content['items']), errors])
            except:
                self.log('The page %d info saved failure' % page, ['error', None])

            #save task
            if self.isLoopTask():
                if self.saveTaskInfo(page, 0, 0, len(content['items']), errors):
                    self.deleteTaskInfo(page)
        else:
            self.log('The page %d finished, total %d items, error %d items' % (page, content['success'], content['error']))

            #save data
            try:
                with open(self.dataInfoPath.format(page=str(page)), "w", encoding="utf-8") as f:
                    f.write('{"total":%d,"error":%d}' % (content['success'], content['error']))

                    self.taskFinished += 1

                    self.log('The page %d info has saved successfully' % page, ['update', self.getProgress('progress'), content['success'], content['error']])
            except:
                self.log('The page %d info saved failure' % page, ['error', None])

            #save task
            if self.isLoopTask():
                if self.saveTaskInfo(page, 0, 0, content['success'], content['error']):
                    self.deleteTaskInfo(page)


        #gc
        del content
        del response

        return True

    
