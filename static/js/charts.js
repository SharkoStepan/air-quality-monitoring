/**
 * Утилиты для работы с графиками
 */

// Цветовая схема для графиков
const CHART_COLORS = {
    temperature: 'rgb(255, 99, 132)',
    humidity: 'rgb(54, 162, 235)',
    co2: 'rgb(255, 205, 86)',
    dust: 'rgb(153, 102, 255)'
};

// Конфигурация по умолчанию для Chart.js
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.color = '#666';

/**
 * Создание графика истории измерений
 * @param {string} canvasId - ID элемента canvas
 * @param {Array} data - Массив данных измерений
 * @param {string} sensorType - Тип датчика
 */
function createMeasurementChart(canvasId, data, sensorType) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = data.map(item => {
        const date = new Date(item.measured_at);
        return date.toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'});
    });

    const values = data.map(item => item.value);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: getSensorLabel(sensorType),
                data: values,
                borderColor: CHART_COLORS[sensorType] || 'rgb(75, 192, 192)',
                backgroundColor: (CHART_COLORS[sensorType] || 'rgb(75, 192, 192)').replace('rgb', 'rgba').replace(')', ', 0.2)'),
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return value + ' ' + getSensorUnit(sensorType);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Получение метки для типа датчика
 * @param {string} sensorType - Тип датчика
 * @returns {string} Человекочитаемая метка
 */
function getSensorLabel(sensorType) {
    const labels = {
        'temperature': 'Температура',
        'humidity': 'Влажность',
        'co2': 'Уровень CO₂',
        'dust': 'Уровень пыли'
    };
    return labels[sensorType] || sensorType;
}

/**
 * Получение единицы измерения для типа датчика
 * @param {string} sensorType - Тип датчика
 * @returns {string} Единица измерения
 */
function getSensorUnit(sensorType) {
    const units = {
        'temperature': '°C',
        'humidity': '%',
        'co2': 'ppm',
        'dust': 'мг/м³'
    };
    return units[sensorType] || '';
}

/**
 * Создание сравнительного графика для нескольких помещений
 * @param {string} canvasId - ID элемента canvas
 * @param {Object} roomsData - Данные по помещениям
 */
function createComparisonChart(canvasId, roomsData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const roomNames = Object.keys(roomsData);
    const datasets = [];

    const sensorTypes = ['temperature', 'humidity', 'co2', 'dust'];
    
    sensorTypes.forEach(type => {
        datasets.push({
            label: getSensorLabel(type),
            data: roomNames.map(room => roomsData[room][type] || 0),
            backgroundColor: CHART_COLORS[type] || 'rgb(75, 192, 192)'
        });
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: roomNames,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Загрузка и отображение истории измерений
 * @param {number} sensorId - ID датчика
 * @param {string} sensorType - Тип датчика
 * @param {string} canvasId - ID элемента canvas
 * @param {number} hours - Количество часов для истории
 */
function loadMeasurementHistory(sensorId, sensorType, canvasId, hours = 24) {
    fetch(`/api/measurements/history/${sensorId}?hours=${hours}`)
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                createMeasurementChart(canvasId, data, sensorType);
            } else {
                const container = document.getElementById(canvasId).parentElement;
                container.innerHTML = '<p class="text-muted text-center">Нет данных за указанный период</p>';
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки истории измерений:', error);
        });
}

/**
 * Обновление графика в реальном времени
 * @param {Chart} chart - Экземпляр Chart.js
 * @param {Object} newData - Новые данные для добавления
 */
function updateChartRealtime(chart, newData) {
    if (!chart || !newData) return;

    chart.data.labels.push(newData.label);
    chart.data.datasets[0].data.push(newData.value);

    // Ограничиваем количество точек на графике
    const maxPoints = 50;
    if (chart.data.labels.length > maxPoints) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }

    chart.update();
}

/**
 * Создание кругового графика для показателей качества воздуха
 * @param {string} canvasId - ID элемента canvas
 * @param {Object} parameters - Параметры качества воздуха
 */
function createQualityPieChart(canvasId, parameters) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const statusCounts = {
        'optimal': 0,
        'acceptable': 0,
        'warning': 0,
        'critical': 0
    };

    Object.values(parameters).forEach(param => {
        if (param.status === 'optimal') statusCounts.optimal++;
        else if (param.status === 'acceptable') statusCounts.acceptable++;
        else if (['low', 'high'].includes(param.status)) statusCounts.warning++;
        else statusCounts.critical++;
    });

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Оптимально', 'Допустимо', 'Предупреждение', 'Критично'],
            datasets: [{
                data: [statusCounts.optimal, statusCounts.acceptable, statusCounts.warning, statusCounts.critical],
                backgroundColor: [
                    'rgb(25, 135, 84)',
                    'rgb(13, 202, 240)',
                    'rgb(255, 193, 7)',
                    'rgb(220, 53, 69)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}
