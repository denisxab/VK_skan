from selenium import webdriver 




def CLR_Html(braws,Namess):

	otvet = []
	all_otvet = []

	# a = Soport_webdriver.CLR_Html(b,['mail_box_send'])

	for name in Namess:

		try:
			all_otvet.append(braws.find_element_by_id(name).text)
			otvet.append('find_element_by_id')
		except:
			pass


		try:
			all_otvet.append(braws.find_element_by_name(name).text)
			otvet.append('find_element_by_name')
		except:
			pass


		try:
			all_otvet.append(braws.find_element_by_xpath(name).text)
			otvet.append('find_element_by_xpath')
		except:
			pass

		try:
			all_otvet.append(braws.find_element_by_link_text(name).text)
			otvet.append('find_element_by_link_text')
		except:
			pass


		try:
			all_otvet.append(braws.find_element_by_partial_link_text(name).text)
			otvet.append('find_element_by_partial_link_text')
		except:
			pass


		try:
			all_otvet.append(braws.find_element_by_tag_name(name).text)
			otvet.append('find_element_by_tag_name')
		except:
			pass


		try:
			all_otvet.append(braws.find_element_by_class_name(name).text)
			otvet.append('find_element_by_class_name')
		except:
			pass

		try:
			all_otvet.append(braws.find_element_by_css_selector(name).text)
			otvet.append('find_element_by_css_selector')
		except:
			pass



	io = ''
	for x in range(len(otvet)):
		io+='{} |-| {} |-| {}\n'.format(str(Namess[x]),str(otvet[x]),str(all_otvet[x]))
	return io

	

