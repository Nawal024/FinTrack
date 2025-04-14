/**
 * Main JavaScript for Personal Expense Tracker
 */

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize date pickers
    initializeDatePickers();
    
    // Setup event listeners
    setupEventListeners();
    
    // Initialize any charts on the page
    initializeCharts();
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
        if (categoryTotalsElement) {
            try {
                const categoryTotals = JSON.parse(categoryTotalsElement.value);
                
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
                            position: 'right',
                            rtl: true,
                            labels: {
                                fontFamily: 'Cairo, sans-serif'
                            }
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
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;
    
    // Add alert to container
    const alertContainer = document.getElementById('alert-container');
    if (alertContainer) {
        alertContainer.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => {
                alertDiv.remove();
            }, 150);
        }, 5000);
    }
}

// Register event listener for edit expense form
document.addEventListener('DOMContentLoaded', function() {
    const editExpenseForm = document.getElementById('edit-expense-form');
    if (editExpenseForm) {
        editExpenseForm.addEventListener('submit', handleUpdateExpense);
    }
});
