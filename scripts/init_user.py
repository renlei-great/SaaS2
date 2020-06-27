import scripts.base
import datetime
from datetime import date, timedelta

from web import models

def run():
    # models.PricePolicy.objects.create(
    #     category = 1,
    #     title = '个人免费版',
    #     price=0,
    #     pro_num=3,
    #     pro_member=2,
    #     pro_space=20,
    #     per_file_size=5,
    # )

    '''
    if(n<0):  获取指点天
        n = abs(n)
        return date.today()-timedelta(days=n)
    else:
        return date.today()+timedelta(days=n)
    '''

    models.Transaction.objects.create(
        status=2,
        order_id="000",
        count=1,
        actual_price=200,
        start_time=date.today()-timedelta(days=10),
        over_time=date.today()+timedelta(days=355),
        price_policy_id=2,
        user_id=8
    )



if __name__ == "__main__":
    run()