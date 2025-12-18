from database.db import db

class Room:
    """Модель помещения"""
    
    def __init__(self, id=None, name=None, area=None, description=None):
        self.id = id
        self.name = name
        self.area = area
        self.description = description
    
    @staticmethod
    def create(name, area, description=None):
        """Создание нового помещения"""
        with db.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO rooms (name, area, description) VALUES (?, ?, ?)",
                (name, area, description)
            )
            return cursor.lastrowid
    
    @staticmethod
    def get_all():
        """Получение всех помещений"""
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM rooms ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_by_id(room_id):
        """Получение помещения по ID"""
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def delete(room_id):
        """Удаление помещения"""
        with db.get_cursor() as cursor:
            cursor.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
