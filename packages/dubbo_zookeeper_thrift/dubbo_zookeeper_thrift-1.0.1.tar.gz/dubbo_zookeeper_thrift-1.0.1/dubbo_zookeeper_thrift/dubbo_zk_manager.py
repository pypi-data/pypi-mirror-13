#!/usr/bin/env python
# coding=utf-8

import urllib
import urlparse

from kazoo.client import KazooClient
import logging

from kazoo.protocol.states import KazooState


class DubboZkManager():
    """
    从 zookeeper服务器中取出 某个服务的 ip:port列表,
    如果zookeeper 断开,则从本地缓存中读取数据

    服务提供者在启动的时候,向ZK上的指定节点/dubbo/${serviceName}/providers目录下写入自己的URL地址,这个操作就完成了服务的发布。
    服务消费者启动的时候,订阅/dubbo/${serviceName}/providers目录下的提供者URL地址，
    并向/dubbo/${serviceName}/consumers目录下写入自己的URL地址.
    注意,所有向ZK上注册的地址都是临时节点,这样就能够保证服务提供者和消费者能够自动感应资源的变化.
    另外,Dubbo还有针对服务粒度的监控,方法是订阅/dubbo/${serviceName}目录下所有提供者和消费者的信息.

    """
    zkDataCache = None
    zkClient = None

    def __init__(self, zk_server_str):
        """Constructor for DubboZkManager
            zkServer: "127.0.0.1:2181"
        """
        logging.basicConfig(level=logging.DEBUG)
        self.zkServerStr = zk_server_str
        if DubboZkManager.zkClient is None:
            DubboZkManager.zkClient = KazooClient(hosts=self.zkServerStr)
            logging.debug("zkClient is connecting")

        if DubboZkManager.zkDataCache is None:
            DubboZkManager.zkDataCache = {}
            # {"kkService":[(),(),()]}

        @DubboZkManager.zkClient.add_listener
        def add_zk_listener(state):
            if state == KazooState.LOST:
                print "kazoo is lost"
            elif state == KazooState.SUSPENDED:
                print "kazoo is suspended"
            else:
                print "kazoo is connected/reconnected"

        '''
        make sure Zookeeper is actually running there first, or the start command will be waiting until its default timeout
        '''
        self.zkClient.start()

        logging.info("zkStart.....")

    def get_service_servers(self,zk_service_name):
        """获取某个thrift服务的服务提供者列表
        :param service_name: 接口名或服务名的全限定名
        :return: list (ip,port),(ip,port).... or []
        """
        path="/dubbo/%s/providers"%zk_service_name;
        if not DubboZkManager.zkClient.exists(path):
            logging.error("path:%s not exists"%path)
            return None

        if DubboZkManager.zkDataCache.has_key(path):
            logging.debug("DubboZkManager.zkDataCache = %s"%DubboZkManager.zkDataCache)
            return DubboZkManager.zkDataCache.get(path);

        @DubboZkManager.zkClient.ChildrenWatch(path)
        def watch_children(children):
            print("path %s  children Changed  now: %s" % (path,children))
            if DubboZkManager.zkDataCache.has_key(path):
                del DubboZkManager.zkDataCache[path];
                server_results = self.__children2ipport__(childrens);
                DubboZkManager.zkDataCache[path] = server_results;
            #写入缓存,更新缓存
        childrens = DubboZkManager.zkClient.get_children(path);
        logging.debug("get_service_servers(%s)=%s"%(zk_service_name,childrens));

        server_results = self.__children2ipport__(childrens);
        if len(server_results) > 0 and not DubboZkManager.zkDataCache.has_key(path):
            DubboZkManager.zkDataCache[path]=server_results;
        return server_results


    def __children2ipport__(self,childrens):
        """
        将 从zookeeper里获取的dubbo配置信息转换成[("127.0.0.1",11011),("127.0.0.1",12121)]
        :param childrens:
        :return:
        """
        if len(childrens) < 1:
            raise Exception("没有服务提供者!");
        server_results = []
        for children in childrens:
            url2 = urllib.unquote(children)
            urlparam = urlparse.urlparse(url2)
            print urlparam
            #logging.debug("service_name=%s"%urlparam.)
            logging.debug("\tdubbo service name = %s "%urlparam.path)
            logging.debug("\tdubbo service scheme = %s "%urlparam.scheme)
            logging.debug("\tdubbo service server address = %s"%urlparam.netloc)
            logging.debug("\tdubbo service params = %s"%urlparam.query)
            server_results.append(tuple(urlparam.netloc.split(":",1)))
        return server_results

if __name__ == '__main__':

    manager = DubboZkManager("127.0.0.1:2181");
    manager.get_service_servers("com.alibaba.dubbo.monitor.MonitorService");

    tt = input("input the name of yours")






