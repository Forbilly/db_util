from db_util import db, dbms, queue


data_list = dbms.silva.select('gov_policy',
                              fields='id,title,dispatch_number,dispatch_office',
                              condition=[('id','IN', (299199, 299200))],
                              limit=100)
print(data_list)

