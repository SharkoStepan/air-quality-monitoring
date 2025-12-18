from database.db import db

class Equipment:
    """Модель оборудования"""
    
    VALID_TYPES = ['heating', 'ventilation', 'air_conditioner', 'humidifier']
    VALID_STATUSES = ['on', 'off', 'maintenance']
    
    def __init__(self, id=None, room_id=None, equipment_type=None, name=None, 
                 power=None, status='off', auto_mode=True):
        self.id = id
        self.room_id = room_id
        self.equipment_type = equipment_type
        self.name = name
        self.power = power
        self.status = status
        self.auto_mode = auto_mode
    
    @staticmethod
    def create(room_id, equipment_type, name, power=None):
        """Создание нового оборудования"""
        if equipment_type not in Equipment.VALID_TYPES:
            raise ValueError(f"Недопустимый тип оборудования: {equipment_type}")
        
        with db.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO equipment (room_id, equipment_type, name, power) VALUES (?, ?, ?, ?)",
                (room_id, equipment_type, name, power)
            )
            return cursor.lastrowid
    
    @staticmethod
    def get_by_room(room_id):
        """Получение всего оборудования в помещении"""
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM equipment WHERE room_id = ? ORDER BY equipment_type",
                (room_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def update_status(equipment_id, status, auto_mode=None):
        """Обновление статуса оборудования"""
        if status not in Equipment.VALID_STATUSES:
            raise ValueError(f"Недопустимый статус: {status}")
        
        with db.get_cursor() as cursor:
            if auto_mode is not None:
                cursor.execute(
                    "UPDATE equipment SET status = ?, auto_mode = ? WHERE id = ?",
                    (status, 1 if auto_mode else 0, equipment_id)
                )
            else:
                cursor.execute(
                    "UPDATE equipment SET status = ? WHERE id = ?",
                    (status, equipment_id)
                )
    
    @staticmethod
    def get_all():
        """Получение всего оборудования"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT e.*, r.name as room_name 
                FROM equipment e 
                JOIN rooms r ON e.room_id = r.id 
                ORDER BY r.name, e.equipment_type
            """)
            return [dict(row) for row in cursor.fetchall()]
