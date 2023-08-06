#!/usr/bin/env python
# coding=utf-8
from random import choice

import thriftpy
from thriftpy.protocol import TCyBinaryProtocolFactory
from thriftpy.rpc import make_client
from thriftpy.transport import TCyFramedTransportFactory

from dubbo_zookeeper_thrift.dubbo_zk_manager import DubboZkManager

# todo print 换成 log

class BaseThriftClient():
    """ThriftClient基础类,封装自动获取服务的提供者和自己生产是客户端连接的通用方法,并将客户端连接缓存起来"""

    zk_manager = DubboZkManager("127.0.0.1:2181");
    #clientCache存储格式为 {"xxxService":[{"ip:port":client}]}
    clientCache = {}
    def __init__(self, thrift_file_path, service_name, package_name):
        """
        ThriftClient基础类构造方法
        :param thrift_file_path: thrift文件位置
        :param service_name: 服务名  xxxService
        :param package_name: 服务所在包名  cn.jpush.xxx
        :return:
        """
        self.thrift_file_path = thrift_file_path
        self.service_name = service_name
        self.package_name = package_name


    def _init_client_(self):
        """
        从zookeeper里拿到xxService的服务提供者的ip port列表
        一次性初始化某个服务的所有client,写入缓存
        :return:
        """
        moduleName = self.service_name + "_thrift"
        baseThriftClient = thriftpy.load(self.thrift_file_path, module_name=moduleName)
        baseService = getattr(baseThriftClient,self.service_name)
        serverList = BaseThriftClient.zk_manager.get_service_servers(self.package_name+"."+self.service_name)
        # 随机选一个可以成功的 选几次试试
        BaseThriftClient.clientCache[self.service_name]=[]
        for i in range(1,len(serverList)):
            try :
                host,port = serverList[i]
                client = make_client(
                    baseService,
                    host,
                    port,
                    proto_factory=TCyBinaryProtocolFactory(),
                    trans_factory=TCyFramedTransportFactory()
                )
                BaseThriftClient.clientCache.get(self.service_name,[]).append({host+":"+port:client})
                print "client make success"
            except Exception,e:
                print e.message


    def get_client(self):

        moduleName = self.service_name + "_thrift"
        baseThriftClient = thriftpy.load(self.thrift_file_path, module_name=moduleName)
        baseService = getattr(baseThriftClient,self.service_name)
        serverList = BaseThriftClient.zk_manager.get_service_servers(self.package_name+"."+self.service_name)
        # 随机选一个可以成功的 选几次试试
        for i in range(1,len(serverList)):
            try :
                host,port = choice(serverList)
                client = make_client(
                    baseService,
                    host,
                    port,
                    proto_factory=TCyBinaryProtocolFactory(),
                    trans_factory=TCyFramedTransportFactory()
                )
                print "client make success"

                return client
            except Exception,e:
                print e.message


    def get_cached_client(self):
        """
        给python thrift 客户端 去获取thrift client的实例
        :return:
        """

        clientDict = BaseThriftClient.clientCache.get(self.service_name,{})
        if len(clientDict) < 1:
            self._init_client_();

        clientDict = BaseThriftClient.clientCache.get(self.service_name,{})

        if len(clientDict) < 1:
            print "[error]:%s client no service provider , call rocyuan]" % self.service_name
            return None

        return choice(clientDict.values())
