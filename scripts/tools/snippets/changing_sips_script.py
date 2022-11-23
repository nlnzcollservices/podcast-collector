import os
folder = r"Y:\ndha\pre-deposit_prod\server_side_deposits\prod\ld_scheduled\periodic"

"""This script can bulky correct designation in already built SIPs"""

for fold in os.listdir(folder):
	if "Kete_korero" in fold:
		print(fold)
		folder_path = os.path.join(folder, fold)
		# new_name = fold[:-2]
		# new_folder_path = os.path.join(folder, new_name)
		# os.rename(folder_path, new_folder_path)
		met_path = os.path.join(folder_path, "content", "mets.xml")
		with open(met_path, "r") as f:
			data = f.read()
		new_data = data.replace("<dc:coverage>01</dc:coverage>","<dc:coverage/>")
		with open(met_path, "w") as f:
			f.write(new_data)

