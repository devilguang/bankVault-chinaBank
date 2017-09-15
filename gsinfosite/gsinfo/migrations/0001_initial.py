# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-13 10:46
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='gsBiZhang',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detailedName', models.CharField(blank=True, max_length=1024)),
                ('versionName', models.CharField(blank=True, max_length=1024)),
                ('peroid', models.CharField(blank=True, max_length=255)),
                ('producer', models.CharField(blank=True, max_length=512)),
                ('producePlace', models.CharField(blank=True, max_length=512)),
                ('value', models.CharField(blank=True, max_length=512)),
                ('remark', models.TextField(default=b'')),
                ('quality', models.CharField(blank=True, max_length=255)),
                ('level', models.CharField(blank=True, max_length=255)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('boxNumber', models.PositiveIntegerField(unique=True)),
                ('boxSeq', models.CharField(max_length=255, unique=True)),
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
            name='gsCase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caseNumber', models.CharField(max_length=255, unique=True)),
                ('status', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='gsDing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detailedName', models.CharField(blank=True, max_length=1024)),
                ('typeName', models.CharField(blank=True, max_length=512)),
                ('peroid', models.CharField(blank=True, max_length=255)),
                ('producer', models.CharField(blank=True, max_length=512)),
                ('producePlace', models.CharField(blank=True, max_length=512)),
                ('carveName', models.CharField(blank=True, max_length=512)),
                ('remark', models.TextField(default=b'')),
                ('quality', models.CharField(blank=True, max_length=255)),
                ('level', models.CharField(blank=True, max_length=255)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detailedName', models.CharField(blank=True, max_length=1024)),
                ('peroid', models.CharField(blank=True, max_length=255)),
                ('remark', models.TextField(default=b'')),
                ('quality', models.CharField(blank=True, max_length=255)),
                ('level', models.CharField(blank=True, max_length=255)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userID', models.PositiveIntegerField()),
                ('userName', models.CharField(max_length=255)),
                ('organization', models.CharField(max_length=255, null=True)),
                ('department', models.CharField(max_length=255, null=True)),
                ('operationType', models.CharField(max_length=255)),
                ('content', models.CharField(max_length=256)),
                ('when', models.DateTimeField(default=datetime.datetime(2017, 9, 13, 18, 46, 0, 271000))),
            ],
        ),
        migrations.CreateModel(
            name='gsProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255)),
                ('code', models.CharField(blank=True, max_length=255)),
                ('parentProject', models.CharField(blank=True, max_length=255)),
                ('parentType', models.CharField(blank=True, max_length=255)),
                ('grandpaProject', models.CharField(blank=True, max_length=255)),
                ('grandpaType', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='gsStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=False)),
                ('close_status', models.BooleanField(default=False)),
                ('incase_status', models.BooleanField(default=False)),
                ('numberingStatus', models.BooleanField(default=False)),
                ('numberingOperator', models.CharField(blank=True, max_length=512)),
                ('numberingCreateDateTime', models.DateTimeField(default=datetime.datetime(2017, 9, 13, 18, 46, 0, 258000))),
                ('numberingUpdateDateTime', models.DateTimeField(null=True)),
                ('analyzingStatus', models.BooleanField(default=False)),
                ('analyzingOperator', models.CharField(blank=True, max_length=512)),
                ('analyzingCreateDateTime', models.DateTimeField(default=datetime.datetime(2017, 9, 13, 18, 46, 0, 258000))),
                ('analyzingUpdateDateTime', models.DateTimeField(null=True)),
                ('measuringStatus', models.BooleanField(default=False)),
                ('measuringOperator', models.CharField(blank=True, max_length=512)),
                ('measuringCreateDateTime', models.DateTimeField(default=datetime.datetime(2017, 9, 13, 18, 46, 0, 258000))),
                ('measuringUpdateDateTime', models.DateTimeField(null=True)),
                ('checkingStatus', models.BooleanField(default=False)),
                ('checkingOperator', models.CharField(blank=True, max_length=512)),
                ('checkingCreateDateTime', models.DateTimeField(default=datetime.datetime(2017, 9, 13, 18, 46, 0, 258000))),
                ('checkingUpdateDateTime', models.DateTimeField(null=True)),
                ('photographingStatus', models.BooleanField(default=False)),
                ('photographingOperator', models.CharField(blank=True, max_length=512)),
                ('photographingCreateDateTime', models.DateTimeField(default=datetime.datetime(2017, 9, 13, 18, 46, 0, 258000))),
                ('photographingUpdateDateTime', models.DateTimeField(null=True)),
                ('completeTime', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='gsSubBox',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subBoxNumber', models.PositiveIntegerField()),
                ('grossWeight', models.FloatField(null=True)),
                ('isValid', models.BooleanField(default=True)),
                ('printTimes', models.PositiveIntegerField(default=0)),
                ('scanTimes', models.PositiveIntegerField(default=0)),
                ('status', models.BooleanField(default=False)),
                ('txtQR', models.CharField(max_length=255, null=True)),
                ('box', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gsinfo.gsBox')),
            ],
            options={
                'ordering': ['box', 'subBoxNumber'],
            },
        ),
        migrations.CreateModel(
            name='gsThing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serialNumber', models.CharField(max_length=255, unique=True)),
                ('serialNumber2', models.CharField(max_length=255, null=True, unique=True)),
                ('subClassName', models.CharField(max_length=255)),
                ('subBoxSeq', models.PositiveIntegerField(default=1)),
                ('isAllocate', models.BooleanField(default=False)),
                ('historyNo', models.IntegerField(null=True)),
                ('box', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gsinfo.gsBox')),
                ('case', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='gsinfo.gsCase')),
                ('subBox', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='gsinfo.gsSubBox')),
            ],
        ),
        migrations.CreateModel(
            name='gsUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.PositiveIntegerField()),
                ('nickName', models.CharField(max_length=255, unique=True)),
                ('organization', models.CharField(max_length=255, null=True)),
                ('department', models.CharField(max_length=255, null=True)),
                ('auth', models.BooleanField(default=False)),
                ('manage', models.BooleanField(default=False)),
                ('numbering', models.BooleanField(default=False)),
                ('analyzing', models.BooleanField(default=False)),
                ('measuring', models.BooleanField(default=False)),
                ('checking', models.BooleanField(default=False)),
                ('photographing', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='gsWork',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workSeq', models.PositiveIntegerField()),
                ('workName', models.CharField(max_length=512)),
                ('createDateTime', models.DateTimeField(default=datetime.datetime(2017, 9, 13, 18, 46, 0, 253000))),
                ('completeDateTime', models.DateTimeField(null=True)),
                ('manager', models.CharField(max_length=512)),
                ('status', models.PositiveIntegerField(default=0)),
                ('box', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gsinfo.gsBox')),
                ('subBox', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='gsinfo.gsSubBox')),
            ],
            options={
                'ordering': ['workSeq', 'createDateTime'],
            },
        ),
        migrations.CreateModel(
            name='gsYinYuan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detailedName', models.CharField(blank=True, max_length=1024)),
                ('versionName', models.CharField(blank=True, max_length=1024)),
                ('peroid', models.CharField(blank=True, max_length=255)),
                ('producer', models.CharField(blank=True, max_length=512)),
                ('producePlace', models.CharField(blank=True, max_length=512)),
                ('value', models.CharField(blank=True, max_length=512)),
                ('marginShape', models.CharField(blank=True, max_length=512)),
                ('remark', models.TextField(default=b'')),
                ('quality', models.CharField(blank=True, max_length=255)),
                ('level', models.CharField(blank=True, max_length=255)),
                ('originalQuantity', models.FloatField(null=True)),
                ('detectedQuantity', models.FloatField(null=True)),
                ('diameter', models.FloatField(null=True)),
                ('thick', models.FloatField(null=True)),
                ('grossWeight', models.FloatField(null=True)),
                ('pureWeight', models.FloatField(null=True)),
                ('thing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gsinfo.gsThing')),
            ],
        ),
        migrations.AddField(
            model_name='gsthing',
            name='work',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='gsinfo.gsWork'),
        ),
        migrations.AddField(
            model_name='gsstatus',
            name='thing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gsinfo.gsThing'),
        ),
        migrations.AddField(
            model_name='gsgongyipin',
            name='thing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gsinfo.gsThing'),
        ),
        migrations.AddField(
            model_name='gsding',
            name='thing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gsinfo.gsThing'),
        ),
        migrations.AddField(
            model_name='gsbizhang',
            name='thing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gsinfo.gsThing'),
        ),
    ]
