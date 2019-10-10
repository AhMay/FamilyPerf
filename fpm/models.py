# fpm/model.py
__author__ ='may'
import datetime
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Common(models.Model):
    create_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    mod_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    class Meta:
        abstract = True

class Family(Common):
    #家庭
    name = models.CharField('家庭名', max_length=10, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '家庭表'
        verbose_name_plural = verbose_name

class UserProfile(models.Model):
    '''家庭用户信息表'''
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    family = models.ForeignKey(Family,on_delete=models.CASCADE)

    def __str__(self):
        return '{}的用户{}'.format(self.family.name,self.user.username)

    class Meta:
        verbose_name = '家庭用户表'
        verbose_name_plural = verbose_name

class MemberInfo(Common):
    '''成员表'''
    sex_choices =(
        (0,'男'),
        (1,'女'),
    )
    name = models.CharField('姓名',max_length=64)
    sex = models.SmallIntegerField('性别', choices=sex_choices, default=1)
    age = models.DecimalField('年龄',max_digits=3,decimal_places=0,default=0)
    #score 记录当前的总分
    #一个成员一定属于某个家庭
    family = models.ForeignKey(Family,on_delete=models.CASCADE)

    def __str__(self):
        return '{}的{}'.format(self.family.name,self.name)

    class Meta:
        verbose_name = '成员表'
        verbose_name_plural = verbose_name
        unique_together =['name','family']

class PerfItem(Common):
    '''成员项目表'''
    name = models.CharField('项目名', max_length=256)
    score_up = models.PositiveSmallIntegerField('加分', default=0)
    score_down = models.SmallIntegerField('减分', default=0)
    active = models.BooleanField('状态', default=True)
    member = models.ForeignKey(MemberInfo, verbose_name='成员', on_delete=models.CASCADE)

    class Meta:
        verbose_name = '成员项目表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{}的绩效项目{}'.format(self.member.name,self.name)

class PerfRecord(Common):
    '''绩效记录'''
    day = models.DateField(verbose_name='日期')
    #属于哪个成员
    member = models.ForeignKey(MemberInfo,on_delete=models.CASCADE,verbose_name='成员')
    item = models.ForeignKey(PerfItem, on_delete=models.CASCADE, verbose_name='绩效项')
    score = models.SmallIntegerField(verbose_name='计分')
    description = models.CharField(verbose_name='描述', max_length=256, default='', blank=True)

    class Meta:
        verbose_name = '绩效记录表'
        verbose_name_plural = verbose_name

class Result(Common):
    '''成绩表'''
    day = models.DateField(verbose_name='日期')
    member = models.ForeignKey(MemberInfo,on_delete=models.CASCADE,verbose_name='成员')
    score = models.SmallIntegerField(verbose_name='总分')
    score_sum = models.SmallIntegerField(verbose_name='累计分数')
    description = models.CharField(verbose_name='总评', max_length=256,default='', blank=True)

    def __str__(self):
        return '{}-{}-{}'.format(self.member.name,self.day,self.score)

    class Meta:
        verbose_name = '成绩表'
        verbose_name_plural = verbose_name


