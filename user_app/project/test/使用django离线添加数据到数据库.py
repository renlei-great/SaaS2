import django
import sys
import os

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# 添加
sys.path.append(base_dir)
# 加载
os.environ.setdefault('DJANGO_SETTINGS_MODULE', "saas_29.settings")
# 模拟启动
django.setup(base_dir)

from user_app.project.models import PriceStrategy

PriceStrategy.objects.create(classify='免费版',
                             title='个人免费版',
                             pro_count=3,
                             pro_member=2,
                             pro_space='20M',
                             one_file='5M',)