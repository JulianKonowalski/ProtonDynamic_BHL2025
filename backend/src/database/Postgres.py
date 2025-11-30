import os
import psycopg2

class Postgres:

    def __init__(self):
        self.connection = psycopg2.connect(
            database="bhl",
            user="admin123",
            password=os.getenv("POSTGRES_PSWD"),
            host="localhost",
            port=5432
        )

    def createUser(self, user_name: str, user_surname: str, rfid: str) -> None:
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                f"""
                    INSERT INTO users (social_credit, role_id, user_name, user_surname, rfid) VALUES
                        (0, 2, '{user_name}', '{user_surname}', {rfid});
                """
            )
            self.connection.commit()
        except: self.connection.rollback()
        cursor.close()

    def getUserData(self, rfid: int) -> dict | None:
        cursor = self.connection.cursor()
        rfid=str(rfid)
        cursor.execute("SELECT * FROM users WHERE rfid=%s;", (rfid,))
        result = cursor.fetchone()
        cursor.close()
        if not result: return None
        return {
            "id": result[0], 
            "social_credit": result[1],
            "role_id": result[2], 
            "user_name": result[3],
            "user_surname": result[4],
            "rfid": result[5]
        }
    
    def getSensorData(self, api_key: str) -> dict | None:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sensors WHERE api_key=%s", (api_key,))
        result = cursor.fetchone()
        cursor.close()
        if not result: return None
        return {
            "id": result[0],
            "api_key": result[1]
        }

    def getTaskTypes(self) -> list[dict]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM task_types;")
        results = cursor.fetchall()
        cursor.close()
        data = []
        for result in results:
            data.append({
                "id": result[0],
                "name": result[1]
            })
        return data


    def getTasks(self) -> list[dict]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tasks;")
        results = cursor.fetchall()
        cursor.close()
        data = []
        for result in results:
            data.append({
                "id": result[0],
                "type": result[1],
                "finished": result[2],
                "owner": result[3]
            })
        return data

    def updateTask(self, task_id: int, finished: bool, owner: int | None):
        cursor = self.connection.cursor()

        finished = "true" if finished else "false"
        owner = str(owner) if owner is not None else "NULL"
        task_id = str(task_id)
        cursor.execute(
            f"""
            UPDATE tasks
            SET finished={finished}, owner={owner}
            WHERE id={task_id};
            """
        )
        self.connection.commit()
        cursor.close()