#!/usr/bin/python
# -*- coding: utf-8 -*-
from multiprocessing import Process,Pool 
import urllib,urllib2,cookielib,sys,os,types,re,threading,MySQLdb
class torrent:
    def __init__(self):
        self.username='yourusername'
        self.password='yourpassword'
        self.db_host='192.168.96.242'
        self.db_user='root'
        self.db_passwd=''
        self.db_name='ftp'
        self.opener = self.cookie()
        self.page_6v = {'movie': 13,'tv':14,'music':15,'ent':16,'pe':17,'file':18,'soft':19,'other':20,'game':21,'avg':44,'record':127,'hdmovie':45,'hdtv':48,'hdrecord':49,'hdmv':50,'hdmusic':91}
    def cookie(self):
        auth_url = 'http://bt.neu6.edu.cn/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
        data={"username":self.username,"password":self.password,"quickforward":"yes","hamdlekey":"ls"}
        post_data=urllib.urlencode(data)
        cookieJar=cookielib.CookieJar()
        opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
        req=urllib2.Request(auth_url,post_data)
        result = opener.open(req)
        return opener
    def pagesum(self,page):
        rs = re.findall(r'\.{3}\s\d*',page)
        return rs[0][4:7]
    def pagelist(self):
        for board in self.page_6v.values():
            #self.page(board)
            p = Process(target=self.page, args=(board,))
            p.start()
    def content(self,url):
        f = self.opener.open(url)
        str = f.read()
        html = str.decode('gbk', 'ignore').encode('utf-8')
        return html
        f.close()
    def page(self,board):
        url = 'http://bt.neu6.edu.cn/forum-'+str(board)+'-1.html'
        html = self.content(url)
        pagemax = int(self.pagesum(html))+1
        for pnum in range(1,pagemax):
            pid=str(board)+'-'+str(pnum)
            turl = 'http://bt.neu6.edu.cn/forum-'+pid+'.html'
            #self.seedinfo(turl)
            t = threading.Thread(target=self.seedinfo,args=(turl,))
            t.start()
            t.join()
    def seedinfo(self,url):
        html = self.content(url)
        rs = re.findall(r'thread.*t">\[.*\]<',html)
        size = re.findall(r'\d*\.\d*\s\wB|\d{1,3}\s[K|M|G|T]B|\d*\sBytes',html)
        sql = "INSERT INTO `file` (`id`, `name`, `dir` , `size`) VALUES "
        for list in rs:
            tid = rs.index(list)
            surl = 'http://bt.neu6.edu.cn/'+re.findall(r'thread.*html',list)[0]
            title = re.findall(r'\[.*\]',list)[0]
            stitle = title.replace("'","\\\'")
            #sql = "INSERT INTO `file` (`id`, `name`, `dir` , `size`) VALUES ('', '"+stitle+"', '"+surl+"', '"+size[tid]+"')"
            sql = sql+"('', '"+stitle+"', '"+surl+"', '"+size[tid]+"'),"
           # print sql[0:-1]
            print surl
           # print size[tid]
        #self.insert(sql[0:-1])
        #sys.exit(0)
    def insert(self,sql):
        conn = MySQLdb.Connect(user='root', passwd='', db='ftp', host='192.168.96.242',charset='utf8')
        cur=conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
down = torrent()
down.pagelist()
#down.seedinfo('14-172')
