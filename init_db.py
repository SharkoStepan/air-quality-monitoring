#!/usr/bin/env python3
"""
Скрипт инициализации базы данных и добавления тестовых данных
"""

from database.db import db
from models.room import Room
from models.sensor import Sensor
from models.equipment import Equipment
from models.measurement import Measurement
from services.data_collection import DataCollectionService
import random

def init_database():
    """Инициализация схемы базы данных"""
    print("Инициализация схемы базы данных...")
    try:
        db.init_db()
        print("✓ База данных инициализирована успешно")
    except Exception as e:
        print(f"✗ Ошибка инициализации БД: {e}")
        return False
    return True

def create_test_data():
    """Создание тестовых данных"""
    print("\nСоздание тестовых данных...")
    
    try:
        # Создание помещений
        print("\nСоздание помещений...")
        rooms = [
            ("Офис 101", 45.5, "Главный офис на первом этаже"),
            ("Конференц-зал", 65.0, "Зал для совещаний на втором этаже"),
            ("Серверная", 25.0, "Помещение с серверным оборудованием")
        ]
        
        room_ids = []
        for name, area, desc in rooms:
            room_id = Room.create(name, area, desc)
            room_ids.append(room_id)
            print(f"  ✓ Создано помещение: {name} (ID: {room_id})")
        
        # Создание датчиков для каждого помещения
        print("\nСоздание датчиков...")
        sensor_types = ['temperature', 'humidity', 'co2', 'dust']
        all_sensors = []
        
        for room_id in room_ids:
            for sensor_type in sensor_types:
                sensor_id = Sensor.create(room_id, sensor_type, f"Датчик {sensor_type}")
                all_sensors.append((sensor_id, sensor_type))
                print(f"  ✓ Создан датчик: {sensor_type} для помещения {room_id}")
        
        # Создание оборудования
        print("\nСоздание оборудования...")
        equipment_data = [
            (room_ids[0], 'heating', 'Радиатор 1', 2000),
            (room_ids[0], 'ventilation', 'Вентилятор 1', 150),
            (room_ids[0], 'humidifier', 'Увлажнитель 1', 50),
            (room_ids[1], 'air_conditioner', 'Кондиционер 1', 3500),
            (room_ids[1], 'ventilation', 'Вентилятор 2', 200),
            (room_ids[2], 'air_conditioner', 'Кондиционер 2', 4000),
            (room_ids[2], 'ventilation', 'Вентилятор 3', 300),
        ]
        
        for room_id, eq_type, name, power in equipment_data:
            eq_id = Equipment.create(room_id, eq_type, name, power)
            print(f"  ✓ Создано оборудование: {name} (ID: {eq_id})")
        
        # Создание тестовых измерений
        print("\nСоздание тестовых измерений...")
        measurement_ranges = {
            'temperature': (18, 26),
            'humidity': (35, 65),
            'co2': (400, 1200),
            'dust': (0.02, 0.20)
        }
        
        for sensor_id, sensor_type in all_sensors:
            min_val, max_val = measurement_ranges[sensor_type]
            value = random.uniform(min_val, max_val)
            DataCollectionService.collect_measurement(sensor_id, value)
            print(f"  ✓ Создано измерение: {sensor_type} = {value:.2f}")
        
        print("\n✓ Тестовые данные успешно созданы")
        
    except Exception as e:
        print(f"\n✗ Ошибка создания тестовых данных: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Главная функция"""
    print("="*60)
    print("Инициализация системы мониторинга качества воздуха")
    print("="*60)
    
    if not init_database():
        return
    
    answer = input("\nХотите создать тестовые данные? (y/n): ")
    if answer.lower() in ['y', 'yes', 'д', 'да']:
        create_test_data()
    
    print("\n" + "="*60)
    print("Инициализация завершена!")
    print("Запустите приложение командой: python app.py")
    print("="*60)

if __name__ == '__main__':
    main()
