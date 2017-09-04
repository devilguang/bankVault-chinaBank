# encoding=UTF-8
import os
import django


def batchInsert():
    init_authority()
    init_property()


def init_property():
    add_property(project='实物类型', type='金银锭类', code='1')
    add_property(project='品名', type='杂金', code='1', parentProject='实物类型', parentType='金银锭类')
    add_property(project='品名', type='杂银', code='2', parentProject='实物类型', parentType='金银锭类')
    add_property(project='明细品名', type='稀一锭', code='02', parentProject='品名', parentType='杂金', grandpaProject='实物类型',
                 grandpaType='金银锭类')
    add_property(project='明细品名', type='稀三锭', code='08', parentProject='品名', parentType='杂金', grandpaProject='实物类型',
                 grandpaType='金银锭类')
    add_property(project='明细品名', type='稀一锭', code='02', parentProject='品名', parentType='杂银', grandpaProject='实物类型',
                 grandpaType='金银锭类')
    add_property(project='明细品名', type='稀二锭', code='06', parentProject='品名', parentType='杂银', grandpaProject='实物类型',
                 grandpaType='金银锭类')
    add_property(project='明细品名', type='稀三锭', code='10', parentProject='品名', parentType='杂银', grandpaProject='实物类型',
                 grandpaType='金银锭类')

    add_property(project='实物类型', type='金银币章类', code='2')
    add_property(project='品名', type='杂金', code='1', parentProject='实物类型', parentType='金银币章类')
    add_property(project='品名', type='杂银', code='2', parentProject='实物类型', parentType='金银币章类')
    add_property(project='明细品名', type='稀一币', code='01', parentProject='品名', parentType='杂金', grandpaProject='实物类型',
                 grandpaType='金银币章类')
    add_property(project='明细品名', type='稀二币', code='04', parentProject='品名', parentType='杂金', grandpaProject='实物类型',
                 grandpaType='金银币章类')
    add_property(project='明细品名', type='稀三币', code='06', parentProject='品名', parentType='杂金', grandpaProject='实物类型',
                 grandpaType='金银币章类')
    add_property(project='明细品名', type='金样币', code='10', parentProject='品名', parentType='杂金', grandpaProject='实物类型',
                 grandpaType='金银币章类')
    add_property(project='明细品名', type='稀一元', code='01', parentProject='品名', parentType='杂银', grandpaProject='实物类型',
                 grandpaType='金银币章类')
    add_property(project='明细品名', type='稀二外元', code='03', parentProject='品名', parentType='杂银', grandpaProject='实物类型',
                 grandpaType='金银币章类')
    add_property(project='明细品名', type='稀二减元', code='04', parentProject='品名', parentType='杂银', grandpaProject='实物类型',
                 grandpaType='金银币章类')
    add_property(project='明细品名', type='稀二钱', code='05', parentProject='品名', parentType='杂银', grandpaProject='实物类型',
                 grandpaType='金银币章类')
    add_property(project='明细品名', type='稀三色元', code='09', parentProject='品名', parentType='杂银', grandpaProject='实物类型',
                 grandpaType='金银币章类')
    add_property(project='明细品名', type='稀三辅币', code='08', parentProject='品名', parentType='杂银', grandpaProject='实物类型',
                 grandpaType='金银币章类')
    add_property(project='明细品名', type='银样币', code='14', parentProject='品名', parentType='杂银', grandpaProject='实物类型',
                 grandpaType='金银币章类')

    add_property(project='实物类型', type='银元类', code='3')
    add_property(project='品名', type='国内稀一级银元', code='3', parentProject='实物类型', parentType='银元类')
    add_property(project='品名', type='国内稀二级银元', code='4', parentProject='实物类型', parentType='银元类')
    add_property(project='品名', type='国内稀三级银元', code='5', parentProject='实物类型', parentType='银元类')
    add_property(project='品名', type='国外稀二级银元', code='6', parentProject='实物类型', parentType='银元类')
    add_property(project='品名', type='普制银元', code='7', parentProject='实物类型', parentType='银元类')
    add_property(project='品名', type='待熔银元8', code='8', parentProject='实物类型', parentType='银元类')
    add_property(project='明细品名', type='待熔银元', code='01', parentProject='品名', parentType='待熔银元8', grandpaProject='实物类型',
                 grandpaType='银元类')
    add_property(project='明细品名', type='袁像民国三年壹圆', code='01', parentProject='品名', parentType='普制银元',
                 grandpaProject='实物类型', grandpaType='银元类')
    add_property(project='明细品名', type='西班牙币', code='01', parentProject='品名', parentType='国外稀二级银元',
                 grandpaProject='实物类型', grandpaType='银元类')
    add_property(project='明细品名', type='造币总厂光绪元宝库平七钱二分', code='01', parentProject='品名', parentType='国内稀三级银元',
                 grandpaProject='实物类型', grandpaType='银元类')
    add_property(project='明细品名', type='丁未大清银币壹圆', code='01', parentProject='品名', parentType='国内稀二级银元',
                 grandpaProject='实物类型', grandpaType='银元类')
    add_property(project='明细品名', type='福建官局造光绪元宝', code='01', parentProject='品名', parentType='国内稀一级银元',
                 grandpaProject='实物类型', grandpaType='银元类')

    add_property(project='实物类型', type='金银工艺品类', code='4')
    add_property(project='品名', type='杂金', code='1', parentProject='实物类型', parentType='金银工艺品类')
    add_property(project='品名', type='杂银', code='2', parentProject='实物类型', parentType='金银工艺品类')
    add_property(project='明细品名', type='稀一工', code='03', parentProject='品名', parentType='杂金', grandpaProject='实物类型',
                 grandpaType='金银工艺品类')
    add_property(project='明细品名', type='稀二工', code='05', parentProject='品名', parentType='杂金', grandpaProject='实物类型',
                 grandpaType='金银工艺品类')
    add_property(project='明细品名', type='稀二工', code='07', parentProject='品名', parentType='杂银', grandpaProject='实物类型',
                 grandpaType='金银工艺品类')
    add_property(project='明细品名', type='稀三工', code='12', parentProject='品名', parentType='杂银', grandpaProject='实物类型',
                 grandpaType='金银工艺品类')
    add_property(project='明细品名', type='普制工', code='13', parentProject='品名', parentType='杂银', grandpaProject='实物类型',
                 grandpaType='金银工艺品类')

    add_property(project='发行库', type='湖北重点库', code='217')
    add_property(project='发行库', type='北京重点库', code='201')
    add_property(project='发行库', type='天津重点库', code='202')
    add_property(project='发行库', type='河北重点库', code='203')


def add_property(project, type, code=None, parentProject='', parentType='', grandpaProject='', grandpaType=''):
    c, created = gsProperty.objects.get_or_create(project=project, type=type, code=code, parentProject=parentProject,
                                                  parentType=parentType, grandpaProject=grandpaProject,
                                                  grandpaType=grandpaType)
    return c


def init_authority():
    # 添加系统默认管理员
    admin, flag = gsUser.objects.createUser(nickName='sysadmin', password='hbjy@396', type=0)
    # 添加超级管理员
    user, flag = gsUser.objects.createUser(nickName='李汉忠', password='123456', type=0)
    # 添加管理员
    user, flag = gsUser.objects.createUser(nickName='凌伟', password='123456', type=1)
    # 添加管理员
    user, flag = gsUser.objects.createUser(nickName='岳华', password='123456', type=1)
    # 添加管理员
    user = gsUser.objects.createUser(nickName='许青', password='123456', type=1)


# Start execution here!
if __name__ == '__main__':
    print "Starting Batch Insert Data script..."
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gsinfosite.settings')
    django.setup()
    from gsinfo.models import gsProperty, gsBox, gsWork, gsThing, gsDing, gsBiZhang, \
        gsYinYuan, gsGongYiPin, gsStatus, gsUser
    from django.contrib.auth.models import Group

    batchInsert()
