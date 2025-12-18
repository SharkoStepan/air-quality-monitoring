from database.db import db
from datetime import datetime, timedelta

class Measurement:
    """Модель измерения"""
    
    def __init__(self, id=None, sensor_id=None, value=None, measured_at=None):
        self.id = id
        self.sensor_id = sensor_id
        self.value = value
        self.measured_at = measured_at
    
    @staticmethod
    def create(sensor_id, value):
        """Создание нового измерения"""
        with db.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO measurements (sensor_id, value) VALUES (?, ?)",
                (sensor_id, value)
            )
            return cursor.lastrowid
    
    @staticmethod
    def get_latest_by_sensor(sensor_id):
        """Получение последнего измерения датчика"""
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM measurements WHERE sensor_id = ? ORDER BY measured_at DESC LIMIT 1",
                (sensor_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def get_latest_by_room(room_id):
        """Получение последних измерений всех датчиков в помещении"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT m.*, s.sensor_type, s.location
                FROM measurements m
                JOIN sensors s ON m.sensor_id = s.id
                WHERE s.room_id = ?
                GROUP BY s.sensor_type
                HAVING m.measured_at = MAX(m.measured_at)
            """, (room_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_history(sensor_id, hours=24):
        """Получение истории измерений за последние N часов"""
        with db.get_cursor() as cursor:
            time_threshold = (datetime.now() - timedelta(hours=hours)).isoformat()
            cursor.execute(
                "SELECT * FROM measurements WHERE sensor_id = ? AND measured_at >= ? ORDER BY measured_at ASC",
                (sensor_id, time_threshold)
            )
            return [dict(row) for row in cursor.fetchall()]
