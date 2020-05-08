# -*- coding:utf-8 -*-

__all__ = ['Exporter']

import sys, os, threading,math,traceback,gc,json,re,time
import requests,pymysql,xlsxwriter
from pymysql.cursors import DictCursor

from lib.Base import Base

class Exporter(Base):
    rootPath = os.path.dirname(os.path.realpath(sys.argv[0]))
    tmpPath = rootPath + '/tmp'
    
    dataDir = tmpPath + '/export-data'
    dataPath = dataDir + '/page-{page}.csv'

    dataInfoDir = tmpPath + '/export-info'
    dataInfoPath = dataInfoDir + '/page-{page}.json'
    taskInfoPath = dataInfoDir + '/task.json'

    errorLogPath = dataInfoDir + '/error.log'

    db_list = []
    threadList = []
    cfg = {}

    def __init__(self, inited=True):
        super().__init__(inited)
        #print('exporter __init__')
    
    def parent(self):
        return super()
        
    def init(self):
        super().init()
        #print('exporter init')

        try:
            if not os.path.exists(self.dataDir):
                os.mkdir(self.dataDir)
            if not os.path.exists(self.dataInfoDir):
                os.mkdir(self.dataInfoDir)
        except:
            traceback.print_exc()
            self.log('Can not create [/export-data] or [/export-info] path.', ['exit', None])

    def loadConfig(self):
        super().loadConfig()
        self.cfg = self.config['Export'] if self.config else None

        #extract
        if self.cfg and self.cfg[self.cfg['extractSection']]:
            for k, v in self.cfg[self.cfg['extractSection']].items():
                self.cfg[k] = v
            
        return self.cfg

    '''
    def log(self, str, extra=None):
        #print('----------------------', end="\n")
        #print(str, end="\n")
        pass
    '''
    def __del__(self):
        self.closeConnect()

    def getMysqlData(self, sql, page):
        if len(self.db_list) < 1:
            self.db_list.append(None)
        
        try:
            self.db_list[page - 1] = pymysql.connect(
                host=self.cfg['host'], 
                port=self.cfg['port'],
                user=self.cfg['user'], 
                password=self.cfg['password'], 
                database=self.cfg['database'], 
                charset=self.cfg['charset'], 
                connect_timeout=self.cfg['connectTimeout']
            )
            
            #self.db_list[page - 1].ping(reconnect=True)

            cursor = self.db_list[page - 1].cursor(DictCursor)
            cursor.execute(sql)
            results = cursor.fetchall()
            
            #gc
            self.db_list[page - 1].close()
            self.db_list[page - 1] = None
            del cursor
            gc.collect()
            
            return results
        except Exception as e:
            self.log('The page %d mysql data can not been fetched, Sql: %s, Error: %s' % (page, sql, e.__str__()), ['error', None])
            return None

    def getElasticsearchData(self, query, page):
        headers = json.loads(self.cfg['headers']) if self.cfg['headers'] else {}
        cookies = json.loads(self.cfg['cookies']) if self.cfg['cookies'] else {}
        
        try:
            response = requests.post(self.cfg['url'], data=query, timeout=self.cfg['connectTimeout'], headers=headers, cookies=cookies, verify=False)
        except Exception as e:
            response = None
            self.log('The page %d request failure, HTTP Error: %s' % (page, e.__str__()), ['error', None])


        if response == None or response.status_code != 200:
            self.log('The page %d request failure, Error: %s' % (page,  'None' if response == None else response.text), ['error', None])

            return None
        
        #print(response.text)
        try:
            content = json.loads(response.text)
        except Exception as e:
            self.log('The page %d parse json data failure, Error: %s' % (page, e.__str__()), ['error', None])

            return None

        ret = []
        for item in content['hits']['hits']:
            ret.append(dict({"_index":item['_index'],"_type":item['_type'],"_id":item['_id']}, **item['_source']))
        #print(ret)

        #gc
        del content
        del response

        return ret

    def getHttpFile(self, sql, page):
        headers = json.loads(self.cfg['headers']) if self.cfg['headers'] else {}
        cookies = json.loads(self.cfg['cookies']) if self.cfg['cookies'] else {}
        
        try:
            response = requests.post(self.cfg['url'], data=sql, timeout=self.cfg['connectTimeout'], headers=headers, cookies=cookies, verify=False)
        except Exception as e:
            response = None
            self.log('The page %d occur HTTP Error: %s' % (page, e.__str__()), ['error', None])


        if response == None or response.status_code != 200:
            self.log('The page %d request failure, Error: %s' % (page,  'None' if response == None else response.text), ['error', None])

            return None
        
        content = response.content.decode()
        r = re.match(r'^(\d+)\n.*', content)
        total = int(r[1])
        return {"total": total, "content": content[len(r[1])+1:]}


    def fetchData(self, sql, page):
        if self.cfg['driver'] == 'mysql':
            return self.getMysqlData(sql, page)
        
        elif self.cfg['driver'] == 'elasticsearch':
            return self.getElasticsearchData(sql, page)

        elif self.cfg['driver'] == 'http-file':
            return self.getHttpFile(sql, page)


    def closeConnect(self):
        for i in self.db_list:
            if i and not i._closed:
                i.close()

    def stopTask(self):
        self.taskStatus = -1
        self.closeConnect()
        gc.collect()

    def runTask(self, resumeRun=False, loopRun=False):
        self.loadConfig()
        
        if not resumeRun:
            self.log('Start clearing export data dir...')
            self.clearDir(self.dataDir)
            self.log('Start clearing export info dir...')
            self.clearDir(self.dataInfoDir)


        gc.collect()
        self.threadList.clear()
        self.threadLock = threading.Semaphore(self.cfg['maxThreadNum'])
        self.taskStatus = 1
        self.taskFinished = -1 if self.isLoopTask() else 0

        totalPage = self.getTotalPage()
        
        self.log('Start running export task...')

        #thread
        for i in range(1, totalPage + 1):
            self.db_list.append(None)

            #start
            if not self.isLoopTask() and os.path.exists(self.dataInfoPath.format(page=i)):
                self.taskFinished += 1
            elif self.isLoopTask() and i <= self.getTaskInfo()['page']:
                self.taskFinished += 1
            else:
                t = threading.Thread(target=self.exportData,args=(i, self.getTaskInfo()['end']+1 if self.isLoopTask() else None))
                self.threadList.append(t)
        
        #start thread
        for v in self.threadList:
            k = v._args[0]
            if self.taskStatus < 0:
                self.log('Thread export-%d has been interrupted without starting' % k)
                break

            self.threadLock.acquire()
            v.start()
            self.log('Thread export-%d has started.' % k, ['progress', self.getProgress('progress')])

        self.log('All %d threads have been started' % len(self.threadList))
        
        for (k, v) in enumerate(self.threadList):
            if self.taskStatus < 0:
                self.log('Thread-%d has been interrupted without ending' % (k+1))
                break

            v.join()
            self.log('Thread-%d has finished' % (k+1), ['progress', self.getProgress('progress')])

            

        #finish
        if self.taskStatus == 1:
            self.taskStatus = 0

        self.threadList.clear()
        gc.collect()

        #loop
        if loopRun and self.taskStatus>=0 and self.taskFinished<totalPage:
            self.log('Loop to run export task...')
            time.sleep(self.cfg['loopSleepTime'])

            if self.taskStatus>=0:
                self.runTask(True, True)
        else:
            self.log('Export task has finished', ['end', self.getProgress('end')])

    def parseSQL(self, sql, page, s, e):
        sql = sql.replace('{start}',str(s))
        sql = sql.replace('{end}',str(e))
        sql = sql.replace('{page}',str(page))
        sql = sql.replace('{offset}',str((page-1) * self.cfg['pageSize']))
        sql = sql.replace('{size}',str(self.cfg['pageSize']))

        return sql

    def exportData(self, page, startLine=None):
        if self.taskStatus < 0:
            self.log('Thread export-%d has been interrupted' % page)
            self.threadLock and self.threadLock.release()
            return

        totalPage = self.getTotalPage()
        self.log('Exporting the page %d, total %d pages...' % (page, totalPage))

        if self.isLoopTask():
            s = startLine
            e = s + self.cfg['pageSize']
        else:
            s = (page - 1) * self.cfg['pageSize'] +  self.cfg['startLine']
            
            e = s + self.cfg['pageSize']
            e = self.cfg['endLine'] if e > self.cfg['endLine'] else e

            #last page
            if page >= totalPage:
                e = e + 1

        sql = self.parseSQL(self.cfg['sql'], page, s, e)
        self.log(sql)
        
        d = self.fetchData(sql, page)
        #print(d)
        if self.cfg['driver'] == 'http-file':
            if self.isLoopTask() :
                if d and d["total"] > 0:
                    self.saveFileData(d, page, s, e)
                else:
                    if not self.isEmpty('checkSql', self.cfg):
                        self.log('Checking the page %d data...' % page)

                        sql2 = self.parseSQL(self.cfg['checkSql'], page, s, e)
                        self.log(sql2)
                        d2 = self.fetchData(sql2, page)
                        if d2 and d2["total"] > 0:
                            self.saveFileData(d2, page, s, e)
                        else:
                            self.log('The page %d is empty' % page)
                    else:
                        self.log('The page %d may be empty' % page)
            else:
                if d and d['total']>=0:
                    self.saveFileData(d, page, s, e)
                else:
                    self.log('The page %d is empty' % page, ['error', None])
        else:
            if self.isLoopTask() :
                if len(d) > 0:
                    self.savePostData(d, page, s, e)
                else:
                    if not self.isEmpty('checkSql', self.cfg):
                        self.log('Checking the page %d data...' % page)

                        sql2 = self.parseSQL(self.cfg['checkSql'], page, s, e)
                        self.log(sql2)
                        d2 = self.fetchData(sql2, page)
                        if d2 and len(d2) > 0:
                            self.savePostData(d2, page, s, e)
                        else:
                            self.log('The page %d is empty' % page)
                    else:
                        self.log('The page %d may be empty' % page)
            else:
                if d != None:
                    self.savePostData(d, page, s, e)
                else:
                    self.log('The page %d is empty' % page, ['error', None])

        #gc
        del d
        gc.collect()

        self.threadLock and self.threadLock.release()
    
    def saveFileData(self, data, page, startLine, endLine):
        if self.taskStatus < 0:
            self.log('Thread export-%d has been interrupted' % page)
            return
        
        self.log('Start exporting the page %d, total %d items...' % (page, data['total']))

        #save data
        with open(self.dataPath.format(page=str(page)), "wb") as f:
            f.write((self.cfg['exportPrefix'] + data['content'] + self.cfg['exportSubfix']).encode(self.cfg['exportCharset'], 'ignore'))

            self.taskFinished += 1
            
            self.log('The page %d info has saved successfully' % page, ['update', self.getProgress('progress'), data['total'], 0])

        #save info
        with open(self.dataInfoPath.format(page=str(page)), "w", encoding="utf-8") as f:
            f.write('{"total":%d,"error":0,"start":%d,"end":%d}' % (data['total'], startLine, endLine))

        #save task
        if self.isLoopTask():
            self.saveTaskInfo(page, startLine, endLine, data['total'], 0)

        return


    def getCsvData(self, d):
        s = self.cfg['exportPrefix']
        
        for row in d:
            t = self.cfg['exportBody'].replace('{field_columns}', ",".join(row.keys()))
            t2 = ''
            fl = len(row)
            
            c = 0
            for i, _ in row.items():
                #filter
                v = str(row[i]) if row[i] != None else row[i]
                if self.cfg['exportFilterPattern']:
                    v = self.filterData(self.cfg['exportFilterPattern'], v, 'export')
                    #print(self.cfg['exportFilterPattern'] + '=>' + v)
                

                if t.find('{comma_fields}') > -1:
                    t2 += self.cfg['exportNullValue'] if v == None else '"%s"' % v
                    if c < fl-1:
                        t2 += ','
                else:
                    t = t.replace('{%s}' % str(i),  str(v) if v != None else '')
                
                c += 1
            
            
            if t.find('{comma_fields}') > -1:
                s += t.replace('{comma_fields}', t2)
            else:
                s += t
            
            #gc
            del t
        
        s += self.cfg['exportSubfix']
        return s

    def savePostData(self, d, page, startLine, endLine):
        if self.taskStatus < 0:
            self.log('Thread export-%d has been interrupted' % page)
            return

        self.log('Start exporting the page %d, total %d items...' % (page, len(d)))

        path = self.dataPath.format(page=str(page))
        startLine = d[0][self.cfg['lineField']] if self.isLoopTask() and len(d) > 0 else startLine
        endLine = d[0][self.cfg['lineField']] if self.isLoopTask() and len(d) > 0 else endLine-1

        #sort and get min & max line
        if self.isLoopTask() :
            for row in d:
                if row[self.cfg['lineField']] > endLine:
                    endLine = row[self.cfg['lineField']]
                if row[self.cfg['lineField']] < startLine:
                    startLine = row[self.cfg['lineField']]

        if self.getExportConfig('exportType') == 'excel':
            try:
                book = xlsxwriter.Workbook(path.replace('.csv', '.xlsx'))
            except Exception as e:
                self.log('Can not create page %d as excel file, Error: %s' % (page, e.__str__()))
                return

            sheet = book.add_worksheet('Worksheet')
            startNo = 0
            
            #header
            if self.cfg['exportPrefix']:
                startNo = 1
                isBold = book.add_format({'bold': 1})
                if self.cfg['exportPrefix'].find('{field_names}') > -1:
                    if d and len(d)>0:
                        c = 0
                        for k,_ in d[0].items():
                            sheet.write(0, c, k, isBold)
                            c += 1
                else:
                    exportHeader = json.loads(self.cfg['exportPrefix'])
                    for i in range(0, len(exportHeader)):  
                        sheet.write(0, i, exportHeader[i], isBold)

            #cells
            for k, row in enumerate(d):
                c = 0
                for _, v in row.items():
                    sheet.write(k + startNo, c, str(v) if v != None else '')
                    c += 1
            
            #cancel
            if self.taskStatus < 0:
                self.log('Thread export-%d has been interrupted' % page)
                return

            try:
                #save data
                book.close()
                self.taskFinished += 1
                self.log('The page %d info has saved successfully' % page, ['update', self.getProgress('progress'), len(d), 0])

                #save info
                with open(self.dataInfoPath.format(page=str(page)), "w", encoding="utf-8") as f:
                    f.write('{"total":%d,"error":0,"start":%d,"end":%d}' % (len(d), startLine, endLine))

                 #save task
                if self.isLoopTask():
                    self.saveTaskInfo(page, startLine, endLine, len(d), 0)

            except Exception as e:
                self.log('Save page %d as excel file failure, Error: %s' % (page, e.__str__()), ['error', None])
            
            #gc
            del book
            del sheet
        else:
            s = self.getCsvData(d)
            if self.taskStatus < 0:
                del s

                self.log('Thread export-%d has been interrupted' % page)
                return

            try:
                #save data
                with open(path, "wb") as f:
                    f.write(s.encode(self.cfg['exportCharset'], 'ignore'))

                    self.taskFinished += 1
                    
                    self.log('The page %d info has saved successfully' % page, ['update', self.getProgress('progress'), len(d), 0])

                #save info
                with open(self.dataInfoPath.format(page=str(page)), "w", encoding="utf-8") as f:
                    f.write('{"total":%d,"error":0,"start":%d,"end":%d}' % (len(d), startLine, endLine))

                #save task
                if self.isLoopTask():
                    self.saveTaskInfo(page, startLine, endLine, len(d), 0)
            except:
                self.log('The page %d info saved failure' % page, ['error', None])

            #gc
            del s

        return



