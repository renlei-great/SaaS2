# import time
# import datetime
#
# # print(datetime.datetime(1997,8,19))
# print(time.gmtime()[0])
#
# ti = int(time.time())
# ti += 60*60*24*12
# print(ti)
# t = ti // (60 * 60 * 24 *12)
# print(t)
# print(time.time())


# import time
# ti = time.gmtime()
# print(ti, type(ti))
# print(ti.tm_year)
# order_id = str(ti.tm_year) + str(ti.tm_mon) + str(ti.tm_mday) + user.username + ':'+  user.id
# print(order_id)
import scripts.base
from django_redis import get_redis_connection
import time

con = get_redis_connection()

con.hmset('pro_django', {'id':1, 'age': 18})
# con.expire('pro_django', 10)
print(con.hgetall('pro_django'))
print(con.hmset('pro_django',{'id': '2'}))
print(con.hmset('pro_django',{'id': '3'}))
print(con.hgetall('pro_django'))
# time.sleep(5)
# print(con.hgetall('pro_django'))
# time.sleep(6)
# print(con.hgetall('pro_django'))

# import uuid
# import bcrypt
# a = str(uuid.uuid4())[0:1]
# b = bcrypt.hashpw(a.encode(), bcrypt.gensalt(5)).decode()
# print(a, b)
# print(bcrypt.checkpw(a.encode(), b.encode()))
# print(str(uuid.uuid4())[0:5])