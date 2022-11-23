import os
import csv
try:
	from settings_prod import  ndha_report_folder, ndha_used_report_folder,logging
except:
	from settings import   ndha_report_folder, ndha_used_report_folder,logging
logger = logging.getLogger(__name__)
files = os.listdir(ndha_used_report_folder)
for el in files:
	print(el)
	my_report = os.path.join(ndha_used_report_folder, el)
	with open(my_report,"r", encoding = 'utf-8') as csvfile:
		reader = csv.reader(csvfile, delimiter = ",")
		try:
			next(reader)
			next(reader)
			next(reader)
			next(reader)
		except Exception as e:
			logger.error(str(e))

			move_flag = False
		try:
			for row in reader:
				if len(row)>3:
					print(row)
		except Exception as e:
			print(str(e))

