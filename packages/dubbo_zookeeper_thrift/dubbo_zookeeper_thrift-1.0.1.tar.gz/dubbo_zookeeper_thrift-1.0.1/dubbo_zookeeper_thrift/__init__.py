#!/usr/bin/env python
# coding=utf-8


from functools import wraps

import time



# todo 不要看这个....
# todo 忽略这个文件不用看 当我测试的


def loadbalance(service,name="random"):
    '''负载均衡,使用在获取 服务提供者的方法上
    :param service:
    :param name:
    :return:
    '''
    # 使用方法 1 当作装饰器作用在调用方法上
    #         2 当作普通方法作为获取服务提供者IP

    """
    Random LoadBalance
        随机，按权重设置随机概率。
        在一个截面上碰撞的概率高，但调用量越大分布越均匀，而且按概率使用权重后也比较均匀，有利于动态调整提供者权重。
    RoundRobin LoadBalance
        轮循，按公约后的权重设置轮循比率。
        存在慢的提供者累积请求问题，比如：第二台机器很慢，但没挂，当请求调到第二台时就卡在那，久而久之，所有请求都卡在调到第二台上。
    LeastActive LoadBalance
        最少活跃调用数，相同活跃数的随机，活跃数指调用前后计数差。
        使慢的提供者收到更少请求，因为越慢的提供者的调用前后计数差会越大。
    ConsistentHash LoadBalance
        一致性Hash，相同参数的请求总是发到同一提供者。
        当某一台提供者挂时，原本发往该提供者的请求，基于虚拟节点，平摊到其它提供者，不会引起剧烈变动。
        算法参见：http://en.wikipedia.org/wiki/Consistent_hashing。
        缺省只对第一个参数Hash，如果要修改，请配置<dubbo:parameter key="hash.arguments" value="0,1" />
        缺省用160份虚拟节点，如果要修改，请配置<dubbo:parameter key="hash.nodes" value="320" />

    """
    if name == "roundrobin":
        pass
    elif name == "leastactive":
        pass
    elif name == "consistenthash":
        pass
    else:# name == random
        pass


    server_list=[("127.0.0.1",9090)]
    # def _loadbalance(function,server_list):
    #     @wraps(function)
    #     def __loadbalance(*args,**kws):
    #
    #         pass

def record_execute(service,server,params,success):
    """作为dubbo监控,暂时还没有去看dubbo源码里面是以什么方式写进去了,有空再看需要补充这一段监控
    Args:
    Returns:
        
    """
    # todo 以某种格式将统计数据写入 zookeeper 监控python的调用行为
    print "service : %s, server:%s, params:%s, success:%s, time:%s"%(service,server,params,success,time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()))

    
