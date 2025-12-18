from config import Config
from services.data_collection import DataCollectionService

class AnalysisService:
    """Сервис анализа качества воздуха"""
    
    @staticmethod
    def evaluate_parameter(param_type, value):
        """Оценка отдельного параметра микроклимата"""
        standards = Config.AIR_QUALITY_STANDARDS.get(param_type)
        if not standards:
            return {'status': 'unknown', 'message': 'Неизвестный параметр'}
        
        if param_type in ['temperature', 'humidity']:
            if value < standards['min']:
                return {'status': 'critical_low', 'message': f'Критически низкий уровень'}
            elif value < standards['optimal_min']:
                return {'status': 'low', 'message': f'Ниже оптимального уровня'}
            elif value <= standards['optimal_max']:
                return {'status': 'optimal', 'message': 'Оптимальный уровень'}
            elif value <= standards['max']:
                return {'status': 'high', 'message': 'Выше оптимального уровня'}
            else:
                return {'status': 'critical_high', 'message': 'Критически высокий уровень'}
        
        elif param_type in ['co2', 'dust']:
            if value <= standards['optimal']:
                return {'status': 'optimal', 'message': 'Оптимальный уровень'}
            elif value <= standards['acceptable']:
                return {'status': 'acceptable', 'message': 'Допустимый уровень'}
            elif value <= standards['max']:
                return {'status': 'high', 'message': 'Повышенный уровень'}
            else:
                return {'status': 'critical', 'message': 'Критический уровень'}
        
        return {'status': 'unknown', 'message': 'Ошибка оценки'}
    
    @staticmethod
    def analyze_room_air_quality(room_id):
        """Комплексный анализ качества воздуха в помещении"""
        state = DataCollectionService.get_room_current_state(room_id)
        
        analysis = {
            'room_id': room_id,
            'parameters': {},
            'overall_status': 'optimal',
            'issues': []
        }
        
        status_priority = {
            'optimal': 0,
            'acceptable': 1,
            'low': 2,
            'high': 2,
            'critical_low': 3,
            'critical_high': 3,
            'critical': 3
        }
        
        for param_type, data in state.items():
            if data is None:
                analysis['parameters'][param_type] = {
                    'status': 'no_data',
                    'message': 'Нет данных'
                }
                analysis['issues'].append(f'Отсутствуют данные по {param_type}')
                continue
            
            evaluation = AnalysisService.evaluate_parameter(param_type, data['value'])
            analysis['parameters'][param_type] = {
                'value': data['value'],
                'status': evaluation['status'],
                'message': evaluation['message'],
                'measured_at': data['measured_at']
            }
            
            # Определение общего статуса (наихудший из всех параметров)
            current_priority = status_priority.get(evaluation['status'], 0)
            overall_priority = status_priority.get(analysis['overall_status'], 0)
            
            if current_priority > overall_priority:
                analysis['overall_status'] = evaluation['status']
            
            if evaluation['status'] not in ['optimal', 'acceptable']:
                analysis['issues'].append(
                    f"{param_type.upper()}: {evaluation['message']}"
                )
        
        return analysis
    
    @staticmethod
    def evaluate_equipment_efficiency(room_id):
        """Оценка эффективности работы оборудования"""
        from models.equipment import Equipment
        
        equipment_list = Equipment.get_by_room(room_id)
        analysis = AnalysisService.analyze_room_air_quality(room_id)
        
        efficiency = {
            'total_equipment': len(equipment_list),
            'active_equipment': sum(1 for e in equipment_list if e['status'] == 'on'),
            'recommendations': []
        }
        
        # Анализ необходимости включения/выключения оборудования
        for equipment in equipment_list:
            eq_type = equipment['equipment_type']
            eq_status = equipment['status']
            
            # Проверка соответствия работы оборудования текущим условиям
            if eq_type == 'heating':
                temp_status = analysis['parameters'].get('temperature', {}).get('status')
                if temp_status in ['critical_low', 'low'] and eq_status == 'off':
                    efficiency['recommendations'].append(
                        f"Рекомендуется включить {equipment['name']}"
                    )
                elif temp_status in ['critical_high', 'high'] and eq_status == 'on':
                    efficiency['recommendations'].append(
                        f"Рекомендуется выключить {equipment['name']}"
                    )
            
            elif eq_type == 'air_conditioner':
                temp_status = analysis['parameters'].get('temperature', {}).get('status')
                if temp_status in ['critical_high', 'high'] and eq_status == 'off':
                    efficiency['recommendations'].append(
                        f"Рекомендуется включить {equipment['name']}"
                    )
            
            elif eq_type == 'humidifier':
                humidity_status = analysis['parameters'].get('humidity', {}).get('status')
                if humidity_status in ['critical_low', 'low'] and eq_status == 'off':
                    efficiency['recommendations'].append(
                        f"Рекомендуется включить {equipment['name']}"
                    )
            
            elif eq_type == 'ventilation':
                co2_status = analysis['parameters'].get('co2', {}).get('status')
                dust_status = analysis['parameters'].get('dust', {}).get('status')
                if (co2_status in ['high', 'critical'] or dust_status in ['high', 'critical']) and eq_status == 'off':
                    efficiency['recommendations'].append(
                        f"Рекомендуется включить {equipment['name']}"
                    )
        
        return efficiency
