import pymysql
import pandas

conn = pymssql.connect(server='', port='', user='', password='', database='')
cursor = conn.cursor()
query = 'select * from your_table_name'


cursor.execute(query)

# writing content of the sql database into csv file 
# this file will be the input of the model
with open("output.csv","w") as outfile:
    writer = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(col[0] for col in cursor.description)
    for row in cursor:
        writer.writerow(row)