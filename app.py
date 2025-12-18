from flask import Flask, render_template, request, jsonify, redirect, url_for
from config import Config
from database.db import db
from models.room import Room
from models.sensor import Sensor
from models.measurement import Measurement
from models.equipment import Equipment
from services.data_collection import DataCollectionService
from services.analysis import AnalysisService
from services.decision_making import DecisionMakingService
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    """Главная страница с общей информацией"""
    rooms = Room.get_all()
    total_sensors = len(Sensor.get_all())
    total_equipment = len(Equipment.get_all())
    
    return render_template('index.html', 
                         rooms=rooms,
                         total_sensors=total_sensors,
                         total_equipment=total_equipment)

@app.route('/rooms')
def rooms():
    """Страница управления помещениями"""
    rooms_list = Room.get_all()
    return render_template('rooms.html', rooms=rooms_list)

@app.route('/api/rooms', methods=['POST'])
def create_room():
    """API: Создание нового помещения"""
    data = request.get_json()
    try:
        room_id = Room.create(
            name=data['name'],
            area=float(data['area']),
            description=data.get('description')
        )
        return jsonify({'success': True, 'room_id': room_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/rooms/<int:room_id>', methods=['DELETE'])
def delete_room(room_id):
    """API: Удаление помещения"""
    try:
        Room.delete(room_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/room/<int:room_id>')
def room_detail(room_id):
    """Детальная информация о помещении"""
    room = Room.get_by_id(room_id)
    if not room:
        return "Помещение не найдено", 404
    
    sensors = Sensor.get_by_room(room_id)
    equipment_list = Equipment.get_by_room(room_id)
    
    # Получение текущих показателей
    current_state = DataCollectionService.get_room_current_state(room_id)
    analysis = AnalysisService.analyze_room_air_quality(room_id)
    
    return render_template('room_detail.html',
                         room=room,
                         sensors=sensors,
                         equipment=equipment_list,
                         current_state=current_state,
                         analysis=analysis,
                         standards=Config.AIR_QUALITY_STANDARDS)

@app.route('/api/sensors', methods=['POST'])
def create_sensor():
    """API: Создание нового датчика"""
    data = request.get_json()
    try:
        sensor_id = Sensor.create(
            room_id=int(data['room_id']),
            sensor_type=data['sensor_type'],
            location=data.get('location')
        )
        return jsonify({'success': True, 'sensor_id': sensor_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/measurements', methods=['POST'])
def add_measurement():
    """API: Добавление нового измерения"""
    data = request.get_json()
    try:
        measurement_id = DataCollectionService.collect_measurement(
            sensor_id=int(data['sensor_id']),
            value=float(data['value'])
        )
        return jsonify({'success': True, 'measurement_id': measurement_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/measurements/history/<int:sensor_id>')
def measurement_history(sensor_id):
    """API: Получение истории измерений"""
    hours = request.args.get('hours', 24, type=int)
    measurements = Measurement.get_history(sensor_id, hours)
    
    return jsonify([{
        'value': float(m['value']),
        'measured_at': m['measured_at'].isoformat()
    } for m in measurements])

@app.route('/equipment')
def equipment():
    """Страница управления оборудованием"""
    equipment_list = Equipment.get_all()
    rooms = Room.get_all()
    return render_template('equipment.html', 
                         equipment=equipment_list,
                         rooms=rooms)

@app.route('/api/equipment', methods=['POST'])
def create_equipment():
    """API: Создание нового оборудования"""
    data = request.get_json()
    try:
        equipment_id = Equipment.create(
            room_id=int(data['room_id']),
            equipment_type=data['equipment_type'],
            name=data['name'],
            power=float(data['power']) if data.get('power') else None
        )
        return jsonify({'success': True, 'equipment_id': equipment_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/equipment/<int:equipment_id>/status', methods=['PUT'])
def update_equipment_status(equipment_id):
    """API: Обновление статуса оборудования"""
    data = request.get_json()
    try:
        Equipment.update_status(
            equipment_id=equipment_id,
            status=data['status'],
            auto_mode=data.get('auto_mode')
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/decisions/<int:room_id>', methods=['POST'])
def make_decision(room_id):
    """API: Принятие решения по управлению оборудованием"""
    try:
        decision = DecisionMakingService.make_decision(room_id)
        
        # Опционально: автоматическое выполнение решения
        if request.args.get('execute') == 'true':
            executed = DecisionMakingService.execute_decision(decision)
            decision['executed_actions'] = executed
        
        return jsonify({'success': True, 'decision': decision})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/equipment/evaluate', methods=['POST'])
def evaluate_equipment_config():
    """API: Оценка конфигурации оборудования"""
    data = request.get_json()
    try:
        evaluation = DecisionMakingService.evaluate_equipment_configuration(
            room_id=int(data['room_id']),
            equipment_params=data['equipment']
        )
        return jsonify({'success': True, 'evaluation': evaluation})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/reports')
def reports():
    """Страница отчетов"""
    rooms = Room.get_all()
    
    reports_data = []
    for room in rooms:
        analysis = AnalysisService.analyze_room_air_quality(room['id'])
        efficiency = AnalysisService.evaluate_equipment_efficiency(room['id'])
        
        reports_data.append({
            'room': room,
            'analysis': analysis,
            'efficiency': efficiency
        })
    
    return render_template('reports.html', reports=reports_data)

@app.template_filter('status_class')
def status_class_filter(status):
    """Фильтр для определения CSS класса по статусу"""
    status_map = {
        'optimal': 'success',
        'acceptable': 'info',
        'low': 'warning',
        'high': 'warning',
        'critical_low': 'danger',
        'critical_high': 'danger',
        'critical': 'danger',
        'no_data': 'secondary'
    }
    return status_map.get(status, 'secondary')

@app.template_filter('format_datetime')
def format_datetime_filter(dt):
    """Фильтр для форматирования даты и времени"""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime('%d.%m.%Y %H:%M:%S')

if __name__ == '__main__':
    # Инициализация базы данных
    try:
        db.init_db()
        print("База данных инициализирована успешно")
    except Exception as e:
        print(f"Ошибка инициализации БД: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
