import os
import re
try:
	from settings import logging, file_folder, template_folder, pr_key, sb_key, logging, start_xml, end_xml
except:
	from settings_prod import logging, file_folder, template_folder, pr_key, sb_key, logging, start_xml, end_xml
my_templates = os.listdir(template_folder)
for temp in my_templates:
	if temp.startswith("mis"):
		temp_path = os.path.join(template_folder, temp)
		#print(temp_path)
		with open(temp_path,"r", encoding = "utf-8") as f:
			data= f.read()
			
		if '2">rdatr<' in data:
			print(temp)
			print(data)
			new_data = data.replace('2">rda<','2">rdatr<')
			# with open(temp_path, "w", encoding = "utf-8") as f:
			# 	f.write(new_data)



			#print(temp)
			# if my_string == "rda": 
			# 	my_new_tag = 'tag="344" ind1=" " ind2=" "><subfield code="a">digital</subfield><subfield code="2">rdatr</subfield>'
			# 	my_old_tag = 'ind1=" " ind2=" " tag="344"><subfield code="a">digital</subfield><subfield code="2">rda</subfield>'
			# 	my_new_template = data.replace(my_old_tag, my_new_tag)
			# 	print(my_new_template)