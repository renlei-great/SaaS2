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


import time
ti = time.gmtime()
print(ti, type(ti))
print(ti.tm_year)
# order_id = str(ti.tm_year) + str(ti.tm_mon) + str(ti.tm_mday) + user.username + ':'+  user.id
# print(order_id)