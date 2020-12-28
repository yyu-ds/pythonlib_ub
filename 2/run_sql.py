from sqlite3 import OperationalError
from sqlite3 import ProgrammingError

os.chdir(r"C:\Users\ub71894\Documents\Python Scripts\sql")
sql_file = 'liteworld.sql'
con = sqlite3.connect('world2.db')
cursor = con.cursor()


def exec_sql_file(cursor, sql_file):
    print ("\n[INFO] Executing SQL script file: '%s'" % (sql_file))
    statement = ""

    for line in open(sql_file):
        if re.match(r'--', line):  # ignore sql comment lines
            continue
        if not re.search(r'[^-;]+;', line):  # keep appending lines that don't end in ';'
            statement = statement + line
        else:  # when you get a line ending in ';' then exec statement and reset for next statement
            statement = statement + line
            #print "\n\n[DEBUG] Executing SQL statement:\n%s" % (statement)
            try:
                cursor.execute(statement)
            except (OperationalError, ProgrammingError) as e:
                print ("\n[WARN] MySQLError during execute statement \n\tArgs: '%s'" % (str(e.args)))

            statement = ""    


exec_sql_file(cursor, sql_file)

con.commit()

con.close()

