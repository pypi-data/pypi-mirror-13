#coding:utf8
'''
Created on 2014年2月22日\n
这里定义了两个服务之间进行接口调用的过程\n
@author:  lan (www.9miao.com)\n
'''
from gtwisted.core.protocols import BaseProtocol,ClientFactory,ServerFactory
from gtwisted.core.asyncresultfactory import AsyncResultFactory
from gtwisted.core.error import RPCDataTooLongError
from gevent.timeout import Timeout
import marshal
import struct
import traceback
from gtwisted.utils import log
from gevent import Greenlet,queue
from gevent.threadpool import ThreadPool
import gevent

ASK_SIGNAL = "ASK"#请求结果的信号
NOTICE_SIGNAL = "NOTICE"#仅做通知的信号，不要求返回值
ANSWER_SIGNAL = "ANSWER"#返回结果值的信号
DEFAULT_TIMEOUT = 30#默认的结果返回超时时间
RPC_DATA_MAX_LENGTH = 2147483647#rpc数据包允许的最大长度

class RemoteObject:
    """远程调用对象
    """
    def __init__(self,broker,timeout=DEFAULT_TIMEOUT):
        """
        """
        self.broker = broker
        self.timeout = timeout
        
    def callRemoteForResult(self,_name,*args, **kw):
        """执行远程调用,并等待结果\n
        @param _name: 调用的远程方法的名称\n
        @param timeout: int 结果返回的默认超时时间\n
        @param args: 远程方法需要的参数\n
        @param kw: 远程方法需要的默认参数\n
        """
        _key,result = AsyncResultFactory().createAsyncResult()
        self.broker._sendMessage(_key,_name,args,kw)
        return result.get(timeout=Timeout(self.timeout))
        
    def callRemoteNotForResult(self,_name,*args, **kw):
        """执行远程调用，不需要等待结果\n
        @param _name: 调用的远程方法的名称\n
        @param args: 远程方法需要的参数\n
        @param kw: 远程方法需要的默认参数\n
        """
        self.broker._sendMessage('',_name,args,kw)
        
class Answerer(Greenlet):
    
    def __init__(self,parent):
        Greenlet.__init__(self)
        self.inbox = queue.Queue()
        self.parent_greenlet = parent
        
    def answer(self,request):
        """
        """
        self.inbox.put(request)
        
    def _run(self):
        while True:
            request = self.inbox.get()
            self.parent_greenlet.answerReceived(request)
            
class Asker(Greenlet):
    
    def __init__(self,parent):
        Greenlet.__init__(self)
        self.inbox = queue.Queue()
        self.pool = ThreadPool(2,self)
        self.parent_greenlet = parent
        
    def ask(self,request):
        """
        """
        self.inbox.put(request)
        
    def _run(self):
        while True:
            request = self.inbox.get()
            self.pool.spawn(self.parent_greenlet.askReceived,request)
#             self.parent_greenlet.askReceived(request)
            

        
class PBProtocl(BaseProtocol):
    """RPC协议处理\n
    """
    
    def __init__(self, transport, factory):
        BaseProtocol.__init__(self, transport, factory)
        self.buff = ""
#         self.answerer = Answerer(self)
#         self.asker = Asker(self)
#         self.answerer.start()
#         self.asker.start()
    
    def getRootObject(self,timeout=DEFAULT_TIMEOUT):
        """获取远程调用对象\n
        """
        return RemoteObject(self,timeout=timeout)
    
    def _sendMessage(self,_key,_name,args,kw):
        """发送远程请求\n
        """
        if _key:
            _msgtype = ASK_SIGNAL
        else:
            _msgtype = NOTICE_SIGNAL
        request = marshal.dumps({'_msgtype':_msgtype,'_key':_key,'_name':_name,'_args':args,'_kw':kw})
        self.writeData(request)
        
    def writeData(self,data):
        """发送数据的统一接口\n
        """
        _length = len(data)
        if _length>RPC_DATA_MAX_LENGTH:
            raise RPCDataTooLongError
        self.transport.sendall(struct.pack("!i",_length)+data)
        
    def dataReceived(self, data):
        """数据到达时的处理\n
        """
        self.buff += data
        while len(self.buff)>=4:
            data_length, = struct.unpack('!i',self.buff[:4])
            if len(self.buff[4:])<data_length:
                break
            else:
                request = self.buff[4:4+data_length]
                self.buff = self.buff[4+data_length:]
                gevent.spawn(self.msgResolve,request)
#                 self.msgResolve(request)
    
    def msgResolve(self,data):
        """消息解析\n
        """
        request = marshal.loads(data)
        _msgtype = request['_msgtype']
        if _msgtype==ASK_SIGNAL or _msgtype==NOTICE_SIGNAL:
            self.askReceived(request)
#             self.asker.ask(request)
        elif _msgtype==ANSWER_SIGNAL:
            self.answerReceived(request)
#             self.answerer.answer(request)
            
    def askReceived(self,request):
        """远程调用请求到达时的处理\n
        """
        _key = request['_key']
        _name = request['_name']
        _args = request['_args']
        _kw = request['_kw']
        method = self.getRemoteMethod(_name)
        try:
            result = self.callRemoteMethod(method, _args, _kw)
        except Exception as e:
            result = None
            log.err(_stuff=e,_why=traceback.format_exc())
            error=str(e)
        else:
            error = None
        if _key:
            response = {'_msgtype':ANSWER_SIGNAL,'_key':_key,'result':result,"error":error}
            _response = marshal.dumps(response)
            self.writeData(_response)
        
    def getRemoteMethod(self,_name):
        """获取远程调用的方法对象\n
        """
        method = getattr(self, "remote_%s"%_name)
        return method
        
    def callRemoteMethod(self,method,_args,_kw):
        """调用远程方法\n
        """
        return method(*_args,**_kw)
        
    def answerReceived(self,request):
        """请求的结果返回后的处理\n
        """
        _key = request['_key']
        aresult = AsyncResultFactory().popAsyncResult(_key)
        if request.get("error",""):
            aresult.set(request['result'])
            raise Exception(request.get("error",""))
        else:
            aresult.set(request['result'])
            
    def connectionLost(self, reason):
        """
        """
        BaseProtocol.connectionLost(self, reason)
        self.asker.kill()
        self.answerer.kill()
        


class PBServerProtocl(PBProtocl):
    
    pass

class PBServerFactory(ServerFactory):
    
    protocol = PBServerProtocl
    
        
class PBClientProtocl(PBProtocl):
    
    pass



class PBClientFactory(ClientFactory):
    
    protocol = PBClientProtocl
    
    def getRootObject(self,timeout=DEFAULT_TIMEOUT):
        """获取远程调用对象\n
        """
        return RemoteObject(self._protocol,timeout=timeout)
    
