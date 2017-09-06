# encoding=UTF-8
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
import math


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
    type = models.PositiveIntegerField()  # 用户类型: 0:超级管理员 1:管理员 2:一般用户
    nickName = models.CharField(max_length=255, unique=True)  # 昵称
    organization = models.CharField(max_length=255,null=True)  # 用户所在组织
    department = models.CharField(max_length=255,null=True)  # 用户所在部门
    auth = models.BooleanField(default=False)  # 各种打印等授权管理: True:拥有 False:未拥有
    manage = models.BooleanField(default=False)  # 实物分发岗位权限: True:拥有 False:未拥有
    numbering = models.BooleanField(default=False)  # 外观信息采集权限: True:拥有 False:未拥有
    analyzing = models.BooleanField(default=False)  # 频谱分析权限: True:拥有 False:未拥有
    measuring = models.BooleanField(default=False)  # 测量称重权限: True:拥有 False:未拥有
    checking = models.BooleanField(default=False)  # 数据审核权限: True:拥有 False:未拥有
    photographing = models.BooleanField(default=False)  # 图像采集岗位权限: True:拥有 False:未拥有
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
        boxSeq = kwargs['boxSeq']
        thing_num = kwargs['thing_num']

        # 生成一条Box记录
        box, createdBox = super(models.Manager, self).get_or_create(boxNumber=boxNumber,
                                                                    productType=productType,
                                                                    className=classNameCode,
                                                                    subClassName=subClassName,
                                                                    wareHouse=wareHouseCode,
                                                                    amount=amount,
                                                                    grossWeight=grossWeight,
                                                                    boxSeq=boxSeq)

        # 生成实物索引表, 依据实物类型, 在实物索引表生成相应的实物索引记录
        thing_num_list = thing_num.split('|')
        thingsList = []
        for thing in thing_num_list:
            thingsList.append(gsThing(serialNumber=thing,box=box,subClassName=subClassName))
        gsThing.objects.bulk_create(thingsList)  # bulk_create批量数据入库，参数是list
        return (box, createdBox)

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
                subBox = gsSubBox.objects.get(box=box,subBoxNumber=subBoxNumber)
                thingsList.append(gsThing(serialNumber=serialNumber, seq=startSeq, box=box, subBoxSeq=subBoxSeq,subBox=subBox))
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


# 箱体实物表
class gsBox(models.Model):
    boxNumber = models.PositiveIntegerField(unique=True)  # 箱号
    boxSeq = models.CharField(max_length=255,unique=True)  # 货发二代系统提供的箱号
    productType = models.CharField(max_length=255)  # 实物类型
    className = models.CharField(max_length=255)  # 品名
    subClassName = models.CharField(max_length=255, null=False)  # 明细品名
    wareHouse = models.CharField(max_length=255)  # 所属发行库
    amount = models.PositiveIntegerField()  # 件数
    grossWeight = models.FloatField(null=True)  # 总毛重
    status = models.BooleanField(default=False)  # False:未封箱; True：已封箱入库
    printTimes = models.PositiveIntegerField(default=0)  # 箱体二维码打印次数
    scanTimes = models.PositiveIntegerField(default=0)  # 箱体二维码扫描次数
    txtQR = models.CharField(max_length=255,null=True)  # 箱体二维码文本内容
    objects = gsBoxManager()

    class Meta:
        ordering = ['boxNumber']

# 箱体实物表
class gsSubBox(models.Model):
    subBoxNumber = models.PositiveIntegerField()  # 箱号
    grossWeight = models.FloatField(null=True)  # 子箱总毛重
    isValid = models.BooleanField(default=True)  # True有效，False无效
    printTimes = models.PositiveIntegerField(default=0)  # 箱体二维码打印次数
    scanTimes = models.PositiveIntegerField(default=0)  # 箱体二维码扫描次数
    box = models.ForeignKey(gsBox)  # 箱体, 参照gsBox表"id"列
    status = models.BooleanField(default=False)  # False:未封箱; True：已封箱入库
    txtQR = models.CharField(max_length=255,null=True)  # 箱体二维码文本内容
    class Meta:
        ordering = ['box','subBoxNumber']


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
        subBoxNumber = kwargs['subBoxNumber']
        workSeq = kwargs['workSeq']
        try:
            box = gsBox.objects.get(boxNumber=boxNumber)
            if subBoxNumber:
                subBox = gsSubBox.objects.get(box=box,subBoxNumber=subBoxNumber)
                work = super(models.Manager, self).get(box=box, workSeq=workSeq,subBox=subBox)
            else:
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
    createDateTime = models.DateTimeField(auto_now_add=True)  # 作业创建时间, 即实物建档时间
    completeDateTime = models.DateTimeField(null=True)  # 作业完成时间, 即最后一个实物信息采集审核完成时间
    manager = models.CharField(max_length=512)  # 实物分发岗位
    status = models.PositiveIntegerField(default=0)  # 状态代码: 0:未启用 1:已启用 2:已完成
    subBox = models.ForeignKey(gsSubBox,null=True)  # 箱体, gsSubBox"id"列
    objects = gsWorkManager()

    class Meta:
        ordering = ['workSeq', 'createDateTime']


# 实物索引表
class gsThing(models.Model):
    serialNumber = models.CharField(max_length=255,unique=True)  # 货发二代系统提供的随机生成的实物编号
    serialNumber2 = models.CharField(max_length=255,unique=True,null=True)  # 编号由四部分组成：品名代码-明细品名代码-发行库代码-实物序号
    subClassName = models.CharField(max_length=255,null=False)  # 明细品名
    subBoxSeq = models.PositiveIntegerField(default=1)  # 子箱号, 从1开始
    isAllocate = models.BooleanField(default=False)  # 实物是否已分配
    historyNo = models.IntegerField(null=True)
    box = models.ForeignKey(gsBox)  # 箱体, 参照gsBox表"id"列
    subBox = models.ForeignKey(gsSubBox,null=True)
    work = models.ForeignKey(gsWork,null=True)

class gsCase(models.Model):
    caseNumber = models.CharField(max_length=255,unique=True,null=False)  # 货发二代系统提供的盒号
    status = models.BooleanField(default=False)  # 是否封盒: False:未完成 True:完成
    box = models.ForeignKey(gsBox)  # 箱体, 参照gsBox表"id"列
    subBox = models.ForeignKey(gsSubBox,null=True)
    work = models.ForeignKey(gsWork)

# 状态表
class gsStatus(models.Model):
    status = models.BooleanField(default=False)  # 实物状态: False:未完成 True:完成
    close_stautus = models.BooleanField(default=False)  # 实物是否封袋: False:未完成 True:完成
    incase_status = models.BooleanField(default=False)  # 实物装入盒子: False:未完成 True:完成

    numberingStatus = models.BooleanField(default=False)  # 环节1外观信息采集状态: False:未完成 True:完成
    numberingOperator = models.CharField(max_length=512, blank=True)  # 环节1外观信息采集记录员
    numberingCreateDateTime = models.DateTimeField(auto_now_add=True)  # 环节1外观信息采集记录生成时间
    numberingUpdateDateTime = models.DateTimeField(null=True)  # 环节1外观信息采集记录最近一次修改时间

    analyzingStatus = models.BooleanField(default=False)  # 环节2频谱检测状态: False:未完成 True:完成
    analyzingOperator = models.CharField(max_length=512, blank=True)  # 环节2频谱检测记录员
    analyzingCreateDateTime = models.DateTimeField(auto_now_add=True)  # 环节2频谱检测记录生成时间
    analyzingUpdateDateTime = models.DateTimeField(null=True)  # 环节2频谱检测记录最近一次修改时间

    measuringStatus = models.BooleanField(default=False)  # 环节3测量称重状态: False:未完成 True:完成
    measuringOperator = models.CharField(max_length=512, blank=True)  # 环节3测量称重记录员
    measuringCreateDateTime = models.DateTimeField(auto_now_add=True)  # 环节3测量称重记录生成时间
    measuringUpdateDateTime = models.DateTimeField(null=True)  # 环节3测量称重记录最近一次修改时间

    checkingStatus = models.BooleanField(default=False)  # 环节4数据审核状态: False:未完成 True:完成
    checkingOperator = models.CharField(max_length=512, blank=True)  # 环节4数据审核记录员
    checkingCreateDateTime = models.DateTimeField(auto_now_add=True)  # 环节4数据审核记录生成时间
    checkingUpdateDateTime = models.DateTimeField(null=True)  # 环节4数据审核记录最近一次修改时间

    photographingStatus = models.BooleanField(default=False)  # 环节4数据审核状态: False:未完成 True:完成
    photographingOperator = models.CharField(max_length=512, blank=True)  # 环节4数据审核记录员
    photographingCreateDateTime = models.DateTimeField(auto_now_add=True)  # 环节4数据审核记录生成时间
    photographingUpdateDateTime = models.DateTimeField(null=True)  # 环节4数据审核记录最近一次修改时间

    thing = models.ForeignKey(gsThing)
    case = models.ForeignKey(gsCase,null=True)

#
# # 作业与实物关系表
# class gsWorkThing(models.Model):
#     thing = models.ForeignKey(gsThing)  # 实物, 参照gsThing表"id"列
#     work = models.ForeignKey(gsWork)  # 作业, 参照gsWork表"id"列
#     status = models.ForeignKey(gsStatus)  # 实物对应的清点查验状态, 参照gsStatus表"id"列
#
#     class Meta:
#         unique_together = (('thing', 'work'))


# 实物属性表
# 金银锭类    
class gsDing(models.Model):
    thing = models.ForeignKey(gsThing)
    detailedName = models.CharField(max_length=1024, blank=True)  # 名称
    typeName = models.CharField(max_length=512, blank=True)  # 型制类型
    peroid = models.CharField(max_length=255, blank=True)  # 时代
    producerPlace = models.CharField(max_length=512, blank=True)  # 制作地/制作人
    carveName = models.CharField(max_length=512, blank=True)  # 铭文
    remark = models.TextField(default='')  # 备注
    quality = models.CharField(max_length=255, blank=True)  # 品相
    level = models.CharField(max_length=255, blank=True)  # 评价等级
    originalQuantity = models.FloatField(null=True)  # 原标注成色

    detectedQuantity = models.FloatField(null=True)  # 频谱检测成色

    length = models.FloatField(null=True)  # 长度
    width = models.FloatField(null=True)  # 宽度
    height = models.FloatField(null=True)  # 高度
    grossWeight = models.FloatField(null=True)  # 毛重

    pureWeight = models.FloatField(null=True)  # 净重

    # # -----------------------------------------------------------
    # measureTime = models.TimeField(null=True)  # 测量时间
    # measureDate = models.DateField(null=True)  # 测量日期
    # Au = models.CharField(max_length=255, null=True)  # 金
    # Ag = models.CharField(max_length=255, null=True)  # 银
    # Cu = models.CharField(max_length=255, null=True)  # 铜
    # Pt = models.CharField(max_length=255, null=True)  # 铂
    # Pd = models.CharField(max_length=255, null=True)  # 钯
    # Zn = models.CharField(max_length=255, null=True)  # 锌
    # Ni = models.CharField(max_length=255, null=True)  # 镍
    # Cd = models.CharField(max_length=255, null=True)  # 镉
    # Co = models.CharField(max_length=255, null=True)  # 钴
    # Ru = models.CharField(max_length=255, null=True)  # 钌
    # Ir = models.CharField(max_length=255, null=True)  # 铱
    # Rh = models.CharField(max_length=255, null=True)  # 铑
    # In = models.CharField(max_length=255, null=True)  # 铟
    # Pb = models.CharField(max_length=255, null=True)  # 铅
    # Fe = models.CharField(max_length=255, null=True)  # 铁
    # Os = models.CharField(max_length=255, null=True)  # 锇
    # W = models.CharField(max_length=255, null=True)  # 钨
    # Others = models.CharField(max_length=255, null=True)  # 其他
    # testUnit = models.CharField(max_length=255, null=True)  # 送检单位
    # testPerson = models.CharField(max_length=255, null=True)  # 检测人员
    # # 序号
    # # 生产厂家
    # # 样品编号
    # sampleName = models.CharField(max_length=255, null=True)  # 样品名称
    # # 重量
    # reportQuality = models.CharField(max_length=255, null=True)  # 申报成色
    # testResult = models.CharField(max_length=255, null=True)  # 检测结果
    # remarks = models.CharField(max_length=255, null=True)  # 备注
    # # 检测依据
    # # 检测单位地址
    # # 联系电话
    # # 检测单位
    # testRequire = models.CharField(max_length=255, null=True)  # 测试要求
    # # -----------------------------------------------------------


# 金银币章类
class gsBiZhang(models.Model):
    thing = models.ForeignKey(gsThing)

    detailedName = models.CharField(max_length=1024, blank=True)  # 名称
    versionName = models.CharField(max_length=1024, blank=True)  # 版别
    peroid = models.CharField(max_length=255, blank=True)  # 时代
    producerPlace = models.CharField(max_length=512, blank=True)  # 制作地/制作人
    value = models.CharField(max_length=512, blank=True)  # 币值
    remark = models.TextField(default='')  # 备注
    quality = models.CharField(max_length=255, blank=True)  # 品相
    level = models.CharField(max_length=255, blank=True)  # 评价等级
    originalQuantity = models.FloatField(null=True)  # 原标注成色

    detectedQuantity = models.FloatField(null=True)  # 检测成色

    diameter = models.FloatField(null=True)  # 直径
    thick = models.FloatField(null=True)  # 厚度
    grossWeight = models.FloatField(null=True)  # 毛重
    pureWeight = models.FloatField(null=True)  # 净重


# 银元类
class gsYinYuan(models.Model):
    thing = models.ForeignKey(gsThing)

    detailedName = models.CharField(max_length=1024, blank=True)  # 名称
    versionName = models.CharField(max_length=1024, blank=True)  # 版别
    peroid = models.CharField(max_length=255, blank=True)  # 时代
    producerPlace = models.CharField(max_length=512, blank=True)  # 制作地/制作人
    value = models.CharField(max_length=512, blank=True)  # 币值
    marginShape = models.CharField(max_length=512, blank=True)  # 边齿
    remark = models.TextField(default='')  # 备注
    quality = models.CharField(max_length=255, blank=True)  # 品相
    level = models.CharField(max_length=255, blank=True)  # 评价等级
    originalQuantity = models.FloatField(null=True)  # 原标注成色

    detectedQuantity = models.FloatField(null=True)  # 检测成色

    diameter = models.FloatField(null=True)  # 直径
    thick = models.FloatField(null=True)  # 厚度
    grossWeight = models.FloatField(null=True)  # 毛重
    pureWeight = models.FloatField(null=True)  # 净重


# 金银工艺品类    
class gsGongYiPin(models.Model):
    thing = models.ForeignKey(gsThing)

    detailedName = models.CharField(max_length=1024, blank=True)  # 名称
    peroid = models.CharField(max_length=255, blank=True)  # 时代
    remark = models.TextField(default='')  # 备注
    quality = models.CharField(max_length=255, blank=True)  # 品相
    level = models.CharField(max_length=255, blank=True)  # 评价等级
    originalQuantity = models.FloatField(null=True)  # 原标注成色

    detectedQuantity = models.FloatField(null=True)  # 检测成色

    length = models.FloatField(null=True)  # 长度
    width = models.FloatField(null=True)  # 宽度
    height = models.FloatField(null=True)  # 高度
    grossWeight = models.FloatField(null=True)  # 毛重
    pureWeight = models.FloatField(null=True)  # 净重

# 属性表
class gsProperty(models.Model):
    project = models.CharField(max_length=255)  # 项目
    type = models.CharField(max_length=255)  # 类型
    code = models.CharField(max_length=255, blank=True)  # 代码

    parentProject = models.CharField(max_length=255, blank=True)  # 父项目
    parentType = models.CharField(max_length=255, blank=True)  # 父类型

    grandpaProject = models.CharField(max_length=255, blank=True)  # 祖项目
    grandpaType = models.CharField(max_length=255, blank=True)  # 祖类型


class gsLog(models.Model):
    userID = models.PositiveIntegerField()  # 用户ID
    userName = models.CharField(max_length=255)  # 用户姓名
    organization = models.CharField(max_length=255,null=True)  # 组织
    department = models.CharField(max_length=255,null=True)  # 部门
    operationType = models.CharField(max_length=255)  # 操作类型
    content = models.CharField(max_length=256)  # 内容
    when = models.DateTimeField(auto_now_add=True)  # 操作日期
