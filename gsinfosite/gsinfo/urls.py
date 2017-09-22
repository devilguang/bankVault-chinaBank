"""gsinfo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views
from . import checking
from . import manage
from . import systemAdmin
from . import measuring
from . import numbering
from . import photographing
from . import analyzing

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^login/getTools/$', views.getTools, name='getTools'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^login/getAllUser/$', views.getAllUser, name='getAllUser'),
    url(r'^login/updatePassword/$', systemAdmin.updatePassword, name='updatePassword'),

    url(r'^systemAdmin/$', systemAdmin.systemAdmin, name='systemAdmin'),
    url(r'^systemAdmin/getProperty/$', systemAdmin.getProperty, name='getProperty'),
    url(r'^systemAdmin/getProductType/$', views.getProductType, name='getProductType'),
    url(r'^systemAdmin/getClassName/(?P<code>\d+)$', views.getClassName, name='getClassName'),
    url(r'^systemAdmin/propertyProcess/$', systemAdmin.propertyProcess, name='propertyProcess'),
    url(r'^systemAdmin/getArchive/$', systemAdmin.getArchive, name='getArchive'),
    url(r'^systemAdmin/getWorkContent/$', systemAdmin.getWorkContent, name='getWorkContent'),
    url(r'^systemAdmin/getWorkData/(?P<workSeq>\d+)$', views.getWorkData, name='getWorkData'),
    url(r'^systemAdmin/userProcess/$', systemAdmin.userProcess, name='userProcess'),
    url(r'^systemAdmin/getUser/$', systemAdmin.getUser, name='getUser'),
    url(r'^systemAdmin/getAuthority/$', systemAdmin.getAuthority, name='getAuthority'),
    url(r'^systemAdmin/authorityProcess/$', systemAdmin.authorityProcess, name='authorityProcess'),
    url(r'^systemAdmin/getWork/(?P<boxNumber>\d+)$', systemAdmin.workProcess, name='workProcess'),
    url(r'^systemAdmin/getTag/(?P<boxNumber>\d+)$', systemAdmin.tagProcess, name='tagProcess'),
    url(r'^systemAdmin/getThing/(?P<boxNumber>\d+)/(?P<serialNumber>\d+-\d+-\d+-\d+)$', systemAdmin.thingProcess,
        name='thingProcess'),
    url(r'^systemAdmin/exploreThing/(?P<boxNumber>\d+)/(?P<serialNumber>\d+-\d+-\d+-\d+)$', views.exploreThing,
        name='exploreThing'),
    url(r'^systemAdmin/updatePassword/$', systemAdmin.updatePassword, name='updatePassword'),
    url(r'^systemAdmin/backToWork/$', systemAdmin.backToWork, name='backToWork'),
    url(r'^systemAdmin/getLogContent/$', systemAdmin.getLogContent, name='getLogContent'),
    url(r'^systemAdmin/getOperationType/$', systemAdmin.getOperationType, name='getOperationType'),
    url(r'^systemAdmin/getUserName/$', systemAdmin.getUserName, name='getUserName'),
    url(r'^systemAdmin/setSysAdmin/$', systemAdmin.setSysAdmin, name='setSysAdmin'),

    url(r'^manage/$', manage.manage, name='manage'),
    url(r'^manage/getProductType/$', views.getProductType, name='getProductType'),
    url(r'^manage/getWareHouse/$', views.getWareHouse, name='getWareHouse'),
    url(r'^manage/getClassName/(?P<code>\d+)$', views.getClassName, name='getClassName'),
    url(r'^manage/getSubClassName/(?P<code>\d+&\d+)$', views.getSubClassName, name='getSubClassName'),
    url(r'^manage/getOprateType/$', views.getOprateType, name='getOprateType'),
    url(r'^manage/getBox/$', manage.getBox, name='getBox'),
    url(r'^manage/getThing/$', manage.getThing, name='getThing'),
    url(r'^manage/generateWorkName/$', manage.generateWorkName, name='generateWorkName'),
    url(r'^manage/generateContentForWork/$', manage.generateContentForWork, name='generateContentForWork'),
    url(r'^manage/createBox/$', manage.createBox, name='createBox'),
    url(r'^manage/addToExistingBox/$', manage.addToExistingBox, name='addToExistingBox'),
    url(r'^manage/deleteBox/$', manage.deleteBox, name='deleteBox'),
    url(r'^manage/createWork/$', manage.createWork, name='createWork'),
    url(r'^manage/deleteWork/$', manage.deleteWork, name='deleteWork'),
    url(r'^manage/getWork/$', manage.getWork, name='getWork'),
    url(r'^manage/startOrStopWork/$', manage.startOrStopWork, name='startOrStopWork'),
    url(r'^manage/getStatusData/$', manage.getStatusData, name='getStatusData'),
    url(r'^manage/generateTag/$', manage.generateTag, name='generateTag'),
    url(r'^manage/generateAbstract/$', manage.generateAbstract, name='generateAbstract'),
    url(r'^manage/generateArchives/$', manage.generateArchives, name='generateArchives'),
    url(r'^manage/generateBoxInfo/$', manage.generateBoxInfo, name='generateBoxInfo'),
    url(r'^manage/exploreThing/(?P<boxNumber>.*?)/(?P<serialNumber>.*?)$', views.exploreThing,name='exploreThing'),
    url(r'^manage/exploreBox/$', manage.exploreBox, name='exploreBox'),
    url(r'^manage/searchThingInfo/$', views.searchThingInfo, name='searchThingInfo'),
    url(r'^manage/boxInOutStore/$', manage.boxInOutStore, name='boxInOutStore'),
    #url(r'^manage/search/$', views.adv_search.as_view(), name='calibration_search'),
    url(r'^manage/advanceSearchHTML/$', manage.advanceSearchHTML, name='advanceSearchHTML'),
    url(r'^manage/advanceSearch/$', manage.advanceSearch, name='advanceSearch'),
    #url(r'^manage/search/$', views.search, name='search'),
    url(r'^manage/search/$', views.GeneralSearch(), name='GeneralSearch'),
    #url(r'^manage/search/$', SearchView(), name='haystack_search'),
    url(r'^manage/restore/$', manage.restore, name='restore'),
    url(r'^manage/getStatisticalReport/$', manage.getStatisticalReport, name='getStatisticalReport'),
    url(r'^manage/getCarveNameReport/$', manage.getCarveNameReport, name='getCarveNameReport'),
    url(r'^manage/getEfficiencyReport/$', manage.getEfficiencyReport, name='getEfficiencyReport'),
    url(r'^manage/print_service/$', manage.print_service, name='print_service'),
    url(r'^manage/print_auth/$', manage.print_auth, name='print_auth'),
    url(r'^manage/getCloseThing/$', manage.getCloseThing, name='getCloseThing'),
    url(r'^manage/closeThing/$', manage.closeThing, name='closeThing'),
    url(r'^manage/getCloseOverThing/$', manage.getCloseOverThing, name='getCloseOverThing'),
    url(r'^manage/getCaseNumber/$', manage.getCaseNumber, name='getCaseNumber'),
    url(r'^manage/confirmInputCase/$', manage.confirmInputCase, name='confirmInputCase'),
    url(r'^manage/print_pic/$', manage.print_pic, name='print_pic'),
    url(r'^manage/enterEvent/$', manage.enterEvent, name='enterEvent'),
    url(r'^manage/cancleInput/$', manage.cancleInput, name='cancleInput'),
    url(r'^manage/openOrigBox/$', manage.openOrigBox, name='openOrigBox'),
    url(r'^manage/checkAmount/$', manage.checkAmount, name='checkAmount'),

    url(r'^checking/$', checking.checking, name='checking'),
    url(r'^checking/getProductType/$', views.getProductType, name='getProductType'),
    url(r'^checking/getClassName/(?P<code>\d+)$', views.getClassName, name='getClassName'),
    url(r'^checking/getSubClassName/(?P<code>\d+&\d+)$', views.getSubClassName, name='getSubClassName'),
    url(r'^checking/getWareHouse/$', views.getWareHouse, name='getWareHouse'),
    url(r'^checking/getWorkSpaceContent/$', views.getWorkSpaceContent, name='getWorkSpaceContent'),
    url(r'^checking/getWorkStatus/$', checking.getWorkStatus, name='getWorkStatus'),
    url(r'^checking/exploreThing/(?P<boxNumber>\d+)/(?P<serialNumber>.*?)$', views.exploreThing,name='exploreThing'),
    url(r'^checking/getDurationCompleteThingAmount/$', checking.getDurationCompleteThingAmount,name='getDurationCompleteThingAmount'),
    url(r'^checking/updateCheckingInfo/$', checking.updateCheckingInfo, name='updateCheckingInfo'),
    url(r'^checking/getThingData/$', checking.getThingData, name='getThingData'),
    url(r'^checking/updateThingData/$', checking.updateThingData, name="updateThingData"),
    url(r'^checking/getWorkData/(?P<workSeq>\d+)$', views.getWorkData, name='getWorkData'),
    url(r'^checking/searchThingInfo/$', views.searchThingInfo, name='searchThingInfo'),
    url(r'^checking/getThingInfo/$', views.getThingInfo, name='getThingInfo'),
    url(r'^checking/getReadyInfo/$', views.getReadyInfo, name='getReadyInfo'),
    url(r'^numbering/checkInfo/$', views.checkInfo, name='checkInfo'),

    url(r'^numbering/$', numbering.numbering, name='numbering'),
    url(r'^numbering/getWorkSpaceContent/$', views.getWorkSpaceContent, name='getWorkSpaceContent'),
    url(r'^numbering/getWorkData/(?P<workSeq>\d+)$', views.getWorkData, name='getWorkData'),
    url(r'^numbering/getProductType/$', views.getProductType, name='getProductType'),
    url(r'^numbering/getClassName/(?P<code>\d+)$', views.getClassName, name='getClassName'),
    url(r'^numbering/getSubClassName/(?P<code>\d+&\d+)$', views.getSubClassName, name='getSubClassName'),
    url(r'^numbering/getWareHouse/$', views.getWareHouse, name='getWareHouse'),
    url(r'^numbering/updateNumberingInfo/$', numbering.updateNumberingInfo, name='updateNumberingInfo'),
    url(r'^numbering/getNumberingInfo/$', numbering.getNumberingInfo, name='getNumberingInfo'),
    url(r'^numbering/searchThingInfo/$', views.searchThingInfo, name='searchThingInfo'),
    url(r'^numbering/checkInfo/$', views.checkInfo, name='checkInfo'),
    url(r'^numbering/getThingInfo/$', views.getThingInfo, name='getThingInfo'),
    url(r'^numbering/getReadyInfo/$', views.getReadyInfo, name='getReadyInfo'),

    url(r'^measuring/$', measuring.measuring, name='measuring'),
    url(r'^measuring/getWorkSpaceContent/$', views.getWorkSpaceContent, name='getWorkSpaceContent'),
    url(r'^measuring/getWorkData/(?P<workSeq>\d+)$', views.getWorkData, name='getWorkData'),
    url(r'^measuring/getProductType/$', views.getProductType, name='getProductType'),
    url(r'^measuring/getClassName/(?P<code>\d+)$', views.getClassName, name='getClassName'),
    url(r'^measuring/getSubClassName/(?P<code>\d+&\d+)$', views.getSubClassName, name='getSubClassName'),
    url(r'^measuring/getWareHouse/$', views.getWareHouse, name='getWareHouse'),
    url(r'^measuring/updateMeasuringInfo/$', measuring.updateMeasuringInfo, name='updateMeasuringInfo'),
    url(r'^measuring/getMeasuringInfo/$', measuring.getMeasuringInfo, name='getMeasuringInfo'),
    url(r'^measuring/searchThingInfo/$', views.searchThingInfo, name='searchThingInfo'),

    url(r'^photographing/$', photographing.photographing, name='photographing'),
    url(r'^photographing/getWorkSpaceContent/$', views.getWorkSpaceContent, name='getWorkSpaceContent'),
    url(r'^photographing/getWorkData/(?P<workSeq>\d+)$', views.getWorkData, name='getWorkData'),
    url(r'^photographing/searchThingInfo/$', views.searchThingInfo, name='searchThingInfo'),
    url(r'^photographing/getPictures/$', photographing.getPictures, name='getPictures'),
    url(r'^photographing/getWareHouse/$', views.getWareHouse, name='getWareHouse'),
    url(r'^photographing/getProductType/$', views.getProductType, name='getProductType'),
    url(r'^photographing/updatePhotographingInfo/$', photographing.updatePhotographingInfo, name='updatePhotographingInfo'),
    url(r'^photographing/delectPic/$', photographing.delectPic, name='delectPic'),

    url(r'^analyzing/$', analyzing.analyzing, name='analyzing'),
    url(r'^analyzing/getWorkSpaceContent/$', views.getWorkSpaceContent, name='getWorkSpaceContent'),
    url(r'^analyzing/getWorkData/(?P<workSeq>\d+)$', views.getWorkData, name='getWorkData'),
    url(r'^analyzing/searchThingInfo/$', views.searchThingInfo, name='searchThingInfo'),
    url(r'^analyzing/getAnalyzingWorkData/$', analyzing.getAnalyzingWorkData, name='getAnalyzingWorkData'),
    url(r'^analyzing/updateAnalyzingInfo/$', analyzing.updateAnalyzingInfo, name='updateAnalyzingInfo'),


]
