import os
import json
import time
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Firefox 
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import Soport_webdriver
from tkinter import *
import re

def openvk (b):
	try:
		b.get('https://vk.com/im')
		b.find_element_by_id('email').send_keys('#')
		b.find_element_by_id('pass').send_keys('#')
		b.find_element_by_id('login_button').click()
		time.sleep(1)
	except NameError :
		b.find_element_by_name("box_x_button").click()




with open('Name.txt','r') as File_name:
	label = File_name.read()


Lik = 0


if Lik == 0:
	name1 = '{}\\ID_gerl.json'.format(label)
	name2 = '{}\\ID_gerl1.json'.format(label)

	if 'ID_gerl1.json' in os.listdir('{}\\'.format(label)):
		with open(name2,'r') as file_json:
			vk_clr = json.load(file_json)

	else:
		with open(name1,'r') as file_json:
			vk_clr = []
			for x in json.load(file_json):
				vk_clr.append(x[0])
			with open(name2,'w') as file_json:
				json.dump(vk_clr,file_json)

elif Lik == 1:
	name2 = 'Like.json'
	with open(name2,'r') as file:
		vk_clr = json.load(file)



def ups():
	global i
	global p
	global vk_clr
	global b
	i+=1
	lab0['text']='{}\n-{}-'.format(vk_clr[i],p-i)
	windo.update()
	b.get('https://vk.com/id{}'.format(vk_clr[i]))

	
def dows():
	global i
	global p
	global vk_clr
	global b
	i-=1
	lab0['text']='{}\n-{}-'.format(vk_clr[i],p-i)
	windo.update()
	b.get('https://vk.com/id{}'.format(vk_clr[i]))

	
def set_message ():
	global i
	global p
	global vk_clr
	global b
	with open('text_mail.txt','r') as file_text:
		red = file_text.read()
		red = ' '.join(re.findall(re.compile('[^\n]+'),red))
		v = b.find_element_by_class_name('page_name').text.split(' ')[0]

		try:
			b.find_element_by_id('profile_message_send').click()
		except selenium.common.exceptions.ElementNotInteractableException:
			b.get('https://vk.com/id{}'.format(vk_clr[i]))
			b.find_element_by_id('profile_message_send').click()

		b.find_element_by_id('mail_box_editable').send_keys('Привет {}, {}'.format(v,red))
		# b.find_element_by_id('mail_box_send').click()

def saves():
	global i
	global p
	global vk_clr
	global b
	global Lik

	with open(name2,'w') as file_json:
		json.dump(vk_clr[i:],file_json)


def LIKE():
	global i
	global p
	global vk_clr
	global b
	lab0['text']='||||||||||||||||||||||||||||||||||'
	windo.update()

	with open('Like.json','r') as file_json:
		lls = json.load(file_json)
		lls.append(vk_clr[i])

	with open('Like.json','w') as file_json:
		json.dump(lls,file_json)


def on_closing():
	saves()
	windo.destroy()
	b.close()


i=0
p = len(vk_clr)
windo = Tk()
windo.geometry('{}x{}'.format('380','450'))
frame1 = Frame(windo)
bat0 = Button(frame1,width=10,text='>',bg='#4E51D8',command=ups)
bat1 = Button(frame1,width=10,text='<',bg='#4E51D8',command=dows)
bat2 = Button(frame1,width=10,text='SV',command=saves)

bat3 = Button(windo,width=10,text='Написать',command=set_message)
bat4 = Button(windo,width=10,text='LIKE',command=LIKE)

lab0 = Label(windo,height=5,width=10,text='--')


lab0.pack(fill=BOTH,expand=True)

frame1.pack(fill=BOTH,expand=True)
bat1.pack(side='left',fill=BOTH,expand=True)
bat2.pack(side='left',fill=BOTH,expand=True)
bat0.pack(side='left',fill=BOTH,expand=True)

bat3.pack(fill=BOTH,expand=True)
bat4.pack(fill=BOTH,expand=True)

caps = DesiredCapabilities().FIREFOX
caps["pageLoadStrategy"] = "eager"

b=webdriver.Firefox(desired_capabilities=caps)
openvk(b)


def upss(a):
	ups()

def dowss(a):
	dows()


windo.bind('<Right>',upss)
windo.bind('<Left>',dowss)

windo.protocol("WM_DELETE_WINDOW", on_closing)
windo.wm_attributes('-topmost',1)
windo.mainloop()

a = Soport_webdriver.CLR_Html(b,['page_name','profile_message_send','profile_action_btn','profile_msg_split'])
print(a)


