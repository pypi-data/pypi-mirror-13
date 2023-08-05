# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from warriors import *
import operator


class Warriors_Table():

    #定义类变量
    #__APK   appendPrimaryKey    要添加主键列表
    #__RTP   ReservedThroughput  预留读写吞吐量
    __APK=[]
    __RTP=None

    def __init__(self,obj):
        self.EndPoint=obj.EndPoint
        self.AccessId=obj.AccessId
        self.AccessSecret=obj.AccessSecret
        self.InstanceName=obj.InstanceName



    def add_PrimaryKey(self,name,DataType):
        '''
            添加主键
        :param name:     主键名
        :param DataType: 类型
        :return:
        '''
        if name==None:
            #假如主键名为空
            raise WARRIORS_Error("Name cannot be empty")
        else:
            #假如数据类型不符合要求
            if DataType==None or DataType==1:
                self.__APK.append((name,"INTEGER"))
            elif DataType==2:
                self.__APK.append((name,"STRING"))
            else:
                raise WARRIORS_Error("Not Support this DataType")
            #返回本类
            return self

    def add_ReservedThroughput(self,put,write):
        '''
            添加预留读写吞吐量
        :param write: 写吞吐量
        :param put:   读吞吐量
        :return:
        '''
        if write==None and put==None:
            self.__RTP=ReservedThroughput(CapacityUnit(0, 0))
            return self
        else:
            #假如读写吞吐量 不为数字，则抛出异常
            if str(write).isdigit()==False or str(put).isdigit()==False:
                raise WARRIORS_Error("Write or put must be number!")
            else:
                #假如其中一个为空
                if write==None:
                    write=0
                else:
                    #转化为int
                    write=int(write)
                if put==None:
                    put=0
                else:
                    #转化为int
                    put=int(put)
                self.__RTP=ReservedThroughput(CapacityUnit(put,write))
                #返回本类
                return self



    def CreateTable(self,name):
        '''
            该函数为创建OTS表
        :param cls:
        :return:
        '''
        #假如 连接错误!

        #连接OTS
        try:
            client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
            if client==None or isinstance(client,int)==True:
                return -2
            else:
                pass
        except Exception as e:
            #连接错误
            raise WARRIORS_Error(str(e))

        if self.__APK==[]:
            #必须要设置主键
            raise WARRIORS_Error("You must set the primary key!")

        if self.__RTP==None:
            #必须要设置预留吞吐量
            raise WARRIORS_Error("You must set the Reserved Throughput!")
        #创建表
        table=TableMeta(name,self.__APK)
        try:
            client.create_table(table,self.__RTP)
            #成功之后，返回True
            return True
        except OTSClientError as msg:
            #假如是客户端错误
            raise WARRIORS_Error(msg.get_error_message())
        except OTSServiceError as e:
            #假如是服务端错误
            msg=e.get_error_code()
            if operator.eq(msg,"OTSObjectAlreadyExist")==True:
                raise WARRIORS_Error("The table already exists!")
            else:
                raise WARRIORS_Error(msg)

    def DeleteTable(self,name):
        '''
           删除OTS 表
        :param name: 表名
        :return:
        '''
        try:
            #连接OTS
            client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
            #删除OTS 表
            client.delete_table(name)
            #成功则返回True
            return True
        except OTSServiceError as e:
            #否则抛出异常
            raise WARRIORS_Error(e.get_error_message())
        except OTSClientError as e:
            raise WARRIORS_Error(e.get_error_message())

    def ListTable(self):
        try:
            #连接OTS
            client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
            #遍历OTS表
            table_list=[]
            Append=table_list.append
            list_response=client.list_table()
            for table in list_response:
                Append(table)
            #返回数据列表
            return table_list

        except OTSClientError as e:
            #否则抛出异常
            raise WARRIORS_Error(e.get_error_message())
        except OTSServiceError as e:
            raise WARRIORS_Error(e.get_error_message())

    def adjust(self,write,put,name):
        '''
           调整表的预留读写吞吐量
        :param write:
        :param put:
        :param name:
        :return:
        '''
        if name==None:
            raise WARRIORS_Error("You must set the table!")
        else:
            #假如读为None，则为0
            if write==None:
                write=0
            elif str(write).isdigit()==True:
                write=int(write)
            else:
                write=0
            #假如写为None，则为0
            if put==None:
                put=0
            elif str(put).isdigit()==True:
                put=int(put)
            else:
                put=0

            try:
                #生成预留读写吞吐量
                RTP=ReservedThroughput(CapacityUnit(write,put))
                #连接OTS
                client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
                if client==None or isinstance(client,int)==True:
                    return -2
                else:
                    pass
                #返回回应
                response=client.update_table(name,RTP)
                #返回现在表的预留吞吐量
                return {
                    "put":response.reserved_throughput_details.capacity_unit.read,
                    "write":response.reserved_throughput_details.capacity_unit.put
                }
            except OTSClientError as e:
                #返回错误
                raise WARRIORS_Error(e.get_error_message())
            except OTSServiceError as e:
                #返回错误
                raise WARRIORS_Error(e.get_error_message())

