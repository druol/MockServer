import sqlite3
import json

class DatabaseManager:
   
    def __init__(self, db_name: str, json_path: str):
        self.db_name = db_name
        self.json_path = json_path

    def _execute_query(self, query, params=None):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    def set_database(self):
        create_responses_table = '''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                response TEXT
            )
        '''
        create_history_table = '''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY,
                method TEXT NOT NULL,
                path TEXT NOT NULL,
                status_code TEXT,
                response_body TEXT
            )
        '''
        self._execute_query(create_responses_table)
        self._execute_query(create_history_table)
        print("Таблицы успешно созданы или уже существуют.")
    
    def add_test_data(self):
        request_to_add = [
                ('GET', 'set/ff'),
                ('POST', 'api/gg'),
                ('PUT', 'set/gg'),
                ('DELETE', 'set/gg')
        ]
        with sqlite3.connect(self.db_name) as connetion:
            cursor = connetion.cursor()
            cursor.executemany("INSERT INTO responses (endpoint, method) VALUES (?, ?)", request_to_add)
            print(f"Добавлено {len(request_to_add)} тестовых записей.")

    def get_all_responses(self):
        print("\nЧтение всех записей из 'responses':")
        all_responses = self._execute_query("SELECT * FROM responses")
        
        for resp in all_responses:
            print(f"ID: {resp[0]}, Method: {resp[2]}, Endpoint: {resp[1]}")

    def parse_json(self, json_path: str):
        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            data_to_insert = []
            for endpoint, details in data.items():
                method = details.get("method") 
                response_body = details.get("response")
                response_as_text = json.dumps(response_body, ensure_ascii=False, indent=2)
                normalized_endpoint = "/" + endpoint.strip().lstrip('/')
                data_to_insert.append((normalized_endpoint, method, response_as_text))

            if not data_to_insert:
                print("В файле нет данных для добавления.")
                return

            # Connect to Database
            with sqlite3.connect(self.db_name) as connection:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM responses") 
                cursor.executemany(
                    "INSERT INTO responses (endpoint, method, response) VALUES (?, ?, ?)",
                    data_to_insert
                )
                print(f"Таблица 'responses' очищена и в нее добавлено {cursor.rowcount} новых записей.")

        except FileNotFoundError:
            print(f"Ошибка: Файл не найден по пути '{json_path}'")
        except json.JSONDecodeError:
            print(f"Ошибка: Не удалось прочитать JSON из файла '{json_path}'. Проверьте его формат.")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

    def clear_table(self, table_name: str):
        self._execute_query(f'DELETE FROM {table_name}')
        print(f"Все записи из таблицы '{table_name}' были успешно удалены.")

    def run_full_setup_cycle(self):
        print("--- Начало полного цикла настройки БД ---")
        self.set_database()
        self.parse_json(self.json_path)
        print("--- Цикл настройки БД завершен ---")
    
    def find_response(self, endpoint: str, method: str):

        query = "SELECT response FROM responses WHERE endpoint = ? AND method = ?"

        result = self._execute_query(query, (endpoint, method.upper()))
        
        if result:
            response_text = result[0][0]
            return json.loads(response_text)
        return None


    # ---- Для работы с историей запросов ---- #
    def add_history_record(self, record: dict):

        query = """
            INSERT INTO history (method, path, status_code, response_body)
            VALUES (:method, :path, :status_code, :response_body)
        """
        self._execute_query(query, record)

    def get_history(self):
        query = "SELECT id, method, path, status_code, response_body FROM history ORDER BY id"

        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def get_history_record_by_id(self, record_id: int):

        query = "SELECT id, method, path, status_code, response_body FROM history WHERE id = ?"
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (record_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        


    def update_response(self, endpoint: str, method: str, new_response: any) -> bool:
        response_as_text = json.dumps(new_response, ensure_ascii=False, indent=2)
        query = "UPDATE responses SET response = ? WHERE endpoint = ? AND method = ?"
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(query, (response_as_text, endpoint, method.upper()))
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении записи: {e}")
            return False