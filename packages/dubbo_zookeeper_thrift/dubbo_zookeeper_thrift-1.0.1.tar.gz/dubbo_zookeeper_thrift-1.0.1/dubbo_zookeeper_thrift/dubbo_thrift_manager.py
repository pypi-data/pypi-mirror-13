#!/usr/bin/env python
# coding=utf-8
import os
from random import choice

import thriftpy
from thriftpy.protocol import TCyBinaryProtocolFactory
from thriftpy.rpc import make_client
from thriftpy.transport import TCyFramedTransportFactory

from dubbo_zookeeper_thrift.dubbo_zk_manager import DubboZkManager


class DubboThriftManager():
    """给python 获取所需要服务的host,port的工具类
    """

    # 用来存储client的缓存 {"xxxService":set([client1,client2])}
    # todo cache 的结构可以再改造下 方便删除掉已经挂了的 client
    clientCache = {}
    def __init__(self, ):
        """Constructor for DubboThriftManager"""
        self.zk_manager = DubboZkManager("127.0.0.1:2181");
        if DubboThriftManager.clientCache is None:
            DubboThriftManager.clientCache = {}


    def __new__(cls):
        # 单例
        if not hasattr(cls, 'instance'):
            cls.instance = super(DubboThriftManager, cls).__new__(cls)
        return cls.instance

    def _get_service_providers_(self,service_name):
        """
        得到一个服务的所有提供者的ip和port
        :param service_name:
        :return: [(ip,port),(ip,port)]
        """
        return self.zk_manager.get_service_servers(service_name)

    def get_thrift_client(self,service_name,package_name,thrift_file_path):
        """
        获取 thrift client的工厂方法
        :param service_name:  thrift文件里的service_name
        :param package_name:  java提供方的包名
        :return:
        """
        if len(DubboThriftManager.clientCache.get(service_name,[])) > 0 :
            return choice(DubboThriftManager.clientCache.get(service_name))
        # 服务的全限定名
        fullyQualifiedServiceName = package_name +"."+ service_name
        providerList = self._get_service_providers_(fullyQualifiedServiceName)
        # todo 取消下面的注释
        if len(providerList) < 1:
            return None
        host,port = choice(providerList)
        # debug
        # host = "127.0.0.1"
        # port = 6000
        moduleName = service_name + "_thrift"
        baseThriftClient = thriftpy.load(thrift_file_path, module_name=moduleName)
        baseService = getattr(baseThriftClient,service_name)
        try :
            # todo 正式时取消下面的注释
            client =  make_client(
                baseService,
                host,
                port,
                proto_factory=TCyBinaryProtocolFactory(),
                trans_factory=TCyFramedTransportFactory()
            )

            # todo 这个是测试代码 后删掉
            # client = make_client(baseService,"127.0.0.1",6000)
            print "client make success"
            if  DubboThriftManager.clientCache.has_key(service_name):
                DubboThriftManager.clientCache.get(service_name,[]).append(client)
            else:
                DubboThriftManager.clientCache[service_name]=[client]
            return client
        except Exception,e:
            print e.message

        return None







