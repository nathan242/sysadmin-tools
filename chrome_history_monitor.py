#!/usr/bin/python

import sys
import os
import getopt
import time
import signal
import warnings
import subprocess
import re
import MySQLdb
import sqlite3


def help():
    sys.stderr.write("\n")
    sys.stderr.write("=== Chrome History Tracker ===\n")
    sys.stderr.write("Usage:\n")
    sys.stderr.write(sys.argv[0]+" [-h] --history_db=FILE --working_dir=DIR --wait=SECONDS [--storage_type=mysql|sqlite3 --table_name=TABLE --commit_every=N [--mysql_host=HOST --mysql_user=USER --mysql_password=PASS --mysql_db=DB] [--sqlite_file=DB]]\n")
    sys.stderr.write("\n")
    sys.stderr.write("Main options:\n")
    sys.stderr.write(" -h                                  Show this help.\n")
    sys.stderr.write(" --history_db=FILE                   Location of Chrome history DB file.\n")
    sys.stderr.write(" --working_dir=DIR                   Working directory for data.\n")
    sys.stderr.write(" --wait=SECONDS                      Time to wait before refreshing history data.\n")
    sys.stderr.write("\n")
    sys.stderr.write("Data capture options:\n")
    sys.stderr.write(" --storage_type=mysql|sqlite3        Capture history data to DB. Can use MySQL or Sqlite3 DB.\n")
    sys.stderr.write(" --table_name=TABLE                  Name of DB table to store data.\n")
    sys.stderr.write(" --commit_every=N                    Commit DB transaction every N inserts.\n")
    sys.stderr.write("\n")
    sys.stderr.write("MySQL options:\n")
    sys.stderr.write(" --mysql_host=HOST                   MySQL server address.\n")
    sys.stderr.write(" --mysql_user=USER                   MySQL username.\n")
    sys.stderr.write(" --mysql_password=PASS               MySQL password.\n")
    sys.stderr.write(" --mysql_db=DB                       MySQL DB name.\n")
    sys.stderr.write("\n")
    sys.stderr.write("Sqlite3 options:\n")
    sys.stderr.write(" --sqlite_file=DB                    Sqlite3 DB file to use.\n")
    sys.stderr.write("\n")


class Database:
    def __init__(self, db_type, db_config, commit_every, db_init):
        """
        db_type - mysql or sqlite3
        db_config - mysql:(db_host, db_user, db_pass, db_db) sqlite3:(db_file)
        commit_every - Commit after N statements
        db_init - Tuple conaining statements to execute on class instantiation
        """
        self.commit_every = commit_every
        self.sqlcount = 0
        
        if db_type == "mysql":
            self.db = MySQLdb.connect(db_config[0], db_config[1], db_config[2], db_config[3])
        elif db_type == "sqlite3":
            self.db = sqlite3.connect(db_config[0])

        self.c = self.db.cursor()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            for i in range(0, len(db_init)):
                self.c.execute(db_init[i])

    def query(self, sql, data = False):
        if data == False:
            self.c.execute(sql)
            self.commit_counter(1)
        else:
            self.c.execute(sql, data)
            self.commit_counter(1)

    def commit_counter(self, count):
        self.sqlcount += count
        if self.sqlcount == self.commit_every:
            self.commit()

    def commit(self):
        self.sqlcount = 0
        self.db.commit()


# Check command line options
wait = 30
history_db = None
working_dir = None
storage_type = None
table_name = None
sqlite_file = None
mysql_host = None
mysql_user = None
mysql_password = None
mysql_db = None
commit_every = 10
cp_comm = "[COPY COMMAND]"

try:
    optlist, args = getopt.getopt(sys.argv[1:], "h", ["wait=", "history_db=", "working_dir=", "storage_type=", "table_name=", "sqlite_file=", "mysql_host=", "mysql_user=", "mysql_password=", "mysql_db=", "commit_every="])
except getopt.GetoptError as err:
    sys.stderr.write(str(err)+"\n")
    help()
    sys.exit(1)

for o, a in optlist:
    if o == "-h":
        help()
        sys.exit(0)
    elif o == "--wait":
        wait = a
    elif o == "--history_db":
        history_db = a
    elif o == "--working_dir":
        working_dir = a
    elif o == "--storage_type":
        storage_type = a
    elif o == "--table_name":
        table_name = re.sub("[^0-9a-zA-Z]", "_", a)
    elif o == "--sqlite_file":
        sqlite_file = a
    elif o == "--mysql_host":
        mysql_host = a
    elif o == "--mysql_user":
        mysql_user = a
    elif o == "--mysql_password":
        mysql_password = a
    elif o == "--mysql_db":
        mysql_db = a
    elif o == "--commit_every":
        commit_every = a
    else:
        sys.stderr.write("Unknown option: "+str(o)+"\n")
        sys.exit(1)

if re.search("^[0-9]+$", str(wait)) is None:
    sys.stderr.write("Wait time must be an integer!\n")
    sys.exit(1)

wait = int(wait)

if history_db == None:
    sys.stderr.write("Please specify history DB file!\n")
    sys.exit(1)

if working_dir == None:
    sys.stderr.write("Please specify a working directory!\n")
    sys.exit(1)

if not os.path.isfile(history_db):
    sys.stderr.write("History DB does not exist or is not a file!\n")
    sys.exit(2)

if not os.path.isdir(working_dir):
    sys.stderr.write("Working directory does not exist or os not a directory!\n")
    sys.exit(2)

if storage_type != None:
    if storage_type not in ("mysql", "sqlite3"):
        sys.stderr.write("Storage type must be \"mysql\" or \"sqlite3\"!\n")
        sys.exit(1)
    if storage_type == "mysql":
        if mysql_host == None:
            sys.stderr.write("Mysql host not set!\n")
            sys.exit(1)
        if mysql_user == None:
            sys.stderr.write("Mysql user not set!\n")
            sys.exit(1)
        if mysql_password == None:
            sys.stderr.write("Mysql password not set!\n")
            sys.exit(1)
        if mysql_db == None:
            sys.stderr.write("Mysql DB not set!\n")
            sys.exit(1)
    elif storage_type == "sqlite3":
        if sqlite_file == None:
            sys.stderr.write("Sqlite3 database file not set!\n")
            sys.exit(1)
    if table_name == None:
        sys.stderr.write("Please specify a table name!\n")
        sys.exit(1)
    if re.search("^[0-9]+$", str(commit_every)) is None:
        sys.stderr.write("Commit_every must be an integer!\n")
        sys.exit(1)
    commit_every = int(commit_every)


# Set up storage DB
if storage_type == "mysql":
    db_config = (mysql_host, mysql_user, mysql_password, mysql_db)
    db_init = ("CREATE TABLE IF NOT EXISTS `"+str(table_name)+"` (`id` INT(11) UNSIGNED PRIMARY KEY AUTO_INCREMENT, `hist_id` INT(11), `datetime` datetime, `url` VARCHAR(500), `title` VARCHAR(500))",)
    db = Database("mysql", db_config, commit_every, db_init)
elif storage_type == "sqlite3":
    db_config = (sqlite_file,)
    db_init = ("CREATE TABLE IF NOT EXISTS `"+str(table_name)+"` (`hist_id` INTEGER, `datetime` TEXT, `url` TEXT, `title` TEXT)",)
    db = Database("sqlite3", db_config, commit_every, db_init)
else:
    db = None


# Exit signal handling
def exit_handler(signum, frame):
    global db
    print "Signal "+str(signum)+" received."
    if db != None:
        sys.stdout.write("Committing database transaction...")
        db.commit()
        sys.stdout.write("Done\n")
    print "Exiting"
    sys.stdout.flush()
    sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)
signal.signal(signal.SIGTERM, exit_handler)


last_id = 0

while True:
    # Sync history file
    try:
        if os.name == "nt":
            cp_comm = "copy"
            copy = subprocess.Popen([cp_comm, history_db, working_dir+"\\History", "/Y"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            cp_comm = "rsync"
            copy = subprocess.Popen([cp_comm, history_db, working_dir+"/History"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            
        copy_ret = copy.communicate()[0]
        copy_rc = copy.returncode
        if copy_rc != 0:
            sys.stderr.write("\n"+cp_comm+" failed! [Returncode = "+str(copy_rc)+"]: "+str(copy_ret)+"\n")
            time.sleep(wait)
            continue
    except:
        sys.stderr.write("\n"+cp_comm+" failed!\n")
        time.sleep(wait)
        continue

    if db == None:
        highest_id = last_id
    else:
        db.query("SELECT MAX(`hist_id`) FROM `"+str(table_name)+"`");
        highest_id = db.c.fetchone()[0]
    
    if highest_id == None:
        highest_id = 0

    try:
        hist_db = sqlite3.connect(working_dir+"/History")
        cur = hist_db.cursor()
        cur.execute("SELECT visits.id, datetime(((visits.visit_time/1000000)-11644473600), 'unixepoch'), urls.url, urls.title FROM urls, visits WHERE urls.id = visits.url AND visits.id > "+str(highest_id))
        result = cur.fetchall()
    except:
        sys.stderr.write("\nCannot read Chrome histroy DB!\n")
        time.sleep(wait)
        continue

    for i in range(0, len(result)):
        last_id = data_id = str(result[i][0])
        data_datetime = result[i][1].encode('ascii', errors='ignore')
        data_url = result[i][2].encode('ascii', errors='ignore')
        data_title = result[i][3].encode('ascii', errors='ignore')

        print ""
        print "ID: "+data_id+" DATETIME: "+data_datetime+" URL: "+data_url+" TITLE: "+data_title
        print ""

        if db != None:
            if storage_type == "mysql":
                db.query("INSERT INTO `"+str(table_name)+"` (`hist_id`, `datetime`, `url`, `title`) VALUES (%s, %s, %s, %s)", (data_id, data_datetime, data_url, data_title))
            elif storage_type == "sqlite3":
                db.query("INSERT INTO `"+str(table_name)+"` (`hist_id`, `datetime`, `url`, `title`) VALUES (?, ?, ?, ?)", (data_id, data_datetime, data_url, data_title))

    if db != None:
        db.commit()
    hist_db.close()
    time.sleep(wait)

