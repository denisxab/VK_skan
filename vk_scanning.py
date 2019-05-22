import os
import json
import time
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Firefox 
from selenium.webdriver.firefox.options import Options



def openvk (b):
	try:
		b.get('https://vk.com/im')
		t=b.find_element_by_id('email')
		t.send_keys('89522444900')
		t=b.find_element_by_id('pass')
		t.send_keys('denisKustov2000kustovDenis')
		s=b.find_element_by_id('login_button')
		s.click()
		time.sleep(1)
	except NameError :
		sf = b.find_element_by_name("box_x_button")
		sf.click()







b=webdriver.Firefox()
openvk(b)


u = 0
for x in os.listdir():
	if x == 'ID_gerl1.json':
		with open('ID_gerl1.json','r') as file_json:
			vk_clr = json.load(file_json)
		u = 1
		break
if u == 0:
	with open('ID_gerl.json','r') as file_json:
		vk_clr = []
		for x in json.load(file_json):
			vk_clr.append(x[0])
		with open('ID_gerl1.json','w') as file_json:
			json.dump(vk_clr,file_json)





try:
	for x in range(len(vk_clr)):
		b.get('https://vk.com/id{}'.format(vk_clr[x]))
		print('------------------------')
		resl = input("Что делаем ? {} - {}".format(len(vk_clr),vk_clr[x]))
		if resl == '+':
			with open('Like.txt','a') as file_txt:
				file_txt.write('|{}|'.format(vk_clr[x]))
		if resl == 'S':
			for yuy in range(x):
				vk_clr.pop(0)
			with open('ID_gerl1.json','w') as file_json:
				json.dump(vk_clr,file_json)
				break


finally:
	with open('ID_gerl1.json','w') as file_json:
		json.dump(vk_clr,file_json)

