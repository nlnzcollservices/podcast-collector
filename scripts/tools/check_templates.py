import os
templates = r"Y:\ndha\pre-deposit_prod\LD_working\podcasts\assets\templates"
for el in os.listdir(templates):
	#print(el)
	tmp = os.path.join(templates,el)
	with open(tmp,"r", encoding='utf-8') as f:
		data = f.read()
	if 'tag="100"' in data:
		print(el.split(".")[0].lstrip("mis_Podcast_").replace("_", " "))


