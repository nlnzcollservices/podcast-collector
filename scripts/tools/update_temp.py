sets = ["12558695740002836"]#all podcasts MGR
	#Planning
for st in sets:
	my_alma.get_set_members(st,{'limit':'100',"offset":str(0)})
	print (my_alma.xml_response_data)
	number_of_records = re.findall('total_record_count="{}">')[0]
	offset = 0
	offset_step = 100
	title_list = []
 	for i in range(number_of_records//100+1):
		offset = offset+offset_step
		my_alma.get_set_members(st,{'limit':'100',"offset":str(offset)})
			print(my_alma.xml_response_data)
			bibs = re.findall(r"<id>(.*?)</id>", my_alma.xml_response_data)	
			print(bibs)
			for ind in range(len(bibs)):
				my_alma.get_bib(bibs[ind])
				print(my_alma.xml_response_data)