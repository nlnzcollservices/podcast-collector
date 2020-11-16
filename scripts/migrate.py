from playhouse.migrate import *

from settings import database_fullname

my_db = SqliteDatabase(database_fullname)
migrator = SqliteMigrator(my_db)



def add_column():


	sip = BooleanField(default=False)
	migrate(
	migrator.add_column('episode', 'sip', sip)
	)

def drop_column():


   migrate(
        migrator.drop_column('episode', 'seas_numb'),
    )


#drop_column()
add_column()