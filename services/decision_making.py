from services.analysis import AnalysisService
from models.equipment import Equipment
from database.db import db
import json

class DecisionMakingService:
    """Сервис принятия решений по управлению оборудованием"""
    
    @staticmethod
    def make_decision(room_id):
        """Принятие решения на основе анализа качества воздуха"""
        analysis = AnalysisService.analyze_room_air_quality(room_id)
        equipment_list = Equipment.get_by_room(room_id)
        
        decision = {
            'room_id': room_id,
            'overall_status': analysis['overall_status'],
            'actions': [],
            'recommendations': []
        }
        
        # Решения по температуре
        temp_data = analysis['parameters'].get('temperature', {})
        temp_status = temp_data.get('status')
        
        if temp_status in ['critical_low', 'low']:
            for eq in equipment_list:
                if eq['equipment_type'] == 'heating' and eq['auto_mode']:
                    decision['actions'].append({
                        'equipment_id': eq['id'],
                        'equipment_name': eq['name'],
                        'action': 'turn_on',
                        'reason': f"Низкая температура: {temp_data.get('value', 'N/A')}°C"
                    })
        elif temp_status in ['critical_high', 'high']:
            for eq in equipment_list:
                if eq['equipment_type'] == 'air_conditioner' and eq['auto_mode']:
                    decision['actions'].append({
                        'equipment_id': eq['id'],
                        'equipment_name': eq['name'],
                        'action': 'turn_on',
                        'reason': f"Высокая температура: {temp_data.get('value', 'N/A')}°C"
                    })
                elif eq['equipment_type'] == 'heating' and eq['status'] == 'on' and eq['auto_mode']:
                    decision['actions'].append({
                        'equipment_id': eq['id'],
                        'equipment_name': eq['name'],
                        'action': 'turn_off',
                        'reason': f"Высокая температура: {temp_data.get('value', 'N/A')}°C"
                    })
        
        # Решения по влажности
        humidity_data = analysis['parameters'].get('humidity', {})
        humidity_status = humidity_data.get('status')
        
        if humidity_status in ['critical_low', 'low']:
            for eq in equipment_list:
                if eq['equipment_type'] == 'humidifier' and eq['auto_mode']:
                    decision['actions'].append({
                        'equipment_id': eq['id'],
                        'equipment_name': eq['name'],
                        'action': 'turn_on',
                        'reason': f"Низкая влажность: {humidity_data.get('value', 'N/A')}%"
                    })
        
        # Решения по CO2 и пыли
        co2_data = analysis['parameters'].get('co2', {})
        dust_data = analysis['parameters'].get('dust', {})
        
        if co2_data.get('status') in ['high', 'critical'] or dust_data.get('status') in ['high', 'critical']:
            for eq in equipment_list:
                if eq['equipment_type'] == 'ventilation' and eq['auto_mode']:
                    reasons = []
                    if co2_data.get('status') in ['high', 'critical']:
                        reasons.append(f"CO2: {co2_data.get('value', 'N/A')} ppm")
                    if dust_data.get('status') in ['high', 'critical']:
                        reasons.append(f"Пыль: {dust_data.get('value', 'N/A')} мг/м³")
                    
                    decision['actions'].append({
                        'equipment_id': eq['id'],
                        'equipment_name': eq['name'],
                        'action': 'turn_on',
                        'reason': ', '.join(reasons)
                    })
        
        # Общие рекомендации
        if analysis['overall_status'] == 'optimal':
            decision['recommendations'].append("Качество воздуха в норме")
        else:
            decision['recommendations'].extend(analysis['issues'])
        
        return decision
    
    @staticmethod
    def execute_decision(decision):
        """Выполнение принятого решения (управление оборудованием)"""
        executed_actions = []
        
        for action in decision['actions']:
            equipment_id = action['equipment_id']
            new_status = 'on' if action['action'] == 'turn_on' else 'off'
            
            try:
                Equipment.update_status(equipment_id, new_status)
                executed_actions.append({
                    'equipment_id': equipment_id,
                    'equipment_name': action['equipment_name'],
                    'status': new_status,
                    'success': True
                })
            except Exception as e:
                executed_actions.append({
                    'equipment_id': equipment_id,
                    'equipment_name': action['equipment_name'],
                    'success': False,
                    'error': str(e)
                })
        
        return executed_actions
    
    @staticmethod
    def save_decision(room_id, decision_type, description, actions):
        """Сохранение решения в базу данных"""
        with db.get_cursor() as cursor:
            cursor.execute(
                """INSERT INTO decisions (room_id, decision_type, description, recommended_actions)
                   VALUES (%s, %s, %s, %s) RETURNING id""",
                (room_id, decision_type, description, json.dumps(actions))
            )
            return cursor.fetchone()['id']
    
    @staticmethod
    def evaluate_equipment_configuration(room_id, equipment_params):
        """Оценка конфигурации оборудования (для проектировщика)"""
        recommendations = []
        
        # Проверка наличия необходимого оборудования
        equipment_types = {eq['type'] for eq in equipment_params}
        
        if 'heating' not in equipment_types and 'air_conditioner' not in equipment_types:
            recommendations.append({
                'type': 'warning',
                'message': 'Отсутствует оборудование для регулирования температуры'
            })
        
        if 'ventilation' not in equipment_types:
            recommendations.append({
                'type': 'warning',
                'message': 'Отсутствует вентиляционное оборудование'
            })
        
        if 'humidifier' not in equipment_types:
            recommendations.append({
                'type': 'info',
                'message': 'Рекомендуется добавить увлажнитель воздуха'
            })
        
        # Проверка мощности оборудования
        for eq in equipment_params:
            if eq.get('power') and eq['power'] < 100:
                recommendations.append({
                    'type': 'warning',
                    'message': f"Низкая мощность оборудования {eq['name']}: {eq['power']}W"
                })
        
        result = {
            'is_valid': len([r for r in recommendations if r['type'] == 'warning']) == 0,
            'recommendations': recommendations
        }
        
        return result
