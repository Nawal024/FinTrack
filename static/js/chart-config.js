/**
 * Chart configuration for Personal Expense Tracker
 */

/**
 * Create a pie chart showing expense distribution by category
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} data - Category totals object (category: amount)
 */
function createCategoryPieChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Extract labels and values from data
    const labels = Object.keys(data);
    const values = Object.values(data);
    
    // Define colors for each category
    const colors = [
        '#4ead96', // Primary - Light green
        '#e6a23c', // Warning - Amber
        '#e15554', // Danger - Red
        '#67c23a', // Success - Green
        '#909399', // Info - Gray
        '#c84869', // Accent - Pink
        '#2c363f', // Dark - Dark gray
        '#f7f2e4'  // Secondary - Cream
    ];
    
    // Create the chart
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, values.length),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                position: 'right',
                rtl: true,
                labels: {
                    fontFamily: 'Cairo, sans-serif'
                }
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem, data) {
                        const value = data.datasets[0].data[tooltipItem.index];
                        const label = data.labels[tooltipItem.index];
                        return `${label}: ${value}`;
                    }
                }
            }
        }
    });
}

/**
 * Create a bar chart showing monthly expense totals
 * @param {string} canvasId - ID of the canvas element
 * @param {Array} labels - Array of month labels
 * @param {Array} values - Array of expense values
 */
function createMonthlyExpensesChart(canvasId, labels, values) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Create the chart
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'إجمالي المصاريف الشهرية',
                data: values,
                backgroundColor: '#4ead96',
                borderColor: '#3c9b85',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        fontFamily: 'Cairo, sans-serif'
                    }
                }],
                xAxes: [{
                    ticks: {
                        fontFamily: 'Cairo, sans-serif'
                    }
                }]
            },
            legend: {
                labels: {
                    fontFamily: 'Cairo, sans-serif'
                }
            }
        }
    });
}

/**
 * Create a line chart showing spending trend over time
 * @param {string} canvasId - ID of the canvas element
 * @param {Array} labels - Array of date labels
 * @param {Array} values - Array of expense values
 */
function createSpendingTrendChart(canvasId, labels, values) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Create the chart
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'نمط الإنفاق',
                data: values,
                backgroundColor: 'rgba(78, 173, 150, 0.2)',
                borderColor: '#4ead96',
                borderWidth: 2,
                pointBackgroundColor: '#4ead96',
                pointBorderColor: '#fff',
                pointRadius: 4,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        fontFamily: 'Cairo, sans-serif'
                    }
                }],
                xAxes: [{
                    ticks: {
                        fontFamily: 'Cairo, sans-serif'
                    }
                }]
            },
            legend: {
                labels: {
                    fontFamily: 'Cairo, sans-serif'
                }
            }
        }
    });
}

/**
 * Create a horizontal bar chart showing budget vs. spending by category
 * @param {string} canvasId - ID of the canvas element
 * @param {Array} categories - Array of category names
 * @param {Array} budgets - Array of budget values
 * @param {Array} actuals - Array of actual spending values
 */
function createBudgetComparisonChart(canvasId, categories, budgets, actuals) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Create the chart
    new Chart(ctx, {
        type: 'horizontalBar',
        data: {
            labels: categories,
            datasets: [
                {
                    label: 'الميزانية',
                    data: budgets,
                    backgroundColor: 'rgba(103, 194, 58, 0.6)',
                    borderColor: '#67c23a',
                    borderWidth: 1
                },
                {
                    label: 'الإنفاق الفعلي',
                    data: actuals,
                    backgroundColor: 'rgba(230, 162, 60, 0.6)',
                    borderColor: '#e6a23c',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                xAxes: [{
                    ticks: {
                        beginAtZero: true,
                        fontFamily: 'Cairo, sans-serif'
                    }
                }],
                yAxes: [{
                    ticks: {
                        fontFamily: 'Cairo, sans-serif'
                    }
                }]
            },
            legend: {
                labels: {
                    fontFamily: 'Cairo, sans-serif'
                }
            }
        }
    });
}
