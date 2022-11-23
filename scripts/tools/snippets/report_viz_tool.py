import json
import pandas as pd
import matplotlib.pyplot as plt
import os
import pyjsonviewer
def json_viz(json_file_path):
	print(json_file_path)

	with open(json_file_path, "r") as f:
		json_object = json.load(f)

	pyjsonviewer.view_data(json_data=json_object)
if __name__ == '__main__':
	script_folder = r"Y:\ndha\pre-deposit_prod\LD_working\podcasts\log\reports\cleaning_report_10_2022"
	json_file_path= os.path.join(script_folder,"podcast_cleaning_report.json")
	

	json_viz(json_file_path)