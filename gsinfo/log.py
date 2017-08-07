# encoding=utf-8

from .models import gsLog
from .models import gsUser


def log(user, operationType,content):
    userID = user.id
    userProfile = gsUser.objects.get(user=user)
    userName = userProfile.nickName

    gsLog.objects.create(userID=userID,
                         userName=userName,
                         operationType=operationType,
                         content=content)

# 获取日志信息——只有systemAdmin可以获取日志信息
def retriveLog(**args):
    userName = args.get('userName', None)
    operationType = args.get('operationType', None)
    startDateTime = args.get('startDateTime', None)
    endDateTime = args.get('endDateTime', None)

    logs = gsLog.objects.all().order_by('-when')
    if userName:
        logs = logs.filter(userName=userName)

    if operationType:
        logs = logs.filter(operationType=operationType)

    if startDateTime and endDateTime:
        pass

    ret = list(logs.values('userID', 'userName', 'operationType', 'content', 'when'))

    return ret

# 只有systemAdmin可以获取日志中的operationType
def getOperationType():
    ops = gsLog.objects.all().values_list('operationType').distinct()

    ret = []
    r = {}
    r['id'] = 0
    r['text'] = '全部'
    ret.append(r)

    idx = 1
    for op in ops:
        r = {}
        r['id'] = idx
        r['text'] = op
        ret.append(r)

        idx = idx + 1

    return ret

# 只有systemAdmin可以获取日志中的userName
def getUserName():
    users = gsLog.objects.all().values_list('userName').distinct()

    ret = []
    r = {}
    r['id'] = 0
    r['text'] = '全部'
    ret.append(r)

    idx = 1
    for u in users:
        r = {}
        r['id'] = idx
        r['text'] = u
        ret.append(r)

        idx = idx + 1

    return ret
