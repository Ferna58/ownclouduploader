from urllib.parse import unquote

import requests
import os
import requests_toolbelt as rt
from requests_toolbelt import MultipartEncoderMonitor
from requests_toolbelt import MultipartEncoder
from functools import partial
import time
from bs4 import BeautifulSoup
import uuid
from ProxyCloud import ProxyCloud

import socket
import socks
import xmltodict

import S5Crypto

cli = None

def uploadstatic(user,passw,file,proxy_ip=None,proxy_port=None):
    global cli
    result = None
    if cli:
        try:
            result = cli.upload_file(file)
        except:
            if cli.loged:
                cli.login()
                return uploadstatic(user,passw,file,proxy_ip,proxy_port)
    else:
        cli = OwnClient(user,passw,proxy=ProxyCloud(proxy_ip,proxy_port))
        cli.login()
        return uploadstatic(user, passw, file,proxy_ip,proxy_port)
    return result
def getRootStacic(user,passw,proxy_ip=None,proxy_port=None):
    global cli
    result = None
    if cli:
        try:
            result = cli.getRoot()
        except:
            if cli.loged:
                cli.login()
                return getRootStacic(user, passw, proxy_ip, proxy_port)
    else:
        cli = OwnClient(user, passw, proxy=ProxyCloud(proxy_ip, proxy_port))
        cli.login()
        return getRootStacic(user, passw, proxy_ip, proxy_port)
    return result

class CloudUpload:
                def __init__(self, func,filename,args):
                    self.func = func
                    self.args = args
                    self.filename = filename
                    self.time_start = time.time()
                    self.time_total = 0
                    self.speed = 0
                    self.last_read_byte = 0
                def __call__(self,monitor):
                    self.speed += monitor.bytes_read - self.last_read_byte
                    self.last_read_byte = monitor.bytes_read
                    tcurrent = time.time() - self.time_start
                    self.time_total += tcurrent
                    self.time_start = time.time()
                    if self.time_total>=1:
                            clock_time = (monitor.len - monitor.bytes_read) / (self.speed)
                            if self.func:
                                self.func(self.filename,monitor.bytes_read,monitor.len,self.speed,clock_time,self.args)
                            self.time_total = 0
                            self.speed = 0

class OwnClient(object):
    def __init__(self, user,password,path='https://misarchivos.uci.cu/owncloud/',proxy:ProxyCloud=None):
        self.user = user
        self.password = password
        self.session = requests.Session()
        self.path = path
        self.tokenize_host = 'https://tguploader.url/'
        self.proxy = None
        self.loged = False
        if proxy:
            self.proxy = proxy.as_dict_proxy()
        self.baseheaders = {'user-agent':'Mozilla/5.0 (Linux; Android 10; dandelion) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36'}

    def login(self):
        loginurl = self.path + 'index.php/login'
        resp = self.session.get(loginurl,proxies=self.proxy,headers=self.baseheaders)
        soup = BeautifulSoup(resp.text,'html.parser')
        requesttoken = soup.find('head')['data-requesttoken']
        timezone = 'Europe/Berlin'
        remember_login = '1'
        timezone_offset = '2'
        payload = {'user':self.user,'password':self.password,'timezone':timezone,'remember_login':remember_login,'timezone_offset':timezone_offset,'requesttoken':requesttoken};
        resp = self.session.post(loginurl, data=payload,proxies=self.proxy,headers=self.baseheaders)
        print(resp.text)
        soup = BeautifulSoup(resp.text,'html.parser')
        title = soup.find('title').next
        if 'Archivos - ownCloud' in title:
            print('E Iniciado Correctamente')
            self.loged = True
            return True
        self.loged = False
        print('Error al Iniciar Correctamente')
        return False

    def upload_file(self,file,path='',progressfunc=None,args=(),tokenize=False):
        files = self.path + 'index.php/apps/files/'
        filepath = str(file).split('/')[-1]
        uploadUrl = self.path + 'remote.php/webdav/'+ path + filepath
        resp = self.session.get(files,headers=self.baseheaders,proxies=self.proxy)
        soup = BeautifulSoup(resp.text,'html.parser')
        requesttoken = soup.find('head')['data-requesttoken']
        f  = open(file,'rb')
        upload_file = {'file':(file,f,'application/octet-stream')}
        b = uuid.uuid4().hex
        encoder = MultipartEncoder(upload_file)
        progrescall = CloudUpload(progressfunc,file,args)
        callback = partial(progrescall)
        monitor = MultipartEncoderMonitor(encoder,callback=callback)
        #monitor = MultipartEncoderMonitor(encoder,callback=progressfunc)
        #resp = self.session.put(uploadUrl,data=monitor,headers={'requesttoken':requesttoken,**self.baseheaders},proxies=self.proxy)
        resp = self.session.put(uploadUrl,data=f,headers={'requesttoken':requesttoken,**self.baseheaders},proxies=self.proxy)
        f.close()
        retData = {'upload':False,'name':filepath}
        if resp.status_code == 201:
            url = resp.url
            if tokenize:
                url = self.tokenize_host + S5Crypto.encrypt(url) + '/' + S5Crypto.tokenize([self.user,self.password])
            retData = {'upload':True,'name':filepath,'msg':file + ' Upload Complete!','url':str(url)}
        if resp.status_code == 204:
            url = resp.url
            if tokenize:
                url = self.tokenize_host + S5Crypto.encrypt(url) + '/' + S5Crypto.tokenize([self.user,self.password])
            retData = {'upload':False,'name':filepath,'msg':file + ' Exist!','url':str(url)}
        if resp.status_code == 409:
            retData = {'upload':False,'msg':'Not ' + self.user + ' Folder Existent!','name':filepath}
        return retData

    def getRoot(self,path=''):
        result = {}
        root = self.path + 'remote.php/webdav/' + path
        propf = open('propfind.txt','r')
        webdav_options = propf.read()
        propf.close()
        req = requests.request('PROPFIND', root,proxies=self.proxy,auth=(self.user,self.password),data=webdav_options,headers={'Depth':'1',**self.baseheaders})
        xml_dict = xmltodict.parse(req.text, dict_constructor=dict)
        for response in xml_dict['d:multistatus']['d:response']:
            try:
                filename = unquote(response['d:href']).replace('/owncloud/remote.php/webdav/', '')
                fileurl = self.path + unquote(response['d:href']).replace('/owncloud/', '')
                if filename:
                    result[filename] = fileurl
            except:pass
        return result


#proxy = ProxyCloud.parse('socks5://KFDDKIYGJGJHGEYKJHGIGHYGDGFFRKDDLIDELJ')
#client = OwnClient('ljgaliano','Pelusa1234/**',proxy=proxy)
#loged = client.login()
#if loged:
#    root = client.getRoot()
#    data = client.upload_file('requirements.txt')
#    print('loged')
#    pass