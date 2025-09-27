// Loading indicator
const loading = {
    show: function() {
        const loader = document.createElement('div');
        loader.className = 'loading';
        loader.innerHTML = '<div class="loading-spinner"></div>';
        document.body.appendChild(loader);
    },
    hide: function() {
        const loader = document.querySelector('.loading');
        if (loader) {
            loader.remove();
        }
    }
};

// AJAX setup
$.ajaxSetup({
    beforeSend: function() {
        loading.show();
    },
    complete: function() {
        loading.hide();
    }
});

// Skill autocomplete
if (document.getElementById('skill_name')) {
    const skillInput = document.getElementById('skill_name');
    let timeout = null;

    skillInput.addEventListener('input', function() {
        clearTimeout(timeout);
        const query = this.value;
        
        if (query.length >= 2) {
            timeout = setTimeout(() => {
                $.get(`/api/skill_search?q=${encodeURIComponent(query)}`, function(data) {
                    // Implement autocomplete UI
                });
            }, 300);
        }
    });
}

// Progress tracking
document.querySelectorAll('.mark-complete').forEach(button => {
    button.addEventListener('click', function() {
        const pathId = this.dataset.pathId;
        const resourceId = this.dataset.resourceId;
        
        $.ajax({
            url: '/update_progress',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                path_id: pathId,
                resource_id: resourceId,
                completed: true
            }),
            success: function(response) {
                if (response.success) {
                    location.reload();
                }
            }
        });
    });
});

// Learning path status updates
document.querySelectorAll('.path-status').forEach(button => {
    button.addEventListener('click', function() {
        const pathId = this.dataset.pathId;
        const status = this.dataset.status;
        
        $.ajax({
            url: '/update_path_status',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                path_id: pathId,
                status: status
            }),
            success: function(response) {
                if (response.success) {
                    location.reload();
                }
            }
        });
    });
});

// Job application status updates
document.querySelectorAll('.update-status').forEach(button => {
    button.addEventListener('click', function() {
        const jobId = this.dataset.jobId;
        document.getElementById('jobId').value = jobId;
    });
});

document.getElementById('saveStatus')?.addEventListener('click', function() {
    const data = {
        job_id: document.getElementById('jobId').value,
        status: document.getElementById('status').value,
        notes: document.getElementById('notes').value
    };
    
    $.ajax({
        url: '/update_opportunity_status',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            if (response.success) {
                location.reload();
            }
        }
    });
});

// Profile form validation
const profileForm = document.querySelector('form[action="/profile"]');
if (profileForm) {
    profileForm.addEventListener('submit', function(e) {
        const targetSalary = document.getElementById('target_salary');
        const salary = parseInt(targetSalary.value);
        
        if (salary < 0) {
            e.preventDefault();
            targetSalary.classList.add('is-invalid');
            targetSalary.nextElementSibling.textContent = 'Salary cannot be negative';
        }
    });
}

// Notifications
function showNotification(message, type = 'success') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Chart initialization (if Chart.js is included)
function initializeCharts() {
    const ctx = document.getElementById('skillsChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: skillLabels,
                datasets: [{
                    label: 'Current Skills',
                    data: currentSkillLevels,
                    fill: true,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgb(54, 162, 235)',
                    pointBackgroundColor: 'rgb(54, 162, 235)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(54, 162, 235)'
                }, {
                    label: 'Required Skills',
                    data: requiredSkillLevels,
                    fill: true,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgb(255, 99, 132)',
                    pointBackgroundColor: 'rgb(255, 99, 132)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(255, 99, 132)'
                }]
            },
            options: {
                elements: {
                    line: {
                        borderWidth: 3
                    }
                },
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 5
                    }
                }
            }
        });
    }
}

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Initialize charts if they exist
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
});