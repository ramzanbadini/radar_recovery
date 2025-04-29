import sqlite3

class DatabaseManager:
    def __init__(self, db_name="radar_systems.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS systems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            system_name TEXT NOT NULL,
            description TEXT,
            upload_date TEXT,
            uploader_name TEXT,
            video_path TEXT,
            radar_type TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def insert_system(self, parent_id, system_name, description, upload_date, uploader_name, video_path, radar_type):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO systems (parent_id, system_name, description, upload_date, uploader_name, video_path, radar_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (parent_id, system_name, description, upload_date, uploader_name, video_path, radar_type))
        self.conn.commit()
        return cursor.lastrowid

    def get_top_level_systems(self, radar_type):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, system_name FROM systems WHERE radar_type = ? AND parent_id IS NULL", (radar_type,))
        return cursor.fetchall()

    def get_subsystems(self, parent_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, system_name FROM systems WHERE parent_id = ?", (parent_id,))
        return cursor.fetchall()

    def get_system_details(self, system_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM systems WHERE id = ?", (system_id,))
        return cursor.fetchone()

    def delete_system(self, system_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM systems WHERE id=?", (system_id,))
        self.conn.commit()

       # return cursor.fetchone()

    def combo_data(self,radar_type):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, system_name FROM systems WHERE radar_type = ? AND parent_id IS NULL", (radar_type,))
        return cursor.fetchall()


##db = DatabaseManager("radar_systems.db")
##print(db.delete_system(4))
##
##
##print(" ")
##
##for entry in db.combo_data("Radar 1"):
##    print (entry[1])
##    print(" ")

