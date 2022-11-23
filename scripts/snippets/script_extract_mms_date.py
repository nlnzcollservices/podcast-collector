small_list = []
big_list = []

with open("build_results2.txt") as f:
	data = f.read()
for el in data.split("\n"):
	if el.startswith("=001"):
		if not el.split(" ")[-1] in small_list:
 			small_list.append(el.split(" ")[-1])
# 	elif el.startswith("=245"):
# 		small_list.append(el.lstrip("=245 10$a"))
# 		big_list.append(small_list)
# 		small_list=[]
# print(big_list)
print(small_list)
