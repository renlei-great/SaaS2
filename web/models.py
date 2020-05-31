from django.db import models
from mdeditor.fields import MDTextField

# Create your models here.

# 用户模型类 -------


class UserInfo(models.Model):
    username = models.CharField(verbose_name='用户名', max_length=32)
    email = models.EmailField(verbose_name='邮箱', max_length=32)
    mobile_phpne = models.CharField(verbose_name='电话', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=100)


# 项目模型类 -------


class PricePolicy(models.Model):
    category_chioces=(
        (1, '免费版'),
        (2, '收费版'),
        (3, '其他'),
    )
    category = models.SmallIntegerField(verbose_name='收费类型', choices=category_chioces, default=2)
    title = models.CharField(verbose_name='标题', max_length=32)
    price = models.PositiveIntegerField(verbose_name='价格/年')

    pro_num = models.PositiveIntegerField(verbose_name='创建项目个数')
    pro_member = models.PositiveIntegerField(verbose_name='项目成员')
    pro_space = models.PositiveIntegerField(verbose_name='项目空间')
    per_file_size = models.PositiveIntegerField(verbose_name='单文件大小')
    create_time = models.DateField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '价格策略'


class Transaction(models.Model):
    status_chioces = (
        (1, '未支付'),
        (2, '已支付'),
    )

    status = models.IntegerField(verbose_name='状态', choices=status_chioces)
    order_id = models.CharField(verbose_name='订单号', max_length=64, unique=True)

    user = models.ForeignKey(verbose_name='用户', to='UserInfo')
    price_policy = models.ForeignKey(verbose_name='价格策略', to='PricePolicy')

    count = models.IntegerField(verbose_name='数量(年)', help_text='0表示无限期')

    actual_price = models.IntegerField(verbose_name='实际支付')

    start_time = models.DateField(verbose_name='开始时间', null=True, blank=True)
    over_time = models.DateField(verbose_name='结束时间', null=True, blank=True)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '交易记录'


class Project(models.Model):
    color_chices = (
        (1, "#56b8eb"),  # 56b8eb
        (2, "#f28033"),  # f28033
        (3, "#ebc656"),  # ebc656
        (4, "#a2d148"),  # a2d148
        (5, "#20BFA4"),  # #20BFA4
        (6, "#7461c2"),  # 7461c2,
        (7, "#20bfa3"),  # 20bfa3,
    )

    project_name = models.CharField(verbose_name='项目名称', max_length=32)
    desc = models.CharField(verbose_name='描述', max_length=300, null=True, blank=True)
    color = models.SmallIntegerField(verbose_name='颜色', choices=color_chices, default=1)
    is_star = models.BooleanField(verbose_name='是否星标', default=False)
    join_count = models.IntegerField(default=1, verbose_name='参与人数')
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo')
    used_space = models.IntegerField(verbose_name='已使用空间', default=0)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    # cos对象所需要的字段
    bucket = models.CharField(verbose_name='桶名称', max_length=128)
    region = models.CharField(verbose_name='地区', max_length=100, default='ap-nanjing')

    class Meta:
        verbose_name = '项目'


class ProjectUser(models.Model):
    project = models.ForeignKey(Project, verbose_name='项目')
    user = models.ForeignKey(UserInfo, verbose_name='用户')
    is_star = models.BooleanField(verbose_name='是否星标', default=False)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '项目参与者'


class Wiki(models.Model):
    project = models.ForeignKey(verbose_name='项目', to='Project')
    title = models.CharField(verbose_name='标题', max_length=32)
    content = models.TextField(verbose_name='内容')

    # 自关联
    parent = models.ForeignKey(verbose_name='父文章', to='Wiki', related_name='children', null=True, blank=True)

    # 深度
    depth = models.IntegerField(verbose_name='深度', default=1)

    def __str__(self):
        return self.title


class FileManage(models.Model):
    file_type_choices = (
        (1,'文件'),
        (2, '文件夹'),
    )
    project = models.ForeignKey(verbose_name='项目', to='Project')
    file_name = models.CharField(verbose_name='文件名', max_length=32)
    file_cla = models.SmallIntegerField(verbose_name='文件类型', choices=file_type_choices)
    file_size = models.IntegerField(verbose_name='文件大小', null=True, blank=True)
    parent = models.ForeignKey(verbose_name='父目录', to='FileManage', related_name='children', null=True, blank=True)
    key = models.CharField(verbose_name='文件存储在cos中的key', max_length=128)
    update_user = models.ForeignKey(verbose_name='更新者', to='UserInfo')
    file_path = models.CharField(verbose_name='文件路径', max_length=255, null=True,
                                 blank=True)  # https://桶.cos.ap-chengdu/....

    create_time = models.DateTimeField(verbose_name='更新时间', auto_now_add=True)








