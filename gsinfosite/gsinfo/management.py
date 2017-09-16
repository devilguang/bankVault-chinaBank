# encoding=UTF-8
from django.db.models.signals import post_migrate
from property import *


def batchInsert(sender, **kwargs):
    # print sender.name
    if sender.name == 'gsinfo':
        init_property()
        init_authority()


def init_property():
    for dic in metaDate:
        project = dic['project']
        val = dic['val']
        for type_code in val:
            code, type = type_code
            add_property(project=project, type=type, code=code)

    for dic1 in level2:
        parentProject = dic1['parentProject']
        parentType = dic1['parentType']
        parentCode = dic1['parentCode']
        val = dic1.get('val', '')
        for dic2 in val:
            project = dic2['project']
            type = dic2['type']
            code = dic2['code']
            add_property(project=project,
                         type=type,
                         code=code,
                         parentProject=parentProject,
                         parentType=parentType,
                         parentCode=parentCode,)
    for dic1 in level3:
        grandpaProject = dic1['grandpaProject']
        grandpaType = dic1['grandpaType']
        grandpaCode = dic1['grandpaCode']
        val1 = dic1['val']
        for dic2 in val1:
            parentProject = dic2['parentProject']
            parentType = dic2['parentType']
            parentCode = dic2['parentCode']
            val2 = dic2.get('val', '')
            for dic3 in val2:
                project = dic3['project']
                type = dic3['type']
                code = dic3['code']
                add_property(project=project,
                             type=type,
                             code=code,
                             parentProject=parentProject,
                             parentType=parentType,
                             parentCode=parentCode,
                             grandpaProject=grandpaProject,
                             grandpaType=grandpaType,
                             grandpaCode=grandpaCode,)



def add_property(project, type, code=None, parentProject='', parentType='', parentCode='', grandpaProject='',
                 grandpaType='', grandpaCode=''):
    from gsinfo.models import gsProperty
    c, created = gsProperty.objects.get_or_create(project=project,
                                                  type=type,
                                                  code=code,
                                                  parentProject=parentProject,
                                                  parentType=parentType,
                                                  parentCode=parentCode,
                                                  grandpaProject=grandpaProject,
                                                  grandpaType=grandpaType,
                                                  grandpaCode=grandpaCode, )
    return c


def init_authority():
    from gsinfo.models import gsUser
    # 添加系统默认管理员
    gsUser.objects.createUser(nickName='sysadmin', password='123456', type=0, organization='system_default',
                              department='system_default')  # 'hbjy@396'


post_migrate.connect(batchInsert)
