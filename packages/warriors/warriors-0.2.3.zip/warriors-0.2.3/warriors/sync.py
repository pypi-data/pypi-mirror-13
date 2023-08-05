# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from warriors import *

class Warriors_Sync():
    '''
       导入数据值，批量的写入到OTS当中

       函数 from_data()  直接导入数据
       函数 add_table()  添加数据表名
       函数 slice()      切片转换函数
       函数 run()        开始同步



    '''


    def __init__(self,obj):
        self.EndPoint=obj.EndPoint
        self.AccessId=obj.AccessId
        self.AccessSecret=obj.AccessSecret
        self.InstanceName=obj.InstanceName
        self.magc_data=None
        self.__PrimaryKey=[]
        self.__table=None
        self.__cut=None
        self.__setting=None
        self.__need_key=[]
        self.__Put_Row=None


    def slice(self,setting):
        '''
           add_slice 为切片转换函数，该函数传入要slice 的栏目名字和数据自动进行切片！
        :param setting: 参数 ，必须为字典形式 键为栏目名称，值为pos 值为0，None

        :return:
        '''
        self.__setting={}
        normal=[]
        if isinstance(setting,dict)==True:
            for k,v in setting.items():
                if v==0:
                    self.__setting["key"]=k
                else:
                    normal.append(k)
                #保存需要键
                self.__need_key.append(k)
            #向类赋值
            self.__setting["normal"]=normal
            if self.__setting.get("key")!=None:
                return self
            else:
                raise WARRIORS_Error("You must set the key ID！")
        else:
            raise WARRIORS_Error("setting must be dict")

    def add_table(self,name):
        '''
           导入数据表
        :param name:
        :return:
        '''
        if name==None:
            raise WARRIORS_Error("Please enter your table name!")
        else:
            self.__table=name
        return self

    def add_cut(self,columns=None):
        if columns==None:
            raise WARRIORS_Error("You must set the Columns!")
        else:
            #假如栏目不为列表
            if isinstance(columns,list)==True:
                self.__cut=columns
                return self
            else:
                #抛出异常
                raise WARRIORS_Error("column must be list！")


    def from_data(self,data):
        if self.__setting==None or self.__setting=={}:
            raise WARRIORS_Error("You muet set the setting!")
        else:
            if self.__table==None:
                raise WARRIORS_Error("You must set the table!")
            #传入数据必须为json数组
            if isinstance(data,list)==True:
                if isinstance(data,dict)==True:
                    pass
                else:
                    raise WARRIORS_Error("Data must be an array of JSON!")
            else:
                raise WARRIORS_Error("Data must be an array of JSON!")
            #处理之后数据储存！
            Filter_data,After=data,data
            #假如需要裁切的话，则开始裁切数据
            if self.__cut!=None:
                cut=self.__cut+self.__need_key
                for d in data:
                    After=[{c:d.get(c) for c in cut}]
                    Filter_data=[{c:d.get(c) for c in self.__cut}]
                data=After

            #生成主ID的每一行
            k=self.__setting.get("key")
            Row=[PutRowItem(Condition("EXPECT_NOT_EXIST"),{"pos":0,"id":d.get(k),"support":0},Filter_data) for d in data if d.get(k)!=None]
            #再生成辅助ID的
            for n in self.__setting.get("normal"):
                Row+=[PutRowItem(Condition("EXPECT_NOT_EXIST"),{"pos":0,"id":d.get(n),"support":0},Filter_data) for d in data if d.get(n)!=None]

            try:
                #连接OTS
                client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
                table=[{"table_name":self.__table,"put":Row}]
                #取回应
                response=client.batch_write_row(table)
                for r in response:
                    if r.get("put")==None:
                        raise WARRIORS_Error("Error,Back Response!")
                    else:
                        for p in r.get("put"):
                            if p.is_ok==True:
                                continue
                            else:
                                raise WARRIORS_Error(p.error_message)
                        return True
            except OTSClientError as e:
                #抛出异常
                raise WARRIORS_Error(e.get_error_message())
            except OTSServiceError as e:
                #抛出异常
                raise WARRIORS_Error(e.get_error_message())










