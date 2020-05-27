import re

stra = '/web/project/234/asfa'

res = re.match(r'(/web/\w+)/', stra).group(1)
print(res)