import scripts.base

from web import models

def run():
    models.PricePolicy.objects.create(
        category = 1,
        title = '个人免费版',
        price=0,
        pro_num=3,
        pro_member=2,
        pro_space=20,
        per_file_size=5,
    )


if __name__ == "__main__":
    run()