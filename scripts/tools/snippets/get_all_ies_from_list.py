from bs4 import BeautifulSoup as bs
from alma_tools import AlmaTools
from database_handler import DbHandler

my_alma = AlmaTools("prod")

def insert_ies():
	
	""" Requests mms_id list from db, passes them to Alma_Tools, parses list of representation xml to extract ies, inserts  tehm to podcasts.db """
	ies_to_delete =[]
	ies_list = ['IE57798846', 'IE57797834', 'IE57797871', 'IE57798899', 'IE57798904', 'IE57797957', 'IE57797994', 'IE57798032', 'IE57798958', 'IE57798963', 'IE57798137', 'IE57798187', 'IE57799012', 'IE57799015']
	mms_list = ['9919009361402836', '9919009361302836', '9919009361202836', '9919009262202836', '9919009262102836', '9919009262002836', '9919009361102836', '9919009361002836', '9919009360902836', '9919009360802836', '9919009360702836', '9919009360602836', '9919009360502836', '9919009360402836']
	for mms in mms_list:
		my_alma.get_representations(mms)
		rep_grab = bs(my_alma.xml_response_data, 'lxml-xml' )
		reps = rep_grab.find( 'representations' ).find_all('id' )
		ies = rep_grab.find_all( 'originating_record_id' )
		for ie in ies:
			for el in ie:
				#print(el)
				my_ie = el.split(":")[-1]
				if my_ie not in ies_list:
				 	ies_to_delete.append([my_ie,mms])
	for el in ies_to_delete:
		print("'"+el[1] )

def find_double_representations():

	my_db = DbHandler()
	mms_dict = my_db.db_reader(["mis_mms", "episode_title", "episode_id", "ie_num"],None,True)
	for el in mms_dict:
		
		if el != {}:
			print(el["episode_id"])
			my_alma.get_representations(el["mis_mms"])
			rep_grab = bs(my_alma.xml_response_data, 'lxml-xml' )
			try:
				reps = rep_grab.find( 'representations' ).find_all('id' )
				ies = rep_grab.find_all( 'originating_record_id' )

				print(ies)
				if len(ies)>1:
					print(len(ies))
					print(el["mis_mms"],el["episode_title"], el["ie_num"])

			except Exception as e:
				print(str(e))
				print(reps)




		 		
def main():

	find_double_representations()

if __name__ == "__main__":
	main()
