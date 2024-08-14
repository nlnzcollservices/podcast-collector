from playhouse.migrate import *

try:
	from settings_prod import database_fullname
except:
	from settings import database_fullname


my_db = SqliteDatabase(database_fullname)
migrator = SqliteMigrator(my_db)

def add_column(table_name, field_name, field_content):
	"""Adds new column to existing table
	Parameters:
		table_name(str) - name of the table with lower letter.
		field_name(str) - name of the new field to add_column.
		field_content(obj db field) - settings for field
	Returns:
		None
	"""
	migrate(migrator.add_column(table_name, field_name, field_content))

def drop_column(table_name, field_name):
	"""Deletes existing column from table
	Parameters:
		table_name(str) - name of the table with lower letter.
		field_name(str) - name of the new field to add_column.
	Returns:
		None
	"""
	migrate(migrator.drop_column(table_name, field_name))

def rename_column(table_name, old_field_name, new_field_name):
    """
    Renames an existing column in a table.
    
    Parameters:
        table_name (str): Name of the table (lowercase).
        old_field_name (str): Current name of the field to rename.
        new_field_name (str): New name for the field.
        
    Returns:
        None
    """
    migrate(migrator.rename_column(table_name, old_field_name, new_field_name))


def main():

	"""This is support tool for modifying database structure"""

	table_name = "episode"
	field_name = "bib_numbering"
	field_content = CharField(default=None, max_length = 50, null = True)
	add_column(table_name, field_name, field_content)


	# old_field_name = "f100"
	# new_field_name = "cataloguer"
	# rename_column(table_name, old_field_name, new_field_name)
	

	#field_content = BooleanField(default = False)
	#field_name2= "seas_n"
	#drop_column(table_name, field_name2)
	
if __name__ == '__main__':
	main()