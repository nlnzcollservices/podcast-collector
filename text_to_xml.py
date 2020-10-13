# -*-coding: utf-8 -*-
#python 3

import os
import re
#insert your working directory bellow
script_folder = os.getcwd()
working_folder = "\\".join(script_folder.split("\\")[:-1])
print(working_folder)
def make_dir(path):
    if not os.path.isdir(path):
        os.mkdir(path)
def main():
    #insert path to text templates bellow
    templates_folder = os.path.join(working_folder, "assets",  "text_templates")
    print(templates_folder)
    #insert path to new templates bellow
    new_templates_folder = os.path.join(working_folder,  "assets" , "xml_templates")
    print(new_templates_folder)
    make_dir(templates_folder)
    make_dir(new_templates_folder)
    flag856 = False
    
    print (templates_folder)
    for fl in os.listdir(templates_folder):
        new_xml = '<?xml version="1.0" encoding="UTF-8" ?><collection><record>'
        print(fl)
        templ_name = fl
        with open(os.path.join(templates_folder,fl)) as f:
            template_data = f.read()
        #print(template_data)
        template_data= template_data[:-1].split("\n")
        for field in template_data[2:-1]:
            new_field =""
            print(field)
            field_content = re.findall(r'>(.*?)<',field)[0]
            field_content = field_content.rstrip(" ").lstrip(" ")
            field_content = field_content.replace("#", " ")
            ######################################################################################################################
            #to separate Leader field
            if "LDR"in field:
                #print(field) 
                #print(leader_content)
                new_field = "<leader>{}</leader>".format(field_content)
                #print(new_field)
                new_xml+=new_field
                #new_xml+="\n"
            ##############################################################################################################33
            #to identify tag numbers
            else:
                print(field)
                if not 'mtag id="347"' in field and not ('mtag id="500"' in field and "Archived" in field) and not 'mtag id="505"' in field and not 'Add Primo permalink' in field:
                    id_tag =  re.findall(r'id=(.*?) subfield',field)[0]

                
                #print(id_tag)
            #################################################################################################################33
            #to get controlfields
                    if int(id_tag[1:-1]) <10:
                        
                    #   print (controlfield_data)
                        new_field = "<controlfield tag={}>{}</controlfield>".format(id_tag,field_content)
                        new_xml+=new_field
                        #new_xml+="\n"

            ######################################################################################################################3
            #to get datafields and subfields inside of them
                    else:
                            print(field)
                            ind1 = re.findall(r'subfield1=(.*?) sub',field)[0]
                            ind2 = re.findall(r'subfield2=(.*?)>',field)[0]
                            subfields = field_content.split("!")[1:]
                            new_field = '<datafield tag={} ind1={} ind2={}>'.format(id_tag, ind1, ind2)

                            new_xml+=new_field
                            #new_xml+="\n"
                            for el in subfields:
                                subf_tag = el[0]
                                subf_content = el[2:].lstrip(" ").rstrip(" ")
                                subf_data = '<subfield code="{}">{}</subfield>'.format(subf_tag, subf_content)
                                new_xml+=subf_data
                                #new_xml+="\n"
                            new_xml+="</datafield>"
                            #new_xml+="\n"
        new_xml +='</record></collection>'
        print(new_xml)
        full_new_template_name = os.path.join(new_templates_folder, fl.split("cases_")[-1].replace(" ", "_") + ".xml")
        with open(full_new_template_name, "w") as templatefile:
            templatefile.write(new_xml)
        
    
    
if __name__ == '__main__':
    main()