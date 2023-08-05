# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from Warriors import *
import operator


class Warrior_Row():

    def __init__(self,obj):
        self.EndPoint=obj.EndPoint
        self.AccessId=obj.AccessId
        self.AccessSecret=obj.AccessSercet
        self.InstanceName=obj.InstanceName


    #定义类变量，分别为主键，表名，更新内容
    __key={}
    __table=None
    __update_attribute={}

    #添加主键
    def add_key(self,name,values):
        '''
          添加主键
        :param name:   主键名
        :param values: 主键值
        :return:
        '''
        if name==None or values==None:
            raise WARRIORS_Error("name or value cannot be empty!")
        else:
            self.__key[name]=values
            return self


    def add_table(self,name):
        '''
            添加表
        :param name: 表名
        :return:
        '''
        self.__table=name
        return self

    def add_update_attribute(self,operation,data):
        '''
           添加更新属性
        :param operation: 操作:["put","delete","modify"]
        :param data:  数据
        :return:
        '''
        if isinstance(data,dict)==True:
            pass
        else:
            WARRIORS_Error("Data must be a dictionary,but is {Type}".format(Type=type(data[0])))
        if operator.eq(operation,"put")==True:
            self.__update_attribute["put"]=data
        elif operation.eq(operation,"delete")==True:
            self.__update_attribute["delete"]=data
        elif operation.eq(operation,"modify")==True:
            self.__update_attribute["put"]=data
        else:raise WARRIORS_Error("Not Support Operation!")
        return self


    def delete(self):
        '''
           删除一行数据
        :return:
        '''
        if self.__key=={} or self.__table==None:
            raise WARRIORS_Error("You must set the Primary Key or table!")
        else:
            try:
                client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
            except :
                raise WARRIORS_Error("Connection failed!")
            try:
                client.delete_row(self.__table,Condition('IGNORE'),self.__key)
                return True
            except:
                raise WARRIORS_Error("Delete Failed!")

    def update(self):
        '''
           更新一行数据
        :return:
        '''
        if self.__update_attribute=={}:
            raise WARRIORS_Error("You must set the attribute!")
        elif self.__table==None:
            raise WARRIORS_Error("You must set the table!")
        elif self.__key==[] or {}:
            raise WARRIORS_Error("You must set the Primary key!")
        else:
            try:
                client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
            except :
                raise WARRIORS_Error("Connection failed!")
            try:
                client.update_row(self.__table,Condition("EXPECT_EXIST"),self.__key,self.__update_attribute)
                return True
            except :
                WARRIORS_Error("Update Failed")



    def get(self,column=None):
        if self.__key==None:
            raise WARRIORS_Error("You must set the Primary Key!")
        else:
            if self.__table==None:
                raise WARRIORS_Error("You must set the table!")
            else:
                if column!=None:
                     if isinstance(column,list)==True:
                         pass
                     else:
                         raise WARRIORS_Error("column must be list!")

                try:
                    client=OTSClient(end_point=self.EndPoint,accessid=self.AccessId,accesskey=self.AccessSecret,instance_name=self.InstanceName)
                    consumed, primary_key_columns, attribute_columns =client.get_row(self.__table,self.__key,column)
                    return {
                        "data":attribute_columns,
                        "CapacityUnit":consumed.read,
                        "key":primary_key_columns
                    }
                except OTSClientError as e:
                    raise WARRIORS_Error(e.get_error_message())
                except OTSServiceError as e:
                    raise WARRIORS_Error(e.get_error_message())

    def set(self,data):
        if self.__key==None:
            raise WARRIORS_Error("You must set the Primary Key!")

        if self.__table==None:raise WARRIORS_Error("You muset set the table!")
        try:
            client=OTSClient(end_point=self.EndPoint,accessid=self.AccessId,accesskey=self.AccessSecret,instance_name=self.InstanceName)
            client.put_row(self.__table,Condition("EXPECT_NOT_EXIST"),self.__key,data)
            return True
        except OTSClientError as e:
            raise WARRIORS_Error(e.get_error_message())
        except OTSServiceError as e:
            raise WARRIORS_Error(e.get_error_message())






