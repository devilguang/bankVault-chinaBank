# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='gsBox',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('boxNumber', models.CharField(unique=True, max_length=255, verbose_name=b'\xe8\xb4\xa7\xe5\x8f\x91\xe4\xba\x8c\xe4\xbb\xa3\xe7\xb3\xbb\xe7\xbb\x9f\xe6\x8f\x90\xe4\xbe\x9b\xe7\x9a\x84\xe7\xae\xb1\xe5\x8f\xb7')),
                ('wareHouse', models.CharField(max_length=255, verbose_name=b'\xe5\x8f\x91\xe8\xa1\x8c\xe5\xba\x93')),
                ('amount', models.PositiveIntegerField(verbose_name=b'\xe4\xbb\xb6\xe6\x95\xb0')),
                ('grossWeight', models.FloatField(null=True, verbose_name=b'\xe6\x80\xbb\xe6\xaf\x9b\xe9\x87\x8d')),
                ('status', models.BooleanField(default=False, verbose_name=b'\xe5\xb0\x81\xe7\xae\xb1\xe7\x8a\xb6\xe6\x80\x81\xef\xbc\x88False:\xe6\x9c\xaa\xe5\xb0\x81\xe7\xae\xb1; True\xef\xbc\x9a\xe5\xb7\xb2\xe5\xb0\x81\xe7\xae\xb1\xe5\x85\xa5\xe5\xba\x93\xef\xbc\x89')),
                ('oprateType', models.BooleanField(default=False, verbose_name=b'\xe6\x93\x8d\xe4\xbd\x9c\xe7\xb1\xbb\xe5\x9e\x8b')),
            ],
            options={
                'ordering': ['boxNumber'],
            },
        ),
        migrations.CreateModel(
            name='gsCase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('caseNumber', models.CharField(unique=True, max_length=255)),
                ('closePerson', models.CharField(unique=True, max_length=255, verbose_name=b'\xe5\xb0\x81\xe8\xa3\x85\xe4\xba\xba')),
                ('closeCheckPerson', models.CharField(unique=True, max_length=255, verbose_name=b'\xe5\xb0\x81\xe8\xa3\x85\xe5\xa4\x8d\xe6\xa0\xb8\xe4\xba\xba')),
                ('closeTime', models.DateTimeField(default=datetime.datetime(2017, 9, 18, 9, 6, 39, 429000), verbose_name=b'\xe5\xb0\x81\xe8\xa3\x85\xe6\x97\xb6\xe9\x97\xb4')),
                ('status', models.BooleanField(default=False, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe5\xb0\x81\xe7\x9b\x92(False:\xe6\x9c\xaa\xe5\xb0\x81\xe7\x9b\x92 True:\xe5\xb7\xb2\xe5\xb0\x81\xe7\x9b\x92)')),
                ('box', models.ForeignKey(to='gsinfo.gsBox')),
            ],
        ),
        migrations.CreateModel(
            name='gsLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('userName', models.CharField(max_length=255)),
                ('organization', models.CharField(max_length=255, null=True)),
                ('department', models.CharField(max_length=255, null=True)),
                ('operationType', models.CharField(max_length=255)),
                ('content', models.CharField(max_length=256)),
                ('when', models.DateTimeField(default=datetime.datetime(2017, 9, 18, 9, 6, 39, 434000))),
            ],
        ),
        migrations.CreateModel(
            name='gsProperty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=255, blank=True)),
                ('parentProject', models.CharField(max_length=255, blank=True)),
                ('parentType', models.CharField(max_length=255, blank=True)),
                ('parentCode', models.CharField(max_length=255, blank=True)),
                ('grandpaProject', models.CharField(max_length=255, blank=True)),
                ('grandpaType', models.CharField(max_length=255, blank=True)),
                ('grandpaCode', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='gsStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.BooleanField(default=False)),
                ('close_status', models.BooleanField(default=False)),
                ('incase_status', models.BooleanField(default=False)),
                ('numberingStatus', models.BooleanField(default=False)),
                ('numberingOperator', models.CharField(max_length=512, blank=True)),
                ('numberingCreateDateTime', models.DateTimeField(default=datetime.datetime(2017, 9, 18, 9, 6, 39, 432000))),
                ('numberingUpdateDateTime', models.DateTimeField(null=True)),
                ('analyzingStatus', models.BooleanField(default=False)),
                ('analyzingOperator', models.CharField(max_length=512, blank=True)),
                ('analyzingCreateDateTime', models.DateTimeField(default=datetime.datetime(2017, 9, 18, 9, 6, 39, 432000))),
                ('analyzingUpdateDateTime', models.DateTimeField(null=True)),
                ('measuringStatus', models.BooleanField(default=False)),
                ('measuringOperator', models.CharField(max_length=512, blank=True)),
                ('measuringCreateDateTime', models.DateTimeField(default=datetime.datetime(2017, 9, 18, 9, 6, 39, 432000))),
                ('measuringUpdateDateTime', models.DateTimeField(null=True)),
                ('checkingStatus', models.BooleanField(default=False)),
                ('checkingOperator', models.CharField(max_length=512, blank=True)),
                ('checkingCreateDateTime', models.DateTimeField(default=datetime.datetime(2017, 9, 18, 9, 6, 39, 432000))),
                ('checkingUpdateDateTime', models.DateTimeField(null=True)),
                ('photographingStatus', models.BooleanField(default=False)),
                ('photographingOperator', models.CharField(max_length=512, blank=True)),
                ('photographingCreateDateTime', models.DateTimeField(default=datetime.datetime(2017, 9, 18, 9, 6, 39, 432000))),
                ('photographingUpdateDateTime', models.DateTimeField(null=True)),
                ('completeTime', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='gsThing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serialNumber', models.CharField(unique=True, max_length=255, verbose_name=b'\xe5\xae\x9e\xe7\x89\xa9\xe5\xba\x8f\xe5\x8f\xb7')),
                ('serialNumber2', models.CharField(max_length=255, unique=True, null=True, verbose_name=b'\xe5\xae\x9e\xe7\x89\xa9\xe7\xbc\x96\xe5\x8f\xb7')),
                ('isAllocate', models.BooleanField(default=False, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe8\xa2\xab\xe5\x88\x9b\xe5\xbb\xba\xe4\xb8\xba\xe4\xbd\x9c\xe4\xb8\x9a')),
                ('level', models.CharField(max_length=255, verbose_name=b'\xe8\xaf\x84\xe4\xbb\xb7\xe7\xad\x89\xe7\xba\xa7', blank=True)),
                ('detailedName', models.CharField(max_length=1024, verbose_name=b'\xe5\x90\x8d\xe7\xa7\xb0', blank=True)),
                ('peroid', models.CharField(max_length=255, verbose_name=b'\xe5\xb9\xb4\xe4\xbb\xa3', blank=True)),
                ('year', models.CharField(max_length=255, verbose_name=b'\xe5\xb9\xb4\xe4\xbb\xbd', blank=True)),
                ('country', models.CharField(max_length=512, verbose_name=b'\xe5\x9b\xbd\xe5\x88\xab', blank=True)),
                ('faceAmount', models.CharField(max_length=512, verbose_name=b'\xe9\x9d\xa2\xe5\x80\xbc', blank=True)),
                ('dingSecification', models.CharField(max_length=512, verbose_name=b'\xe8\xa7\x84\xe6\xa0\xbc', blank=True)),
                ('zhangType', models.CharField(max_length=512, verbose_name=b'\xe6\x80\xa7\xe8\xb4\xa8', blank=True)),
                ('shape', models.CharField(max_length=512, verbose_name=b'\xe5\xb7\xa5\xe8\x89\xba\xe5\x93\x81\xe7\xb1\xbb\xe5\x99\xa8\xe5\x9e\x8b\xef\xbc\x88\xe5\x9e\x8b\xe5\x88\xb6\xef\xbc\x89', blank=True)),
                ('appearance', models.CharField(max_length=255, verbose_name=b'\xe5\x93\x81\xe7\x9b\xb8\xef\xbc\x88\xe5\xae\x8c\xe6\xae\x8b\xe7\xa8\x8b\xe5\xba\xa6\xef\xbc\x89', blank=True)),
                ('mark', models.CharField(max_length=512, verbose_name=b'\xe9\x93\xad\xe6\x96\x87\xef\xbc\x88\xe6\x96\x87\xe5\xad\x97\xe4\xbf\xa1\xe6\x81\xaf\xef\xbc\x89', blank=True)),
                ('grossWeight', models.FloatField(null=True, verbose_name=b'\xe6\xaf\x9b\xe9\x87\x8d')),
                ('pureWeight', models.FloatField(null=True, verbose_name=b'\xe7\xba\xaf\xe9\x87\x8d')),
                ('originalQuantity', models.FloatField(null=True, verbose_name=b'\xe5\x8e\x9f\xe6\xa0\x87\xe6\xb3\xa8\xe6\x88\x90\xe8\x89\xb2')),
                ('detectedQuantity', models.FloatField(null=True, verbose_name=b'\xe9\xa2\x91\xe8\xb0\xb1\xe6\xa3\x80\xe6\xb5\x8b\xe6\x88\x90\xe8\x89\xb2')),
                ('amount', models.PositiveIntegerField(null=True, verbose_name=b'\xe4\xbb\xb6\xef\xbc\x88\xe6\x9e\x9a\xef\xbc\x89\xe6\x95\xb0')),
                ('length', models.FloatField(null=True, verbose_name=b'\xe9\x95\xbf\xe5\xba\xa6')),
                ('width', models.FloatField(null=True, verbose_name=b'\xe5\xae\xbd\xe5\xba\xa6')),
                ('height', models.FloatField(null=True, verbose_name=b'\xe9\xab\x98\xe5\xba\xa6')),
                ('remark', models.TextField(default=b'', verbose_name=b'\xe5\xa4\x87\xe6\xb3\xa8')),
                ('box', models.ForeignKey(to='gsinfo.gsBox')),
                ('case', models.ForeignKey(to='gsinfo.gsCase', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='gsUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.PositiveIntegerField(verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7\xe7\xb1\xbb\xe5\x9e\x8b\xef\xbc\x880:\xe8\xb6\x85\xe7\xba\xa7\xe7\xae\xa1\xe7\x90\x86\xe5\x91\x98 1:\xe7\xae\xa1\xe7\x90\x86\xe5\x91\x98 2:\xe4\xb8\x80\xe8\x88\xac\xe7\x94\xa8\xe6\x88\xb7\xef\xbc\x89')),
                ('userName', models.CharField(max_length=255, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7\xe5\x90\x8d')),
                ('organization', models.CharField(max_length=255, null=True, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7\xe6\x89\x80\xe5\x9c\xa8\xe7\xbb\x84\xe7\xbb\x87')),
                ('department', models.CharField(max_length=255, null=True, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7\xe6\x89\x80\xe5\x9c\xa8\xe9\x83\xa8\xe9\x97\xa8')),
                ('auth', models.BooleanField(default=False, verbose_name=b'\xe6\x8e\x88\xe6\x9d\x83\xe7\xae\xa1\xe7\x90\x86\xe5\xb2\x97\xe4\xbd\x8d\xe6\x9d\x83\xe9\x99\x90\xef\xbc\x88True:\xe6\x8b\xa5\xe6\x9c\x89 False:\xe6\x9c\xaa\xe6\x8b\xa5\xe6\x9c\x89\xef\xbc\x89')),
                ('manage', models.BooleanField(default=False, verbose_name=b'\xe5\xae\x9e\xe7\x89\xa9\xe5\x88\x86\xe5\x8f\x91\xe5\xb2\x97\xe4\xbd\x8d\xe6\x9d\x83\xe9\x99\x90\xef\xbc\x88True:\xe6\x8b\xa5\xe6\x9c\x89 False:\xe6\x9c\xaa\xe6\x8b\xa5\xe6\x9c\x89\xef\xbc\x89')),
                ('numbering', models.BooleanField(default=False, verbose_name=b'\xe5\xa4\x96\xe8\xa7\x82\xe4\xbf\xa1\xe6\x81\xaf\xe9\x87\x87\xe9\x9b\x86\xe6\x9d\x83\xe9\x99\x90\xef\xbc\x88True:\xe6\x8b\xa5\xe6\x9c\x89 False:\xe6\x9c\xaa\xe6\x8b\xa5\xe6\x9c\x89\xef\xbc\x89')),
                ('analyzing', models.BooleanField(default=False, verbose_name=b'\xe9\xa2\x91\xe8\xb0\xb1\xe5\x88\x86\xe6\x9e\x90\xe5\xb2\x97\xe4\xbd\x8d\xe6\x9d\x83\xe9\x99\x90\xef\xbc\x88True:\xe6\x8b\xa5\xe6\x9c\x89 False:\xe6\x9c\xaa\xe6\x8b\xa5\xe6\x9c\x89\xef\xbc\x89')),
                ('measuring', models.BooleanField(default=False, verbose_name=b'\xe6\xb5\x8b\xe9\x87\x8f\xe7\xa7\xb0\xe9\x87\x8d\xe5\xb2\x97\xe4\xbd\x8d\xe6\x9d\x83\xe9\x99\x90\xef\xbc\x88True:\xe6\x8b\xa5\xe6\x9c\x89 False:\xe6\x9c\xaa\xe6\x8b\xa5\xe6\x9c\x89\xef\xbc\x89')),
                ('checking', models.BooleanField(default=False, verbose_name=b'\xe5\xae\x9e\xe7\x89\xa9\xe8\xae\xa4\xe5\xae\x9a\xe5\xb2\x97\xe4\xbd\x8d\xe6\x9d\x83\xe9\x99\x90\xef\xbc\x88True:\xe6\x8b\xa5\xe6\x9c\x89 False:\xe6\x9c\xaa\xe6\x8b\xa5\xe6\x9c\x89\xef\xbc\x89')),
                ('photographing', models.BooleanField(default=False, verbose_name=b'\xe5\x9b\xbe\xe5\x83\x8f\xe9\x87\x87\xe9\x9b\x86\xe5\xb2\x97\xe4\xbd\x8d\xe6\x9d\x83\xe9\x99\x90\xef\xbc\x88True:\xe6\x8b\xa5\xe6\x9c\x89 False:\xe6\x9c\xaa\xe6\x8b\xa5\xe6\x9c\x89\xef\xbc\x89')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='gsWork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('workSeq', models.PositiveIntegerField()),
                ('workName', models.CharField(max_length=512)),
                ('createDateTime', models.DateTimeField(default=datetime.datetime(2017, 9, 18, 9, 6, 39, 427000))),
                ('completeDateTime', models.DateTimeField(null=True)),
                ('status', models.PositiveIntegerField(default=0)),
                ('box', models.ForeignKey(to='gsinfo.gsBox')),
                ('user', models.ForeignKey(to='gsinfo.gsUser')),
            ],
            options={
                'ordering': ['workSeq', 'createDateTime'],
            },
        ),
        migrations.AddField(
            model_name='gsthing',
            name='work',
            field=models.ForeignKey(to='gsinfo.gsWork', null=True),
        ),
        migrations.AddField(
            model_name='gsstatus',
            name='thing',
            field=models.ForeignKey(to='gsinfo.gsThing'),
        ),
        migrations.AddField(
            model_name='gslog',
            name='user',
            field=models.ForeignKey(to='gsinfo.gsUser'),
        ),
        migrations.AddField(
            model_name='gsbox',
            name='property',
            field=models.ForeignKey(to='gsinfo.gsProperty'),
        ),
    ]
