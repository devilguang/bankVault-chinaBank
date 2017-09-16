# encoding=UTF-8
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
import math
import datetime
import shortuuid
from webServiceAPI import *


# Create your models here.
class gsUserManager(models.Manager):
    def createUser(self, **kwargs):
        nickName = kwargs['nickName']
        type = kwargs['type']
        password = kwargs['password']
        organization = kwargs['organization']
        department = kwargs['department']
        # 生成User
        u = User.objects.order_by('-id')  # User类操作的是数据库中的auth_user表，u是一个对象列表，按照id倒叙排列
        if 0 != u.count():
            username = 'user{0}'.format(u[0].id + 1)  #
        else:
            username = 'user'
        user = User.objects.create_user(username=username, password=password)

        # 先在auth_user表中创建用户，再在gsinfo_gsUser表中创建用户
        if user:
            gsUser.objects.get_or_create(user=user,
                                         nickName=nickName,
                                         organization=organization,
                                         department=department,
                                         type=type)

            return

    def deleteUser(self, **kwargs):
        nickName = kwargs['nickName']
        # 删除用户名为nickName的作业, admin用户为系统默认用户,不能删除
        # 注意：Django将根据nickName的值进行"级联"删除
        if nickName != 'sysadmin':
            try:
                user = super(models.Manager, self).get(nickName=kwargs['nickName'])  # 用超级用户身份来删除
                user.delete()
                deletedUser = True
            except ObjectDoesNotExist:
                deletedUser = False
        else:
            deletedUser = False  # 这里是否有问题？应该为False？

        return deletedUser


class gsUser(models.Model):
    user = models.OneToOneField(User)  # OneToOneField(someModel) 可以理解为 ForeignKey(SomeModel, unique=True)
    type = models.PositiveIntegerField(verbose_name='用户类型（0:超级管理员 1:管理员 2:一般用户）')
    nickName = models.CharField(verbose_name='用户名',max_length=255, unique=True)
    organization = models.CharField(verbose_name='用户所在组织',max_length=255,null=True)
    department = models.CharField(verbose_name='用户所在部门',max_length=255,null=True)
    auth = models.BooleanField(verbose_name='授权管理岗位权限（True:拥有 False:未拥有）',default=False)
    manage = models.BooleanField(verbose_name='实物分发岗位权限（True:拥有 False:未拥有）',default=False)
    numbering = models.BooleanField(verbose_name='外观信息采集权限（True:拥有 False:未拥有）',default=False)
    analyzing = models.BooleanField(verbose_name='频谱分析岗位权限（True:拥有 False:未拥有）',default=False)
    measuring = models.BooleanField(verbose_name='测量称重岗位权限（True:拥有 False:未拥有）',default=False)
    checking = models.BooleanField(verbose_name='实物认定岗位权限（True:拥有 False:未拥有）',default=False)
    photographing = models.BooleanField(verbose_name='图像采集岗位权限（True:拥有 False:未拥有）',default=False)
    '''
    当我们对gsUser进行操作时，必然是通过gsUser.objects来进行的，gsUser.objects除了固有的方法（如：
    get、create、update、get_or_create等）外我们还定义的createUser和deleteUser，当我们调用：
    gsUser.objects.createUser()创建新用户时候会先在auth_user中创建用户再在gsinfo_gsuser中创建，当我们
    调用gsUser.objects.createUser()时，会级联删除，即删除auth_user和gsinfo_gsuser中的内容
    '''
    objects = gsUserManager()

    def __unicode__(self):
        return self.nickName


# 针对CharField来说，''(空字符串)等价于NULL
# 箱体
class gsBoxManager(models.Manager):
    # 有两种情况：
    # 一、当要记录实物数据时，实物对应的盒子还没有创建，此时调用createBox，先创建盒子再写入实物信息
    # 二、当要记录实物数据时，实物对应的盒子已存在，此时调用addToExistingBox写入实物信息
    def createBox(self, **kwargs):
        productType = kwargs['productType']
        classNameCode = kwargs['className']
        subClassName = kwargs['subClassName']
        boxNumber = kwargs['boxNumber']
        wareHouseCode = kwargs['wareHouse']
        amount = kwargs['amount']
        grossWeight = kwargs['grossWeight']
        oprateType = kwargs['oprateType']


        # 生成一条Box记录
        prop = gsProperty.objects.get(code=subClassName, parentCode=classNameCode,grandpaCode=productType)
        box, createdBox = super(models.Manager, self).get_or_create(boxNumber=boxNumber,
                                                                    wareHouse=wareHouseCode,
                                                                    amount=amount,
                                                                    grossWeight=grossWeight,
                                                                    oprateType=oprateType,
                                                                    property=prop)





        # 生成实物索引表, 依据实物类型, 在实物索引表生成相应的实物索引记录
        if oprateType == '1':
            # 请求件序号
            # code = '3|{0}'.format(amount)
            # thingSeq = getNumberAPI(code)
            # thingSeq_list = thing_seq.split('|')
            # --------------
            thingSeq_list = []
            for i in range(amount):
                serialNumber = str(shortuuid.ShortUUID().random(length=10))
                thingSeq_list.append(serialNumber)

                # img = qrcode.make(data=serialNumber)
                # pic_name = serialNumber + '.png'
                # box_dir = os.path.join(settings.TAG_DATA_PATH, 'serialNumber', str(boxNumber))
                # if not os.path.exists(box_dir):
                #     os.makedirs(box_dir)  # mkdir
                # filePath = os.path.join(box_dir, pic_name)
                # img.resize((256, 256))
                # img.save(filePath)
            # --------------
            thingsList = []
            for thing in thingSeq_list:
                thingsList.append(gsThing(serialNumber=thing, box=box, property=prop,amount=1))
            gsThing.objects.bulk_create(thingsList)  # bulk_create批量数据入库，参数是list
        elif oprateType == '2':
            # 请求件序号
            # code = '3|{0}'.format(1)
            # thingSeq = getNumberAPI(code)
            # --------------
            serialNumber = str(shortuuid.ShortUUID().random(length=5))
            # img = qrcode.make(data=serialNumber)
            # pic_name = serialNumber + '.png'
            # box_dir = os.path.join(settings.TAG_DATA_PATH, 'serialNumber', str(boxNumber))
            # if not os.path.exists(box_dir):
            #     os.makedirs(box_dir)  # mkdir
            # filePath = os.path.join(box_dir, pic_name)
            # img.resize((256, 256))
            # img.save(filePath)
            # --------------
            gsThing.objects.create(gsThing(serialNumber=serialNumber, box=box, property=prop, amount=amount))
        elif oprateType == '3':
            pass



    def addToExistingBox(self, **kwargs):
        productType = kwargs['productType']
        classNameCode = kwargs['className']
        boxNumber = kwargs['boxNumber']
        subClassNameCode = kwargs['subClassName']
        wareHouseCode = kwargs['wareHouse']
        amount = kwargs['amount']
        startSeq = kwargs['startSeq']
        subBoxNumber = kwargs['subBoxNumber']


        box = super(models.Manager, self).get(boxNumber=boxNumber)

        thingsList = []
        subBoxSeq = gsThing.objects.filter(box=box).order_by('-subBoxSeq')[0].subBoxSeq + 1

        # 生成实物索引记录
        for _ in range(amount):
            serialNumber = classNameCode + '-' + subClassNameCode + '-' + wareHouseCode + '-' + str(startSeq)
            if subBoxNumber == '':
                thingsList.append(gsThing(serialNumber=serialNumber, seq=startSeq, box=box, subBoxSeq=subBoxSeq,))
            else:
                thingsList.append(gsThing(serialNumber=serialNumber, seq=startSeq, box=box, subBoxSeq=subBoxSeq))
            startSeq = startSeq + 1

        gsThing.objects.bulk_create(thingsList)
        super(models.Manager, self).filter(boxNumber=boxNumber).update(amount=amount + box.amount)

        return (box, True)

    def deleteBox(self, **kwargs):
        # 删除箱号为boxNumber的作业
        # 注意：Django将根据gsBox的"ID"值进行"级联"删除
        try:
            box = super(models.Manager, self).get(boxNumber=kwargs['boxNumber'])
            id = box.id
            box = super(models.Manager, self).get(id=id)
            box.delete()
            deletedBox = True
        except ObjectDoesNotExist:
            deletedBox = False

        return deletedBox

# 属性表
class gsProperty(models.Model):
    project = models.CharField(max_length=255)  # 项目
    type = models.CharField(max_length=255)  # 类型
    code = models.CharField(max_length=255, blank=True)  # 代码

    parentProject = models.CharField(max_length=255, blank=True)  # 父项目
    parentType = models.CharField(max_length=255, blank=True)  # 父类型
    parentCode = models.CharField(max_length=255, blank=True)  # 父代码

    grandpaProject = models.CharField(max_length=255, blank=True)  # 祖项目
    grandpaType = models.CharField(max_length=255, blank=True)  # 祖类型
    grandpaCode = models.CharField(max_length=255, blank=True)  # 祖代码

# 箱体实物表
class gsBox(models.Model):
    boxNumber = models.CharField(verbose_name='货发二代系统提供的箱号',max_length=255,unique=True)
    wareHouse = models.CharField(verbose_name='发行库', max_length=255, unique=True)
    amount = models.PositiveIntegerField(verbose_name='件数',)
    grossWeight = models.FloatField(verbose_name='总毛重',null=True)
    status = models.BooleanField(verbose_name='封箱状态（False:未封箱; True：已封箱入库）',default=False)
    oprateType = models.BooleanField(verbose_name='操作类型', default=False) # 1、逐一查验，2、同质同类查验、3较大存量查验
    property = models.ForeignKey(gsProperty)

    objects = gsBoxManager()
    class Meta:
        ordering = ['boxNumber']

# 作业
class gsWorkManager(models.Manager):
    # work的开始前提是在box已经存在的基础上
    def createWork(self, **kwargs):
        subBoxNumber = kwargs['subBoxNumber']
        box = gsBox.objects.get(boxNumber=kwargs['boxNumber'])
        # 生成一条Work记录
        if subBoxNumber == '':
            ws = super(models.Manager, self).filter(box=box).order_by('-workSeq')
            if ws.count() != 0:
                workSeq = ws[0].workSeq + 1
            else:
                workSeq = 1
            work, createdWork = super(models.Manager, self).get_or_create(workSeq=workSeq, box=box,
                                                                          workName=kwargs['workName'],
                                                                          manager=kwargs['operator'])
        else:
            subBox = gsSubBox.objects.get(box=box,subBoxNumber=subBoxNumber)
            ws = super(models.Manager, self).filter(box=box,subBox=subBox).order_by('-workSeq')
            if ws.count() != 0:
                workSeq = ws[0].workSeq + 1
            else:
                workSeq = 1
            work, createdWork = super(models.Manager, self).get_or_create(workSeq=workSeq, box=box,
                                                                          workName=kwargs['workName'],
                                                                          manager=kwargs['operator'],
                                                                          subBox=subBox)

        if createdWork:  # 该条记录为新增记录, 即为新创建作业
            # 依据实物类型, 在实物属性表中生成对应的实物信息档案, 以及实物信息采集状态记录
            productTypeCode = box.productType
            ts = kwargs['thingSet']

            if ('1' == productTypeCode):  # 金银锭类
                info = gsDing
                infoManager = gsDing.objects
            elif ('2' == productTypeCode):  # 金银币章类
                info = gsBiZhang
                infoManager = gsBiZhang.objects
            elif ('3' == productTypeCode):  # 银元类
                info = gsYinYuan
                infoManager = gsYinYuan.objects
            elif ('4' == productTypeCode):  # 金银工艺品类
                info = gsGongYiPin
                infoManager = gsGongYiPin.objects

            infosList = []
            statusList = []
            for serialNumber in ts:
                thing = gsThing.objects.get(serialNumber=serialNumber)
                # 生成一条实物信息档案记录
                infosList.append(info(thing=thing))
                # 生成一条实物信息采集状态记录
                statusList.append(gsStatus(thing=thing))

            infoManager.bulk_create(infosList)
            gsStatus.objects.bulk_create(statusList)

            # 更新实物的作业分配状态
            gsThing.objects.filter(serialNumber__in=ts).update(isAllocate=True,work=work)

        return (work, createdWork)

    def deleteWork(self, **kwargs):
        # 删除序号为workSeq的作业
        boxNumber = int(kwargs['boxNumber'])
        workSeq = kwargs['workSeq']
        try:
            box = gsBox.objects.get(boxNumber=boxNumber)
            work = super(models.Manager, self).get(box=box, workSeq=workSeq)
            # 删除实物信息档案记录和实物信息采集状态记录
            productTypeCode = box.productType
            work_things = gsThing.objects.filter(work=work)

            if ('1' == productTypeCode):  # 金银锭类
                infoManager = gsDing.objects
            elif ('2' == productTypeCode):  # 金银币章类
                infoManager = gsBiZhang.objects
            elif ('3' == productTypeCode):  # 银元类
                infoManager = gsYinYuan.objects
            elif ('4' == productTypeCode):  # 金银工艺品类
                infoManager = gsGongYiPin.objects

            n = len(work_things)
            if n > 0:
                infoManager.filter(thing__in=work_things).delete()
                gsStatus.objects.filter(thing__in=work_things).delete()
                work_things.update(isAllocate=False)

            work.delete()
            deletedWork = True
        except ObjectDoesNotExist:
            deletedWork = False

        return deletedWork


# 清点查验作业表
class gsWork(models.Model):
    workSeq = models.PositiveIntegerField()  # 作业序号, 从1开始
    box = models.ForeignKey(gsBox)  # 箱体, 参照gsBox表"id"列
    workName = models.CharField(max_length=512)  # 作业名称
    createDateTime = models.DateTimeField(default=datetime.datetime.now())  # 作业创建时间, 即实物建档时间
    completeDateTime = models.DateTimeField(null=True)  # 作业完成时间, 即最后一个实物信息采集审核完成时间
    # manager = models.CharField(max_length=512)  # 实物分发岗位
    status = models.PositiveIntegerField(default=0)  # 状态代码: 0:未启用 1:已启用 2:已完成
    objects = gsWorkManager()

    class Meta:
        ordering = ['workSeq', 'createDateTime']

class gsCase(models.Model):
    caseNumber = models.CharField(max_length=255, unique=True, null=False)
    closePerson = models.CharField(verbose_name='封装人',max_length=255, unique=True, null=False)
    closeCheckPerson = models.CharField(verbose_name='封装复核人', max_length=255, unique=True, null=False)
    closeTime = models.DateTimeField(verbose_name='封装时间',default=datetime.datetime.now())
    status = models.BooleanField(verbose_name='是否封盒(False:未封盒 True:已封盒)',default=False)
    box = models.ForeignKey(gsBox)

# 实物索引表
class gsThing(models.Model):
    serialNumber = models.CharField(verbose_name='实物序号',max_length=255,unique=True)
    serialNumber2 = models.CharField(verbose_name='实物编号',max_length=255,unique=True,null=True)
    isAllocate = models.BooleanField(verbose_name='实物是否已分配',default=False)
    historyNo = models.IntegerField(null=True)
    # ------------------实物字段
    level = models.CharField(verbose_name='评价等级', max_length=255, blank=True)
    detailedName = models.CharField(verbose_name='名称',max_length=1024, blank=True)
    peroid = models.CharField(verbose_name='年代',max_length=255, blank=True)
    year = models.CharField(verbose_name='年份', max_length=255, blank=True)
    country = models.CharField(verbose_name='国别', max_length=512, blank=True)
    biFaceAmount = models.CharField(verbose_name='面值', max_length=512, blank=True)
    dingSecification = models.CharField(verbose_name='规格', max_length=512, blank=True)
    zhangType = models.CharField(verbose_name='性质', max_length=512, blank=True)
    gongShape = models.CharField(verbose_name='器型（型制）', max_length=512, blank=True)
    appearance = models.CharField(verbose_name='品相（完残程度）', max_length=255, blank=True)
    mark = models.CharField(verbose_name='铭文（文字信息）', max_length=512, blank=True)
    grossWeight = models.FloatField(verbose_name='毛重', null=True)
    pureWeight = models.FloatField(verbose_name='纯重', null=True)
    originalQuantity = models.FloatField(verbose_name='原标注成色', null=True)
    detectedQuantity = models.FloatField(verbose_name='频谱检测成色', null=True)
    amount = models.PositiveIntegerField(verbose_name='件（枚）数', null=True)
    length = models.FloatField(verbose_name='长度', null=True)
    width = models.FloatField(verbose_name='宽度', null=True)
    height = models.FloatField(verbose_name='高度', null=True)
    # +++这几个字段是货发二代系统不需要的，清点系统的是否还需要？
    # producer = models.CharField(verbose_name='制作人',max_length=512, blank=True)
    # producePlace = models.CharField(verbose_name='制作地',max_length=512, blank=True)
    # versionName = models.CharField(verbose_name='版别',max_length=1024, blank=True)
    # marginShape = models.CharField(verbose_name='边齿',max_length=512, blank=True)
    # +++
    remark = models.TextField(verbose_name='备注', default='')
    # ------------------
    box = models.ForeignKey(gsBox)
    work = models.ForeignKey(gsWork,null=True)
    case = models.ForeignKey(gsCase,null=True)
    property = models.ForeignKey(gsProperty)

# 状态表
class gsStatus(models.Model):
    status = models.BooleanField(default=False)  # 实物状态: False:未完成 True:完成
    close_status = models.BooleanField(default=False)  # 实物是否封袋: False:未完成 True:完成
    incase_status = models.BooleanField(default=False)  # 实物装入盒子: False:未完成 True:完成

    numberingStatus = models.BooleanField(default=False)  # 环节1外观信息采集状态: False:未完成 True:完成
    numberingOperator = models.CharField(max_length=512, blank=True)  # 环节1外观信息采集记录员
    numberingCreateDateTime = models.DateTimeField(default=datetime.datetime.now())  # 环节1外观信息采集记录生成时间
    numberingUpdateDateTime = models.DateTimeField(null=True)  # 环节1外观信息采集记录最近一次修改时间

    analyzingStatus = models.BooleanField(default=False)  # 环节2频谱检测状态: False:未完成 True:完成
    analyzingOperator = models.CharField(max_length=512, blank=True)  # 环节2频谱检测记录员
    analyzingCreateDateTime = models.DateTimeField(default=datetime.datetime.now())  # 环节2频谱检测记录生成时间
    analyzingUpdateDateTime = models.DateTimeField(null=True)  # 环节2频谱检测记录最近一次修改时间

    measuringStatus = models.BooleanField(default=False)  # 环节3测量称重状态: False:未完成 True:完成
    measuringOperator = models.CharField(max_length=512, blank=True)  # 环节3测量称重记录员
    measuringCreateDateTime = models.DateTimeField(default=datetime.datetime.now())  # 环节3测量称重记录生成时间
    measuringUpdateDateTime = models.DateTimeField(null=True)  # 环节3测量称重记录最近一次修改时间

    checkingStatus = models.BooleanField(default=False)  # 环节4数据审核状态: False:未完成 True:完成
    checkingOperator = models.CharField(max_length=512, blank=True)  # 环节4数据审核记录员
    checkingCreateDateTime = models.DateTimeField(default=datetime.datetime.now())  # 环节4数据审核记录生成时间
    checkingUpdateDateTime = models.DateTimeField(null=True)  # 环节4数据审核记录最近一次修改时间

    photographingStatus = models.BooleanField(default=False)  # 环节4数据审核状态: False:未完成 True:完成
    photographingOperator = models.CharField(max_length=512, blank=True)  # 环节4数据审核记录员
    photographingCreateDateTime = models.DateTimeField(default=datetime.datetime.now())  # 环节4数据审核记录生成时间
    photographingUpdateDateTime = models.DateTimeField(null=True)  # 环节4数据审核记录最近一次修改时间

    completeTime = models.DateTimeField(null=True)  # 实物完成时间
    thing = models.ForeignKey(gsThing)

class gsLog(models.Model):
    userID = models.PositiveIntegerField()  # 用户ID
    userName = models.CharField(max_length=255)  # 用户姓名
    organization = models.CharField(max_length=255,null=True)  # 组织
    department = models.CharField(max_length=255,null=True)  # 部门
    operationType = models.CharField(max_length=255)  # 操作类型
    content = models.CharField(max_length=256)  # 内容
    when = models.DateTimeField(default=datetime.datetime.now())  # 操作日期
