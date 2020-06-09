from utils.tencent.cos import create_cos


client = create_cos()

res = client.head_object('user-id-8-pro-name-wjcs-5ad5-1302000219', 'pro_id-23-user-id-8- xnhj.jpg')

print(res, type(res), res.get('ETag'))