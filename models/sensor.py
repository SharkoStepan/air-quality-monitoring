from database.db import db

class Sensor:
    """Модель датчика"""
    
    VALID_TYPES = ['temperature', 'humidity', 'co2', 'dust']
    
    def __init__(self, id=None, room_id=None, sensor_type=None, location=None, status='active'):
        self.id = id
        self.room_id = room_id
        self.sensor_type = sensor_type
        self.location = location
        self.status = status
    
    @staticmethod
    def create(room_id, sensor_type, location=None):
        """Создание нового датчика"""
        if sensor_type not in Sensor.VALID_TYPES:
            raise ValueError(f"Недопустимый тип датчика: {sensor_type}")
        
        with db.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO sensors (room_id, sensor_type, location) VALUES (?, ?, ?)",
                (room_id, sensor_type, location)
            )
            return cursor.lastrowid
    
    @staticmethod
    def get_by_room(room_id):
        """Получение всех датчиков в помещении"""
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sensors WHERE room_id = ? ORDER BY sensor_type",
                (room_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_all():
        """Получение всех датчиков"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT s.*, r.name as room_name 
                FROM sensors s 
                JOIN rooms r ON s.room_id = r.id 
                ORDER BY r.name, s.sensor_type
            """)
            return [dict(row) for row in cursor.fetchall()]
