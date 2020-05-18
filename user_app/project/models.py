from django.db import models

from user_app.user.models import UserInfo

# Create your models here.


class PriceStrategy(models.Model):
    classify = models.CharField(verbose_name='分类', max_length=10)
    title = models.CharField(verbose_name='标题', max_length=20)
    price = models.CharField(default=0, verbose_name='价格/年', max_length=10)
    pro_count = models.CharField(verbose_name='创建项目个数', max_length=10)
    pro_member = models.CharField(verbose_name='项目成员', max_length=10)
    pro_space = models.CharField(verbose_name='项目空间', max_length=50)
    one_file = models.CharField(verbose_name='单文件', max_length=50)
    create_time = models.DateField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '价格策略'


class UserPriceOrder(models.Model):
    user = models.ForeignKey(UserInfo, verbose_name='用户')
    stutic = models.IntegerField(choices=((1, '已支付'), (2, '未支付')), verbose_name='状态')
    unit_price = models.CharField(max_length=10, verbose_name='单价')
    actual_price = models.CharField(max_length=10, verbose_name='实际支付')
    create_time = models.DateField(auto_now_add=True, verbose_name='开始时间')
    over_time = models.DateField(verbose_name='结束时间')
    year_num = models.IntegerField(verbose_name='数量(年)')
    order_id = models.CharField(verbose_name='订单号', max_length=20)

    class Meta:
        verbose_name = '交易记录'


class Project(models.Model):
    project_name = models.CharField(verbose_name='项目名称', max_length=20)
    desc = models.CharField(verbose_name='描述', max_length=300)
    color = models.CharField(verbose_name='颜色', max_length=10)
    asterisk = models.BooleanField(verbose_name='是否星标', default=False)
    part_num = models.CharField(verbose_name='参与人数', max_length=10)
    creator = models.ForeignKey(UserInfo, verbose_name='创建者')
    used_space = models.CharField(verbose_name='已使用空间', max_length=50)

    class Meta:
        verbose_name = '项目'


class ProjectParticipant(models.Model):
    project = models.ForeignKey(Project, verbose_name='项目')
    user = models.ForeignKey(UserInfo, verbose_name='用户')
    asterisk = models.BooleanField(verbose_name='是否星标', default=False)

    class Meta:
        verbose_name = '项目参与者'