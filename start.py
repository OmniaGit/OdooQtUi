'''
Created on 02 feb 2017

@author: Daniel
'''
import logging
from RPC.rpc import RpcConnection
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

scheme = 'http'
xmlrpcServerIP = '127.0.0.1'
xmlrpcPort = 8069
user = 'admin'
password = 'admin'
dbName = 'plm_9'

rpcInstance = RpcConnection(user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP)
rpcInstance.loginWithUser()

