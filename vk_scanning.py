import requests
import threading
import json
import os

#------------------------------------------------------#
def cleaning_id(all_id,group):
	n = []
	for x in all_id:
		if x[1] == 1:
			if x[2] >= 1999 and x[2] <= 2001:
				if x[3] == 2:
					if x[4] == 1:
						if x[5] <= 800:
							if x[6] == 0 or x[6] == 6 or x[6] == 1:
								n.append(x)

	with open('{}\\ID_gerl.json'.format(group),'w') as file_json:
		json.dump(n,file_json)
########################################################
def vK_skan(отступ,group,token,v):
	global all_id
	counts=1000
	offset = отступ[0]
	while offset <= отступ[1]:
		respons = requests.get('https://api.vk.com/method/groups.getMembers', params={
				"access_token":token,
				'v':v,
				"group_id":group,
				'count':counts,
				'offset':offset,
				'fields':'sex, city, bdate,followers_count,relation,can_write_private_message'
				})
		offset+=counts
		try:
			for i in respons.json()['response']['items']:
				try:
					a = (i['id'],i['sex'],int(i['bdate'].split('.')[2]),i['city']['id'] ,i['can_write_private_message'] ,i['followers_count'] ,i['relation'])
					all_id.append(a)
				except:
					continue
		except KeyError:
			print(respons.json())
########################################################
def sorting_numbers(number_all,stream):
	b = number_all//(stream) # 10
	v = []
	d = []
	for u in range(stream):
		v.append(number_all)
		number_all = number_all - b
		if u > 0:
			f = v[u],v[u-1]
			d.append(f)
			if u+1 == stream:
				v.append(number_all)
				f = v[u+1],v[u]
				d.append(f)
	return d
#------------------------------------------------------#


a = 908500
stream = 30


os.system('Name.txt')
with open('Name.txt','r') as File_name:
	group = File_name.read()



os.mkdir(group) 
token = "f289aa40f289aa40f289aa4039f2e03297ff289f289aa40ae2c6b5129292562a1d4c02f"
v = "5.74"
result_function = sorting_numbers(a,stream)
all_id = []
threading_list=[]
for x in range(stream):
	t = threading.Thread(target=vK_skan,args=(result_function[x],group,token,v))
	threading_list.append(t)
	t.start()
for y in threading_list:
	y.join()
cleaning_id(all_id,group)
print('++++++++++++++++++++++++++')