# encoding=UTF-8
from django.db.models.signals import post_migrate
from property import *

def batchInsert(sender, **kwargs):
    #print sender.name
    if sender.name == 'gsinfo':
        init_property()
        init_authority()

def init_property():
    for dic in metaDate:
        project = dic['project']
        val = dic['val']
        for type_code in val:
            code,type = type_code
            add_property(project=project, type=type, code=code)

    for dic1 in detail:
        grandpaProject = dic1['grandpaProject']
        grandpaType = dic1['grandpaType']
        grandpaCode = dic1['grandpaCode']
        val1 = dic1['val']
        for dic2 in val1:
            parentProject = dic2['parentProject']
            parentType = dic2['parentType']
            parentCode = dic2['parentCode']
            val2 = dic2.get('val','')
            if val2:
                for dic3 in val2:
                    project = dic3['parentProject']
                    type = dic3['parentType']
                    code = dic3['parentCode']
                    add_property(project=project,
                                 type=type,
                                 code=code,
                                 parentProject=parentProject,
                                 parentType=parentType,
                                 parentCode=parentCode,
                                 grandpaProject=grandpaProject,
                                 grandpaType=grandpaType,
                                 grandpaCode=grandpaCode,
                                 )

            else:
                add_property(project=parentProject,
                             type=parentType,
                             code=parentCode,
                             parentProject=grandpaProject,
                             parentType=grandpaType,
                             parentCode=grandpaCode,)

def add_property(project, type, code=None, parentProject='', parentType='', grandpaProject='', grandpaType=''):
    from gsinfo.models import gsProperty
    c, created = gsProperty.objects.get_or_create(project=project, type=type, code=code, parentProject=parentProject,
                                                  parentType=parentType, grandpaProject=grandpaProject,
                                                  grandpaType=grandpaType)
    return c


def init_authority():
    from gsinfo.models import gsUser
    # 添加系统默认管理员
    gsUser.objects.createUser(nickName='sysadmin', password='123456', type=0,organization='system_default',department='system_default')  # 'hbjy@396'

post_migrate.connect(batchInsert)