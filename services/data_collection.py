from models.sensor import Sensor
from models.measurement import Measurement

class DataCollectionService:
    """Сервис сбора данных с датчиков"""
    
    @staticmethod
    def collect_measurement(sensor_id, value):
        """Сбор и сохранение измерения от датчика"""
        if value < 0:
            raise ValueError("Значение измерения не может быть отрицательным")
        
        return Measurement.create(sensor_id, value)
    
    @staticmethod
    def get_room_current_state(room_id):
        """Получение текущего состояния микроклимата в помещении"""
        measurements = Measurement.get_latest_by_room(room_id)
        
        state = {
            'temperature': None,
            'humidity': None,
            'co2': None,
            'dust': None
        }
        
        for measurement in measurements:
            sensor_type = measurement['sensor_type']
            state[sensor_type] = {
                'value': float(measurement['value']),
                'measured_at': measurement['measured_at'],
                'location': measurement['location']
            }
        
        return state
    
    @staticmethod
    def validate_sensors_in_room(room_id):
        """Проверка наличия всех необходимых датчиков в помещении"""
        sensors = Sensor.get_by_room(room_id)
        sensor_types = {s['sensor_type'] for s in sensors}
        
        required_types = set(Sensor.VALID_TYPES)
        missing_types = required_types - sensor_types
        
        return {
            'is_valid': len(missing_types) == 0,
            'missing_sensors': list(missing_types)
        }
