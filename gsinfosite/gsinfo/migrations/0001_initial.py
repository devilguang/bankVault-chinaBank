# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='gsBiZhang',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('detailedName', models.CharField(max_length=1024, blank=True)),
                ('versionName', models.CharField(max_length=1024, blank=True)),
                ('peroid', models.CharField(max_length=255, blank=True)),
                ('producerPlace', models.CharField(max_length=512, blank=True)),
                ('value', models.CharField(max_length=512, blank=True)),
                ('remark', models.TextField(default=b'')),
                ('quality', models.CharField(max_length=255, blank=True)),
                ('level', models.CharField(max_length=255, blank=True)),
                ('originalQuantity', models.FloatField(null=True)),
                ('detectedQuantity', models.FloatField(null=True)),
                ('diameter', models.FloatField(null=True)),
                ('thick', models.FloatField(null=True)),
                ('grossWeight', models.FloatField(null=True)),
                ('pureWeight', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='gsBox',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('boxNumber', models.PositiveIntegerField(unique=True)),
                ('boxSeq', models.CharField(unique=True, max_length=255)),
                ('productType', models.CharField(max_length=255)),
                ('className', models.CharField(max_length=255)),
                ('subClassName', models.CharField(max_length=255)),
                ('wareHouse', models.CharField(max_length=255)),
                ('amount', models.PositiveIntegerField()),
                ('grossWeight', models.FloatField(null=True)),
                ('status', models.BooleanField(default=False)),
                ('printTimes', models.PositiveIntegerField(default=0)),
                ('scanTimes', models.PositiveIntegerField(default=0)),
                ('txtQR', models.CharField(max_length=255, null=True)),
            ],
            options={
                'ordering': ['boxNumber'],
            },
        ),
        migrations.CreateModel(
            name='gsDing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('detailedName', models.CharField(max_length=1024, blank=True)),
                ('typeName', models.CharField(max_length=512, blank=True)),
                ('peroid', models.CharField(max_length=255, blank=True)),
                ('producerPlace', models.CharField(max_length=512, blank=True)),
                ('carveName', models.CharField(max_length=512, blank=True)),
                ('remark', models.TextField(default=b'')),
                ('quality', models.CharField(max_length=255, blank=True)),
                ('level', models.CharField(max_length=255, blank=True)),
                ('originalQuantity', models.FloatField(null=True)),
                ('detectedQuantity', models.FloatField(null=True)),
                ('length', models.FloatField(null=True)),
                ('width', models.FloatField(null=True)),
                ('height', models.FloatField(null=True)),
                ('grossWeight', models.FloatField(null=True)),
                ('pureWeight', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='gsGongYiPin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('detailedName', models.CharField(max_length=1024, blank=True)),
                ('peroid', models.CharField(max_length=255, blank=True)),
                ('remark', models.TextField(default=b'')),
                ('quality', models.CharField(max_length=255, blank=True)),
                ('level', models.CharField(max_length=255, blank=True)),
                ('originalQuantity', models.FloatField(null=True)),
                ('detectedQuantity', models.FloatField(null=True)),
                ('length', models.FloatField(null=True)),
                ('width', models.FloatField(null=True)),
                ('height', models.FloatField(null=True)),
                ('grossWeight', models.FloatField(null=True)),
                ('pureWeight', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='gsLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('userID', models.PositiveIntegerField()),
                ('userName', models.CharField(max_length=255)),
                ('organization', models.CharField(max_length=255, null=True)),
                ('department', models.CharField(max_length=255, null=True)),
                ('operationType', models.CharField(max_length=255)),
                ('content', models.CharField(max_length=256)),
                ('when', models.DateTimeField(auto_now_add=True)),
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
                ('grandpaProject', models.CharField(max_length=255, blank=True)),
                ('grandpaType', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='gsStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.BooleanField(default=False)),
                ('numberingStatus', models.BooleanField(default=False)),
                ('numberingOperator', models.CharField(max_length=512, blank=True)),
                ('numberingCreateDateTime', models.DateTimeField(auto_now_add=True)),
                ('numberingUpdateDateTime', models.DateTimeField(null=True)),
                ('analyzingStatus', models.BooleanField(default=False)),
                ('analyzingOperator', models.CharField(max_length=512, blank=True)),
                ('analyzingCreateDateTime', models.DateTimeField(auto_now_add=True)),
                ('analyzingUpdateDateTime', models.DateTimeField(null=True)),
                ('measuringStatus', models.BooleanField(default=False)),
                ('measuringOperator', models.CharField(max_length=512, blank=True)),
                ('measuringCreateDateTime', models.DateTimeField(auto_now_add=True)),
                ('measuringUpdateDateTime', models.DateTimeField(null=True)),
                ('checkingStatus', models.BooleanField(default=False)),
                ('checkingOperator', models.CharField(max_length=512, blank=True)),
                ('checkingCreateDateTime', models.DateTimeField(auto_now_add=True)),
                ('checkingUpdateDateTime', models.DateTimeField(null=True)),
                ('photographingStatus', models.BooleanField(default=False)),
                ('photographingOperator', models.CharField(max_length=512, blank=True)),
                ('photographingCreateDateTime', models.DateTimeField(auto_now_add=True)),
                ('photographingUpdateDateTime', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='gsSubBox',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subBoxNumber', models.PositiveIntegerField()),
                ('grossWeight', models.FloatField(null=True)),
                ('isValid', models.BooleanField(default=True)),
                ('printTimes', models.PositiveIntegerField(default=0)),
                ('scanTimes', models.PositiveIntegerField(default=0)),
                ('status', models.BooleanField(default=False)),
                ('txtQR', models.CharField(max_length=255, null=True)),
                ('box', models.ForeignKey(to='gsinfo.gsBox')),
            ],
            options={
                'ordering': ['box', 'subBoxNumber'],
            },
        ),
        migrations.CreateModel(
            name='gsThing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serialNumber', models.CharField(unique=True, max_length=255)),
                ('serialNumber2', models.CharField(max_length=255, unique=True, null=True)),
                ('subClassName', models.CharField(max_length=255)),
                ('subBoxSeq', models.PositiveIntegerField(default=1)),
                ('isAllocate', models.BooleanField(default=False)),
                ('historyNo', models.IntegerField(null=True)),
                ('box', models.ForeignKey(to='gsinfo.gsBox')),
                ('subBox', models.ForeignKey(to='gsinfo.gsSubBox', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='gsUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.PositiveIntegerField()),
                ('nickName', models.CharField(unique=True, max_length=255)),
                ('organization', models.CharField(max_length=255, null=True)),
                ('department', models.CharField(max_length=255, null=True)),
                ('auth', models.BooleanField(default=False)),
                ('manage', models.BooleanField(default=False)),
                ('numbering', models.BooleanField(default=False)),
                ('analyzing', models.BooleanField(default=False)),
                ('measuring', models.BooleanField(default=False)),
                ('checking', models.BooleanField(default=False)),
                ('photographing', models.BooleanField(default=False)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='gsWork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('workSeq', models.PositiveIntegerField()),
                ('workName', models.CharField(max_length=512)),
                ('createDateTime', models.DateTimeField(auto_now_add=True)),
                ('completeDateTime', models.DateTimeField(null=True)),
                ('manager', models.CharField(max_length=512)),
                ('status', models.PositiveIntegerField(default=0)),
                ('box', models.ForeignKey(to='gsinfo.gsBox')),
                ('subBox', models.ForeignKey(to='gsinfo.gsSubBox', null=True)),
            ],
            options={
                'ordering': ['workSeq', 'createDateTime'],
            },
        ),
        migrations.CreateModel(
            name='gsYinYuan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('detailedName', models.CharField(max_length=1024, blank=True)),
                ('versionName', models.CharField(max_length=1024, blank=True)),
                ('peroid', models.CharField(max_length=255, blank=True)),
                ('producerPlace', models.CharField(max_length=512, blank=True)),
                ('value', models.CharField(max_length=512, blank=True)),
                ('marginShape', models.CharField(max_length=512, blank=True)),
                ('remark', models.TextField(default=b'')),
                ('quality', models.CharField(max_length=255, blank=True)),
                ('level', models.CharField(max_length=255, blank=True)),
                ('originalQuantity', models.FloatField(null=True)),
                ('detectedQuantity', models.FloatField(null=True)),
                ('diameter', models.FloatField(null=True)),
                ('thick', models.FloatField(null=True)),
                ('grossWeight', models.FloatField(null=True)),
                ('pureWeight', models.FloatField(null=True)),
                ('thing', models.ForeignKey(to='gsinfo.gsThing')),
            ],
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
            model_name='gsgongyipin',
            name='thing',
            field=models.ForeignKey(to='gsinfo.gsThing'),
        ),
        migrations.AddField(
            model_name='gsding',
            name='thing',
            field=models.ForeignKey(to='gsinfo.gsThing'),
        ),
        migrations.AddField(
            model_name='gsbizhang',
            name='thing',
            field=models.ForeignKey(to='gsinfo.gsThing'),
        ),
    ]
