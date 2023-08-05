# -*- coding: utf-8 -*-
__author__ = 'Administrator'
from warriors import *



class Warriors_Engine():

    '''
     magc_ID            为查阅ID
     magc_unit          为平移单位
     magc_support       为辅助ID
     magc_Columns       为栏目列表
     magc_table         为表名
     __magc_PrimaryKey  为主键设置
     __magc_SliceCount  为切片次数
'''
    magc_ID=None
    magc_unit=0
    magc_support=None
    magc_Columns=[]
    magc_table=None
    magc_data=None
    __magc_PrimaryKey=[]
    __magc_SliceCount=2
    __magc_space=[]
    __space_unit=[]
    def __init__(self,obj):
        self.EndPoint=obj.EndPoint
        self.AccessId=obj.AccessId
        self.AccessSecret=obj.AccessSecret
        self.InstanceName=obj.InstanceName





    def create(self,name=None):
        '''
           创建表
        :param name: 表名
        :return:
        '''
        #假如名字为空，则抛出异常
        name=name or self.magc_table
        if name==None:
            raise WARRIORS_Error("Name cannot be empty")
        try:
            client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
            if client==None or isinstance(client,int)==True:
                return -2
            else:
                pass
        except Exception as e:
            #连接错误
            raise WARRIORS_Error(str(e))

        #设置主键
        PrimaryKey=[('pos', 'INTEGER'), ('id', 'INTEGER'),("support",'INTEGER')]
        #设置预留写吞吐量
        Resered=ReservedThroughput(CapacityUnit(0,0))
        #生成表 类
        table=TableMeta(name,PrimaryKey)
        try:
            #生成表
            client.create_table(table,Resered)
            return True
        except OTSClientError as e:
            raise WARRIORS_Error(e.get_error_message())
        except OTSServiceError as e:
            raise WARRIORS_Error(e.get_error_message())


    def delete_table(self,name=None):
        '''
           删除一个表
        :param name:
        :return:
        '''
        name=name or self.magc_table
        if name==None:
            raise WARRIORS_Error("You must set the table!")
        else:
            try:
                client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
                if client==None or isinstance(client,int)==True:
                    return -2
                else:
                    pass
                client.delete_table(name)
            except OTSServiceError,e:
                raise WARRIORS_Error(e.get_error_message())
            except OTSClientError,e:
                raise WARRIORS_Error(e.get_error_message())

    def list(self):
        '''
           罗列有多少个表
        :return:
        '''

        try:
            #连接OTS
            client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
            if client==None or isinstance(client,int)==True:
                return -2
            else:
                pass
            #取表名
            table_list=client.list_table()
            #赋值
            table=[t for t in table_list]
            return table
        except OTSServiceError,e:
            #连接错误
            raise WARRIORS_Error(str(e.get_error_message()))

    def adjust(self,write,put,name=None):
        name=name or self.magc_table
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







    def Translation(self,unit=1):
        '''
           平移函数，调用该函数增加一个单位
        :param unit: 单位
        :return:
        '''
        #假如单位小于0 或者为空
        if unit<0 or unit==None: raise WARRIORS_Error("Unit cannot be empty")
        #增加一个单位
        self.magc_unit+=unit
        return self

    def add_id(self,ID):
        #假如已经有一个magic ID 值，则用一个数组存储！
        if self.magc_ID!=None:
            if isinstance(self.magc_ID,int)==True or isinstance(self.magc_ID,str)==True or isinstance(self.magc_ID,long)==True:
                self.magc_ID=[self.magc_ID,ID]
            elif isinstance(self.magc_ID,list)==True:
                self.magc_ID.append(ID)
            else:
                raise WARRIORS_Error("Type is Not Support!")
        else:
            self.magc_ID=ID

        #返回了类
        return self

    def add_support(self,support):
        #增加辅助值
        self.magc_support=support
        return self

    def add_GetColumns(self,Columns):
        #假如Columns 为列表
        if isinstance(Columns,list)==True:
            self.magc_Columns=[k for k in Columns]
        elif isinstance(Columns,str)==True:
            self.magc_Columns=[Columns]
        else:
            self.magc_Columns.append(Columns)
        return self

    def add_table(self,table):
        '''
           导入表
           可以导入不存在的表，然后调用create()进行创建！
        :param table:
        :return:
        '''
        #添加表
        self.magc_table=table
        return self

    def add_data(self,data):
        '''
            data 为输入数据

        :param data:
        :return:
        '''
        if data==None:
            raise WARRIORS_Error("data cannot be empty")
        else:
            if isinstance(data,dict)==False:
                raise WARRIORS_Error("Data must be Dict!")
            self.magc_data=data
        return self





    def range(self,total=100):
        #判断self.mac_id是否符合要求
        if self.magc_ID==None or self.magc_ID=="":
            raise WARRIORS_Error("ID Cannot be empty!")
        elif isinstance(self.magc_ID,str)==True or isinstance(self.magc_ID,int)==True or isinstance(self.magc_ID,long)==True:
            inclusive_id=self.magc_ID
            exclusive_id=self.magc_ID
        elif isinstance(self.magc_ID,list)==True:
            inclusive_id=self.magc_ID[0]
            exclusive_id=self.magc_ID[1]
        else:
            raise WARRIORS_Error("Type of ID is Not Support!")

        #假如单位为空
        if self.magc_unit==None:
            self.magc_unit=0

        if self.magc_table==None:
            raise WARRIORS_Error("You must set the table!")
        elif self.magc_Columns==[]:
            self.magc_Columns=None




        #设置最低值
        inclusive={"pos":self.magc_unit,"id":inclusive_id,"support":INF_MIN}
        #设置最大值
        exclusive={"pos":self.magc_unit,"id":exclusive_id,"support":INF_MAX}
        #链接OTS
        try:
            client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
            if client==None or isinstance(client,int)==True:
                return -2
            else:
                pass
        except Exception as e:
            #连接错误
            raise WARRIORS_Error(str(e))

        #查询范围
        try:
            consumed, next_start_primary_key, row_list = client.get_range(self.magc_table, 'FORWARD',inclusive, exclusive,self.magc_Columns,total)
            data=[{"key":r[0],"data":r[1]} for r in row_list]
            return {
                "data":data,"CapacityUnit":consumed.read
            }

        except OTSClientError as e:
            raise WARRIORS_Error(e.get_error_message())
        except OTSServiceError as e:
            raise WARRIORS_Error(e.get_error_message())

    def nicety(self):
        '''
           nicety 为精确查询函数
           在调用之前，必须设置文章ID，文章所在表，文章辅助ID，想要得到的栏目等等！

        :return:
        '''
        #判断魔方参数是否为空
        if self.magc_ID==None:
            raise WARRIORS_Error("You must set the ID!")
        elif self.magc_table==None:
            raise WARRIORS_Error("You must set the table!")
        elif self.magc_support==None:
            self.magc_support=0
        else:
            pass

        if self.magc_Columns==[] or self.magc_Columns==None:
            self.magc_Columns=None

        #假如魔方单位为空
        if self.magc_unit==None:
            self.magc_unit=0

        #链接OTS
        try:
            client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
            if client==None or isinstance(client,int)==True:
                return -2
            else:
                pass
        except OTSClientError as e:
            raise WARRIORS_Error(e.get_error_message())
        except OTSServiceError as e:
            raise WARRIORS_Error(e.get_error_message())
        #假如链接成功！
        #则进行下一步
        #组建Primary Key

        PrimaryKey={"pos":self.magc_unit,"id":self.magc_ID,"support":self.magc_support}
        #可以查询
        try:
            consumed, primary_key_columns, attribute_columns =client.get_row(self.magc_table,PrimaryKey,self.magc_Columns)
            return {
                "data":attribute_columns,
                "key":primary_key_columns,
                "CapacityUnit":int(consumed.read)
            }
        except OTSClientError as e:
            #查询失败！
            raise WARRIORS_Error(e.get_error_message())
        except OTSServiceError as e:
            raise WARRIORS_Error(e.get_error_message())

    def slice(self,setting):
        '''
           slice 为切片转换函数，该函数传入要slice 的栏目名字和数据自动进行切片！
        :param slice_column:
        :param data:
        :return:
        '''
        #data
        data=self.magc_data or None
        if data==None:
            #导入数据流
            raise WARRIORS_Error("You must set the data!")
        #假如出现副ID 有没有设置pos ，抛出异常！
        mid=None
        PrimaryKey=[]
        #遍历setting
        for k,v in setting.items():
            if k not in self.magc_data:raise WARRIORS_Error("Data Do not have {k}".format(k))
            PrimaryKey.append({"id":self.magc_data.get(k),"pos":0,"support":0} if v==0 else {"id":self.magc_data.get(k),"pos":v,"support":mid or None})
            #假如为主键，则设置mid值
            if v==0:mid=data.get(k)

        #假如没有主键
        if mid==None:raise WARRIORS_Error("You do not set the main!")
        for p in PrimaryKey:
            if p.get("pos")!=0:
                p["support"]=mid
                self.__magc_PrimaryKey.append(p)
            else:
                self.__magc_PrimaryKey.append(p)
        return self




    def set(self):
        '''
           添加一条新的数据，本函数是调用batchWrite.在调用本函数，我建议您能调用slice 进行切片转换！

        :return:
        '''
        if self.__magc_space!=[]:
            raise WARRIORS_Error("please call the realize()!")
        elif self.magc_table==None or self.magc_data==None or isinstance(self.magc_data,dict)==False:
            raise WARRIORS_Error("Table or data cannot be empty!")
        else:
            if self.__magc_PrimaryKey==None or self.__magc_PrimaryKey==[] or self.__magc_PrimaryKey=={}:
                raise WARRIORS_Error("You must set the Primary Key!")
            elif isinstance(self.__magc_PrimaryKey,list):
                pass
            else:
                raise WARRIORS_Error("Primary Key is Not Support!")

            #性能优化
            put=[PutRowItem(Condition('EXPECT_NOT_EXIST'),p,self.magc_data) for p in self.__magc_PrimaryKey ]

            #添加一条put table
            table_item={"table_name":self.magc_table,"put":put}
            try:
                client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
                if client==None or isinstance(client,int)==True:
                    return -2
                else:
                    pass
                #写入数据
                response=client.batch_write_row([table_item])
                for r in response:
                    if r.get("put")==None:
                        raise WARRIORS_Error("Error!")
                    else:
                        for p in r.get("put"):
                            if p.is_ok==True:
                                continue
                            else:
                                raise WARRIORS_Error(p.error_message)
                        return True
            except OTSServiceError as e:
                raise WARRIORS_Error(e.get_error_message())
            except OTSClientError as e:
                raise WARRIORS_Error(e.get_error_message())

    def update(self):
        '''
           更新数据
        :return:
        '''
        if self.__magc_PrimaryKey==[] or self.__magc_PrimaryKey==None:
            if self.magc_ID==None:
                raise WARRIORS_Error("You must set the Primary Key!")
            else:
                PrimaryKey=[{"pos":0,"id":self.magc_ID,"support":self.magc_support or 0}]
        else:
            PrimaryKey=self.__magc_PrimaryKey



        if self.magc_data==None or self.magc_data==[] or self.magc_data=={}:
            raise WARRIORS_Error("You must set the Data!")
        elif self.magc_table==False or self.magc_table==[] or self.magc_table=={}:
            raise WARRIORS_Error("You must set the table!")

        UpdateMagcData={
            "put":self.magc_data
        }

        #性能优化
        update_item=[UpdateRowItem(Condition("IGNORE"),k,UpdateMagcData) for k in PrimaryKey]

        #生成table item
        table_item=[{"table_name":self.magc_table,"update":update_item}]
        #连接OTS
        try:
            client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
            if client==None or isinstance(client,int)==True:
                return -2
            else:
                pass
            result=client.batch_write_row(table_item)
            for r in result:
                if r.get("update")==None:
                    raise WARRIORS_Error("Error!")
                else:
                    for u in r.get("update"):
                        if u.is_ok==True:
                            continue
                        else:
                            raise WARRIORS_Error(u.error_message)
            return True
        except OTSServiceError as e:
            #连接错误
            raise WARRIORS_Error(e.get_error_message())
        except OTSClientError as  e:
            #连接错误
            raise WARRIORS_Error(e.get_error_message())




    def delete(self):
        '''

        :return:
        '''
        if self.__magc_PrimaryKey==[] or self.__magc_PrimaryKey==None:
            if self.magc_ID==None:
                raise WARRIORS_Error("You must set the Primary Key!")
            else:
                PrimaryKey=[{"pos":0,"id":self.magc_ID,"support":self.magc_support or 0}]
        else:
            PrimaryKey=self.__magc_PrimaryKey

        if self.magc_table==None:
            raise WARRIORS_Error("You must set the table!")

        delete_item=[DeleteRowItem(Condition('IGNORE'),k) for k in PrimaryKey]
        table_items=[{"table_name":self.magc_table,"delete":delete_item}]
        try:
            client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
            if client==None or isinstance(client,int)==True:
                return -2
            else:
                pass
            result=client.batch_write_row(table_items)
            for r in result:
                if r.get("delete")==None:
                    raise WARRIORS_Error("Delete Failed!")
                else:
                    for d in r.get("delete"):
                        if d.is_ok==True:
                            continue
                        else:
                            raise WARRIORS_Error(d.error_message)
            return True
        except OTSClientError as e:
            raise WARRIORS_Error(e.get_error_message())
        except OTSServiceError as e:
            raise WARRIORS_Error(e.get_error_message())

    def add_space(self,columns=None,unit=None):
        '''
             增加空间，本函数为了实现不同POS 不同属性而开发出来.columns 为属性设置，一定为数组形式。假如为None,则为全部属性。而unit 为int ，假如为None ，则默认为0

        :param columns: 要取得属性名字列表
        :param unit:    pos id 值
        :return:
        '''

        if self.magc_data==None or self.magc_data==[]:
            raise WARRIORS_Error("You must set the data!")
        elif self.__magc_PrimaryKey==[]:
            raise WARRIORS_Error("You must slice the Primary Key!")
        else:
            unit=unit or 0
            if columns==None:
                data=self.magc_data
            else:
                data={c:self.magc_data.get(c) for c in columns if self.magc_data.get(c)!=None}
            if isinstance(unit,int)==True:
                space=[PutRowItem(Condition("EXPECT_NOT_EXIST"),p,data) for p in self.__magc_PrimaryKey if p.get("pos")==unit]
                self.__magc_space+=space
                self.__space_unit.append(unit)
                return self
            else:
                raise WARRIORS_Error("Units must be numeric!")

    def remain(self):
        '''
          假如用户是个别的位置需要调整，剩下的都希望要全部属性，就可以调用本函数!
        :return:
        '''
        if self.magc_data==None or self.magc_data==[]:
            raise WARRIORS_Error("You must set the data!")
        elif self.__magc_PrimaryKey==[]:
            raise WARRIORS_Error("You must slice the Primary Key!")
        else:
            space=[PutRowItem(Condition("EXPECT_NOT_EXIST"),p,self.magc_data) for p in self.__magc_PrimaryKey if p.get("pos") not in self.__space_unit]
            self.__magc_space+=space

        return self







    def realize(self):
        '''
          realize 在调用之前，必须要调用add_space函数，来增加空间。本函数是针对不同的pos增加不同属性为开发出来的，如果你是不同pos，上传相同的数据的话，请使用set函数
          不同pos，上传不同的数据好处就是有效减少数据重复性，节约成本，加快速度。例如：我们建立一个用户列表，pos:0，id:1，属性可以是全部，但是当pos:1，id:1的时候我就不需要全部属性，我只需要其中一个两个就行了，那我在
           写入的时候，就要增加空间，告诉系统，unit为0（POS:0），columns就是为None（就是全部属性）,然后在设置unit为1，columns就是为其中一两个属性的名字，然后在调用本函数就可以实现了!
        :return:
        '''

        space=self.__magc_space
        table=self.magc_table
        #假如space为空
        if space==None or space==[]:
            raise WARRIORS_Error("You must set the space!")
        else:
            #假如表为空
            if table==None or table==[]:
                raise WARRIORS_Error("You must set the table!")
            else:
                table=[{"table_name":table,"put":space}]
                #连接OTS
                try:
                    client=OTSClient(self.EndPoint,self.AccessId,self.AccessSecret,self.InstanceName)
                    if client==None or isinstance(client,int)==True:
                        return -2
                    else:
                        pass
                    response=client.batch_write_row(table)
                    #检查是不是每一个行都写入成功！
                    for r in response:
                        if r.get("put")==None:
                            raise WARRIORS_Error("Error!")
                        else:
                            for p in r.get("put"):
                                if p.is_ok==True:
                                    continue
                                else:
                                    raise WARRIORS_Error(p.error_message)
                    #是的话，返回True
                    return True
                except OTSClientError as e:
                    raise WARRIORS_Error(e.get_error_message())
                except OTSServiceError as e:
                    raise WARRIORS_Error(e.get_error_message())







