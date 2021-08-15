import sqlite3


class DatabaseSetup:
    # datenbank connection
    dbcon = sqlite3.connect("./database.sqlite")
    dbcur = dbcon.cursor()

    dbcur.execute("""
    CREATE TABLE channels (
        channel_id INTEGER constraint channels_pk primary key,
        server_id INTEGER);
    """)

    # Datatypes: NULL, INTEGER, REAL (deziaml number), TEXT, BLOB
    dbcon.commit()
    dbcon.close()
