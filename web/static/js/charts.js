/**
 * Chart.js visualization helpers for QLib Web
 */

/**
 * Chart instances registry
 */
const charts = {};

/**
 * Create line chart
 */
function createLineChart(canvasId, labels, datasets, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    // Destroy existing chart
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                mode: 'index',
                intersect: false,
            }
        },
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: '时间'
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: '值'
                }
            }
        }
    };

    charts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: { ...defaultOptions, ...options }
    });

    return charts[canvasId];
}

/**
 * Create bar chart
 */
function createBarChart(canvasId, labels, datasets, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                position: 'top',
            }
        }
    };

    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: { ...defaultOptions, ...options }
    });

    return charts[canvasId];
}

/**
 * Create histogram chart
 */
function createHistogramChart(canvasId, data, options = {}) {
    // Create histogram bins
    const min = Math.min(...data);
    const max = Math.max(...data);
    const binCount = 30;
    const binSize = (max - min) / binCount;

    const bins = new Array(binCount).fill(0);
    data.forEach(value => {
        const binIndex = Math.min(Math.floor((value - min) / binSize), binCount - 1);
        bins[binIndex]++;
    });

    const labels = bins.map((_, i) => (min + i * binSize).toFixed(2));

    return createBarChart(canvasId, labels, [{
        label: '频数',
        data: bins,
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
    }], {
        ...options,
        plugins: {
            ...options.plugins,
            title: {
                display: true,
                text: `均值: ${(data.reduce((a, b) => a + b) / data.length).toFixed(4)}, ` +
                      `标准差: ${Math.sqrt(data.reduce((a, b) => a + (b - data.reduce((c, d) => c + d) / data.length) ** 2, 0) / data.length).toFixed(4)}`
            }
        }
    });
}

/**
 * Create pie chart
 */
function createPieChart(canvasId, labels, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    const colors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(201, 203, 207, 0.8)'
    ];

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                position: 'right',
            }
        }
    };

    charts[canvasId] = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 1
            }]
        },
        options: { ...defaultOptions, ...options }
    });

    return charts[canvasId];
}

/**
 * Create horizontal bar chart
 */
function createHorizontalBarChart(canvasId, labels, datasets, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: true,
        indexAxis: 'y',
        plugins: {
            legend: {
                display: false
            }
        }
    };

    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: { ...defaultOptions, ...options }
    });

    return charts[canvasId];
}

/**
 * Create portfolio comparison chart
 */
function createPortfolioChart(canvasId, dates, portfolioValues, benchmarkValues = null) {
    const datasets = [{
        label: '策略净值',
        data: portfolioValues,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        fill: true,
        tension: 0.1
    }];

    if (benchmarkValues) {
        datasets.push({
            label: '基准',
            data: benchmarkValues,
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.1)',
            fill: true,
            tension: 0.1
        });
    }

    return createLineChart(canvasId, dates, datasets, {
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: '日期'
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: '净值'
                },
                beginAtZero: false
            }
        }
    });
}

/**
 * Create drawdown chart
 */
function createDrawdownChart(canvasId, dates, drawdownValues) {
    return createLineChart(canvasId, dates, [{
        label: '回撤',
        data: drawdownValues,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.3)',
        fill: true,
        tension: 0.1
    }], {
        scales: {
            y: {
                display: true,
                title: {
                    display: true,
                    text: '回撤 (%)'
                },
                min: Math.min(...drawdownValues) - 0.05
            }
        }
    });
}

/**
 * Create feature importance chart
 */
function createFeatureImportanceChart(canvasId, featureNames, importanceValues) {
    // Sort features by importance
    const features = featureNames.map((name, i) => ({
        name: name,
        importance: importanceValues[i]
    })).sort((a, b) => b.importance - a.importance).slice(0, 20);

    const labels = features.map(f => f.name);
    const values = features.map(f => f.importance);

    return createHorizontalBarChart(canvasId, labels, [{
        data: values,
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
    }]);
}

/**
 * Create training loss chart
 */
function createTrainingLossChart(canvasId, epochs, trainLoss, validLoss = null) {
    const datasets = [{
        label: '训练损失',
        data: trainLoss,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        fill: false,
        tension: 0.1
    }];

    if (validLoss) {
        datasets.push({
            label: '验证损失',
            data: validLoss,
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.1)',
            fill: false,
            tension: 0.1
        });
    }

    return createLineChart(canvasId, epochs, datasets, {
        scales: {
            x: {
                display: true,
                title: {
                    display: true,
                    text: 'Epoch'
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: '损失'
                }
            }
        }
    });
}

/**
 * Destroy chart
 */
function destroyChart(canvasId) {
    if (charts[canvasId]) {
        charts[canvasId].destroy();
        delete charts[canvasId];
    }
}

/**
 * Destroy all charts
 */
function destroyAllCharts() {
    Object.keys(charts).forEach(canvasId => {
        destroyChart(canvasId);
    });
}

/**
 * Initialize factor test charts with demo data
 */
function initFactorTestCharts() {
    showEmptyChartState('ic-chart', '等待因子分析数据...');
    showEmptyChartState('ic-dist-chart', '等待因子分析数据...');
    showEmptyChartState('group-return-chart', '等待因子分析数据...');
}

/**
 * Initialize training charts with demo data
 */
function initTrainingCharts() {
    // 显示空状态而非演示数据
    showEmptyChartState('train-loss-chart', '等待训练数据...');
    showEmptyChartState('valid-metrics-chart', '等待训练数据...');
    showEmptyChartState('feature-importance-chart', '等待训练数据...');
}

/**
 * Show empty chart state with message
 */
function showEmptyChartState(canvasId, message) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    // Destroy existing chart
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    charts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: message,
                    font: {
                        size: 16,
                        style: 'italic'
                    },
                    color: '#6c757d'
                }
            },
            scales: {
                x: {
                    display: false
                },
                y: {
                    display: false
                }
            }
        }
    });
}

/**
 * Initialize backtest charts with demo data
 */
function initBacktestCharts() {
    const dates = ['2017-01', '2017-02', '2017-03', '2017-04', '2017-05', '2017-06', '2017-07', '2017-08', '2017-09', '2017-10', '2017-11', '2017-12'];
    const portfolio = [1.0, 1.05, 1.12, 1.08, 1.15, 1.2, 1.25, 1.22, 1.28, 1.3, 1.35, 1.4];
    const benchmark = [1.0, 1.02, 1.04, 1.01, 1.05, 1.08, 1.1, 1.07, 1.12, 1.14, 1.16, 1.18];

    // Portfolio chart
    createPortfolioChart('portfolio-chart', dates, portfolio, benchmark);

    // Drawdown chart
    const drawdown = [0, -0.02, 0, -0.04, 0, 0, 0, -0.03, 0, 0, 0, 0];
    createDrawdownChart('drawdown-chart', dates, drawdown);
}
