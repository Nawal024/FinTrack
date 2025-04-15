/**
 * Main JavaScript for Personal Expense Tracker
 */

// Custom plugin for HTML legend in Chart.js
Chart.plugins.register({
    id: 'customCategoryIcons',
    afterRender: function(chart) {
        // Only for pie charts and only once
        if (chart.config.type === 'pie' && !chart.customLegendRendered) {
            // Get the dedicated legend container
            const legendContainer = document.getElementById('chart-custom-legend');
            if (!legendContainer) return;
            
            // Clear existing content
            legendContainer.innerHTML = '';
            
            // Get category mappings
            const categoryNamesElement = document.getElementById('category-names-data');
            if (!categoryNamesElement) return;
            
            try {
                const categoryNames = JSON.parse(categoryNamesElement.value);
                const datasets = chart.data.datasets[0];
                const labels = chart.data.labels;
                const colors = datasets.backgroundColor;
                
                // Create legend items
                for (let i = 0; i < labels.length; i++) {
                    const category = labels[i];
                    const color = Array.isArray(colors) ? colors[i] : colors;
                    const categoryNameEn = categoryNames[category] || '';
                    const value = datasets.data[i];
                    
                    // Get icon for category
                    let iconClass = 'fas fa-question-circle'; // Default
                    
                    if (categoryNameEn === 'Food') {
                        iconClass = 'fas fa-utensils';
                    } else if (categoryNameEn === 'Transport') {
                        iconClass = 'fas fa-car';
                    } else if (categoryNameEn === 'Shopping') {
                        iconClass = 'fas fa-shopping-bag';
                    } else if (categoryNameEn === 'Bills') {
                        iconClass = 'fas fa-file-invoice-dollar';
                    } else if (categoryNameEn === 'Entertainment') {
                        iconClass = 'fas fa-film';
                    } else if (categoryNameEn === 'Health') {
                        iconClass = 'fas fa-heartbeat';
                    } else if (categoryNameEn === 'Education') {
                        iconClass = 'fas fa-graduation-cap';
                    } else if (categoryNameEn === 'Other') {
                        iconClass = 'fas fa-ellipsis-h';
                    }
                    
                    // Create legend item
                    const legendItem = document.createElement('div');
                    legendItem.className = 'chart-legend-item';
                    legendItem.style.display = 'flex';
                    legendItem.style.alignItems = 'center';
                    legendItem.style.padding = '8px 5px';
                    legendItem.style.fontSize = '14px';
                    legendItem.style.borderRadius = '4px';
                    legendItem.style.marginBottom = '8px';
                    legendItem.style.cursor = 'pointer';
                    
                    // Add hover effect
                    legendItem.addEventListener('mouseover', function() {
                        this.style.backgroundColor = 'rgba(0,0,0,0.05)';
                    });
                    legendItem.addEventListener('mouseout', function() {
                        this.style.backgroundColor = 'transparent';
                    });
                    
                    // Add color box
                    const colorBox = document.createElement('span');
                    colorBox.style.backgroundColor = color;
                    colorBox.style.width = '14px';
                    colorBox.style.height = '14px';
                    colorBox.style.display = 'inline-block';
                    colorBox.style.marginLeft = '8px';
                    colorBox.style.borderRadius = '2px';
                    
                    // Add icon
                    const icon = document.createElement('i');
                    icon.className = iconClass;
                    icon.style.marginLeft = '8px';
                    icon.style.marginRight = '5px';
                    icon.style.color = '#333';
                    icon.style.width = '20px';
                    icon.style.textAlign = 'center';
                    
                    // Add category and value
                    const labelContainer = document.createElement('div');
                    labelContainer.style.display = 'flex';
                    labelContainer.style.flexDirection = 'column';
                    labelContainer.style.flexGrow = '1';
                    
                    const categoryLabel = document.createElement('span');
                    categoryLabel.textContent = category;
                    categoryLabel.style.fontWeight = 'bold';
                    
                    const valueLabel = document.createElement('span');
                    valueLabel.textContent = `${parseFloat(value).toFixed(2)} ريال`;
                    valueLabel.style.fontSize = '12px';
                    valueLabel.style.color = '#666';
                    
                    labelContainer.appendChild(categoryLabel);
                    labelContainer.appendChild(valueLabel);
                    
                    // Assemble
                    legendItem.appendChild(colorBox);
                    legendItem.appendChild(icon);
                    legendItem.appendChild(labelContainer);
                    legendContainer.appendChild(legendItem);
                    
                    // Add click event to highlight corresponding segment
                    legendItem.addEventListener('click', function() {
                        const index = i;
                        const meta = chart.getDatasetMeta(0);
                        const activeSegment = meta.data[index];
                        
                        // Toggle active state
                        const alreadyActive = activeSegment._model.outerRadius > meta.outerRadius;
                        
                        // Reset all segments
                        meta.data.forEach(function(segment, i) {
                            segment._model.outerRadius = meta.outerRadius;
                        });
                        
                        // Highlight selected segment if not already active
                        if (!alreadyActive) {
                            activeSegment._model.outerRadius = meta.outerRadius * 1.1;
                        }
                        
                        chart.update();
                    });
                }
                
                chart.customLegendRendered = true;
            } catch (error) {
                console.error('Error creating custom legend:', error);
            }
        }
    }
});

// Auto-dismiss flash messages
function setupFlashMessages() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // تحقق مما إذا كانت التنبيه هو تنبيه الإنفاق (مثلاً عبر إضافة فئة مخصصة)
        if (alert.classList.contains('spending-alert')) {
            // لا تختفي تلقائيًا (أو قم بتطبيق أي شيء آخر)
            return;
        }

        // الاختفاء التلقائي لبقية التنبيهات
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}


// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize date pickers
    initializeDatePickers();
    // Setup flash message auto-dismiss
    setupFlashMessages();
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize any charts on the page
    initializeCharts();
    
    // Fix dropdown width issues and mobile layout
    fixSelectWidthIssues();
    
    // Create notification container if it doesn't exist
    if (!document.getElementById('notification-container')) {
        const notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        document.body.appendChild(notificationContainer);
    }
});

/**
 * Initialize date picker inputs
 */
function initializeDatePickers() {
    // Find all date inputs and set them to current date by default if empty
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = today;
        }
    });
}

/**
 * Setup all event listeners for the application
 */
function setupEventListeners() {
    // Add Expense Form Submission
    const addExpenseForm = document.getElementById('add-expense-form');
    if (addExpenseForm) {
        addExpenseForm.addEventListener('submit', handleAddExpense);
    }
    
    // Edit Expense Buttons
    const editButtons = document.querySelectorAll('.edit-expense-btn');
    editButtons.forEach(button => {
        button.addEventListener('click', handleEditExpenseClick);
    });
    
    // Delete Expense Buttons
    const deleteButtons = document.querySelectorAll('.delete-expense-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', handleDeleteExpense);
    });
    
    // Category Budget Edit Form
    const categoryBudgetForms = document.querySelectorAll('.category-budget-form');
    categoryBudgetForms.forEach(form => {
        form.addEventListener('submit', handleUpdateCategoryBudget);
    });
}

/**
 * Handle adding a new expense
 * @param {Event} event - Form submission event
 */
function handleAddExpense(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Send AJAX request to add expense
    fetch('/api/expenses', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            showAlert('تمت إضافة المصروف بنجاح', 'success');
            
            // Reset form
            form.reset();
            
            // Set date to today
            const dateInput = form.querySelector('input[type="date"]');
            if (dateInput) {
                dateInput.value = new Date().toISOString().split('T')[0];
            }
            
            // Reload page after short delay to reflect the changes
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            // Show error message
            showAlert('خطأ: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('حدث خطأ أثناء إضافة المصروف', 'danger');
    });
}

/**
 * Handle click on edit expense button
 * @param {Event} event - Click event
 */
function handleEditExpenseClick(event) {
    const button = event.currentTarget;
    const expenseId = button.getAttribute('data-id');
    const expenseRow = button.closest('tr');
    
    // Get expense data from the row
    const category = expenseRow.querySelector('.expense-category').textContent.trim();
    const amount = parseFloat(expenseRow.querySelector('.expense-amount').textContent.replace(/[^\d.-]/g, ''));
    const date = expenseRow.querySelector('.expense-date').getAttribute('data-date');
    const description = expenseRow.querySelector('.expense-description').textContent.trim();
    
    // Populate modal with expense data
    const modal = document.getElementById('editExpenseModal');
    if (modal) {
        modal.querySelector('#edit-expense-id').value = expenseId;
        modal.querySelector('#edit-expense-category').value = category;
        modal.querySelector('#edit-expense-amount').value = amount;
        modal.querySelector('#edit-expense-date').value = date;
        modal.querySelector('#edit-expense-description').value = description;
        
        // Show the modal using Bootstrap JavaScript
        new bootstrap.Modal(modal).show();
    }
}

/**
 * Handle updating an expense
 * @param {Event} event - Form submission event
 */
function handleUpdateExpense(event) {
    event.preventDefault();
    
    const form = event.target;
    const expenseId = form.querySelector('#edit-expense-id').value;
    
    // Get form data
    const category = form.querySelector('#edit-expense-category').value;
    const amount = form.querySelector('#edit-expense-amount').value;
    const date = form.querySelector('#edit-expense-date').value;
    const description = form.querySelector('#edit-expense-description').value;
    
    // Create data object
    const data = {
        category: category,
        amount: amount,
        date: date,
        description: description
    };
    
    // Send AJAX request to update expense
    fetch(`/api/expenses/${expenseId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            showAlert('تم تحديث المصروف بنجاح', 'success');
            
            // Hide modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editExpenseModal'));
            if (modal) {
                modal.hide();
            }
            
            // Reload page after short delay to reflect the changes
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            // Show error message
            showAlert('خطأ: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('حدث خطأ أثناء تحديث المصروف', 'danger');
    });
}

/**
 * Handle deleting an expense
 * @param {Event} event - Click event
 */
function handleDeleteExpense(event) {
    if (!confirm('هل أنت متأكد من حذف هذا المصروف؟')) {
        return;
    }
    
    const button = event.currentTarget;
    const expenseId = button.getAttribute('data-id');
    
    // Send AJAX request to delete expense
    fetch(`/api/expenses/${expenseId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            showAlert('تم حذف المصروف بنجاح', 'success');
            
            // Remove expense row from table
            const expenseRow = button.closest('tr');
            if (expenseRow) {
                expenseRow.remove();
            }
        } else {
            // Show error message
            showAlert('خطأ: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('حدث خطأ أثناء حذف المصروف', 'danger');
    });
}

/**
 * Handle updating a category budget
 * @param {Event} event - Form submission event
 */
function handleUpdateCategoryBudget(event) {
    event.preventDefault();
    
    const form = event.target;
    const categoryId = form.getAttribute('data-category-id');
    const budgetInput = form.querySelector('.budget-input');
    const budget = budgetInput.value;
    
    // Get category data from the DOM
    const categoryCard = form.closest('.category-card');
    const nameEn = categoryCard.getAttribute('data-name-en');
    const nameAr = categoryCard.getAttribute('data-name-ar');
    
    // Create data object
    const data = {
        name_en: nameEn,
        name_ar: nameAr,
        budget: budget
    };
    
    // Send AJAX request to update category
    fetch(`/api/categories/${categoryId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            showAlert('تم تحديث الميزانية بنجاح', 'success');
            
            // Reload page after short delay to reflect the changes
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            // Show error message
            showAlert('خطأ: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('حدث خطأ أثناء تحديث الميزانية', 'danger');
    });
}

/**
 * Initialize charts on the page
 */
function initializeCharts() {
    // Category pie chart
    const pieChartCanvas = document.getElementById('categoryPieChart');
    if (pieChartCanvas) {
        const categoryTotalsElement = document.getElementById('category-totals-data');
        const categoryNamesElement = document.getElementById('category-names-data');
        
        if (categoryTotalsElement && categoryNamesElement) {
            try {
                const categoryTotals = JSON.parse(categoryTotalsElement.value);
                const categoryNames = JSON.parse(categoryNamesElement.value);
                
                // Extract labels and data from categoryTotals object
                const labels = Object.keys(categoryTotals);
                const data = Object.values(categoryTotals);
                
                // Generate random colors for each category
                const colors = generateRandomColors(labels.length);
                
                // Create chart
                new Chart(pieChartCanvas, {
                    type: 'pie',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: data,
                            backgroundColor: colors,
                            borderColor: colors,
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        legend: {
                            display: false // Hide default legend, we'll use our custom one
                        },
                        tooltips: {
                            enabled: true,
                            mode: 'single',
                            callbacks: {
                                label: function(tooltipItem, data) {
                                    const label = data.labels[tooltipItem.index];
                                    const value = data.datasets[0].data[tooltipItem.index];
                                    return `${label}: ${value}`;
                                }
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Error parsing category totals:', error);
            }
        }
    }
    
    // Monthly expenses bar chart
    const barChartCanvas = document.getElementById('monthlyExpensesChart');
    if (barChartCanvas) {
        const chartLabelsElement = document.getElementById('chart-labels-data');
        const chartValuesElement = document.getElementById('chart-values-data');
        
        if (chartLabelsElement && chartValuesElement) {
            try {
                const chartLabels = JSON.parse(chartLabelsElement.value);
                const chartValues = JSON.parse(chartValuesElement.value);
                
                // Create chart
                new Chart(barChartCanvas, {
                    type: 'bar',
                    data: {
                        labels: chartLabels,
                        datasets: [{
                            label: 'إجمالي المصاريف الشهرية',
                            data: chartValues,
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
            } catch (error) {
                console.error('Error parsing chart data:', error);
            }
        }
    }
}

/**
 * Generate random colors for chart
 * @param {number} count - Number of colors to generate
 * @returns {Array} Array of color strings
 */
function generateRandomColors(count) {
    const colors = [];
    const predefinedColors = [
        '#4ead96', // Primary
        '#e6a23c', // Warning
        '#e15554', // Danger
        '#67c23a', // Success
        '#909399', // Info
        '#c84869', // Accent
        '#2c363f', // Dark
        '#f7f2e4'  // Secondary
    ];
    
    // Use predefined colors first
    for (let i = 0; i < count; i++) {
        if (i < predefinedColors.length) {
            colors.push(predefinedColors[i]);
        } else {
            // Generate random colors if we need more
            const r = Math.floor(Math.random() * 255);
            const g = Math.floor(Math.random() * 255);
            const b = Math.floor(Math.random() * 255);
            colors.push(`rgba(${r}, ${g}, ${b}, 0.8)`);
        }
    }
    
    return colors;
}

/**
 * Show an alert message
 * @param {string} message - The message to display
 * @param {string} type - Alert type (success, danger, warning, info)
 */
function showAlert(message, type) {
    // Create notification element
    const notificationDiv = document.createElement('div');
    notificationDiv.className = `notification notification-${type}`;
    
    // Determine icon based on type
    let icon = 'info-circle';
    if (type === 'success') {
        icon = 'check-circle';
    } else if (type === 'warning') {
        icon = 'exclamation-triangle';
    } else if (type === 'danger' || type === 'error') {
        icon = 'times-circle';
        type = 'error'; // Normalize type
    }
    
    notificationDiv.innerHTML = `
        <div class="notification-icon">
            <i class="fas fa-${icon}"></i>
        </div>
        <div class="notification-message">${message}</div>
        <button type="button" class="notification-close" aria-label="Close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add notification to container
    const notificationContainer = document.getElementById('notification-container');
    if (notificationContainer) {
        // Add to DOM
        notificationContainer.appendChild(notificationDiv);
        
        // Add click listener to close button
        const closeButton = notificationDiv.querySelector('.notification-close');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                notificationDiv.remove();
            });
        }
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notificationDiv.style.opacity = '0';
            setTimeout(() => {
                notificationDiv.remove();
            }, 300);
        }, 5000);
    }
}

/**
 * Fix the width and display issues for select dropdowns
 */
function fixSelectWidthIssues() {
    // Fix all select elements
    const selects = document.querySelectorAll('select.form-control');
    
    selects.forEach(select => {
        // Ensure the select can expand as needed
        select.style.overflow = 'hidden';
        select.style.textOverflow = 'ellipsis';
        select.style.maxWidth = '100%';
        
        // Add change event to ensure selected option is visible
        select.addEventListener('change', function() {
            // Force a repaint to ensure the selected option is fully visible
            this.style.width = '100%';
        });
    });
    
    // Fix mobile view for action buttons
    fixMobileResponsiveLayout();
}

/**
 * Fix mobile responsive layout issues
 */
function fixMobileResponsiveLayout() {
    // Check if we're on a mobile device (less than 768px)
    const isMobile = window.innerWidth < 768;
    
    // Fix action buttons on mobile
    const actionButtonsContainers = document.querySelectorAll('.action-buttons');
    if (isMobile) {
        actionButtonsContainers.forEach(container => {
            container.style.display = 'flex';
            container.style.flexDirection = 'row';
            container.style.gap = '0.5rem';
            container.style.justifyContent = 'flex-end';
        });
    } else {
        actionButtonsContainers.forEach(container => {
            container.style.display = 'flex';
            container.style.gap = '0.5rem';
        });
    }
    
    // Add resize listener to update mobile layout
    window.addEventListener('resize', function() {
        fixMobileResponsiveLayout();
    });
}

// Register event listener for edit expense form
document.addEventListener('DOMContentLoaded', function() {
    const editExpenseForm = document.getElementById('edit-expense-form');
    if (editExpenseForm) {
        editExpenseForm.addEventListener('submit', handleUpdateExpense);
    }
});
