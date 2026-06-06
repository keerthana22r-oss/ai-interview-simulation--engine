// AJAX Functions for AI Interview Platform

// Generic AJAX function
function ajaxRequest(url, method, data, successCallback, errorCallback) {
    $.ajax({
        url: url,
        method: method,
        data: data,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        },
        success: function(response) {
            if (successCallback) {
                successCallback(response);
            }
        },
        error: function(xhr, status, error) {
            if (errorCallback) {
                errorCallback(xhr, status, error);
            } else {
                console.error('AJAX Error:', error);
                showNotification('An error occurred. Please try again.', 'error');
            }
        }
    });
}

// Mark notification as read
function markNotificationRead(notificationId, element) {
    ajaxRequest(
        `/notifications/mark-read/${notificationId}/`,
        'POST',
        {},
        function(response) {
            if (response.success) {
                $(element).closest('.notification-item').removeClass('bg-blue-50');
                $(element).remove();
                updateNotificationCount();
            }
        }
    );
}

// Mark all notifications as read
function markAllNotificationsRead() {
    ajaxRequest(
        '/notifications/mark-all-read/',
        'POST',
        {},
        function(response) {
            if (response.success) {
                $('.notification-item').removeClass('bg-blue-50');
                $('.mark-read-btn').remove();
                updateNotificationCount();
                showNotification('All notifications marked as read');
            }
        }
    );
}

// Update notification count in navbar
function updateNotificationCount() {
    const unreadCount = $('.notification-item.bg-blue-50').length;
    const badge = $('.notification-badge');
    
    if (unreadCount > 0) {
        badge.text(unreadCount);
        badge.removeClass('hidden');
    } else {
        badge.addClass('hidden');
    }
}

// Save question
function saveQuestion(questionId, button) {
    const note = prompt('Add a note (optional):');
    
    $.ajax({
        url: `/save-question/${questionId}/`,
        method: 'POST',
        data: {
            'note': note || ''
        },
        success: function(response) {
            showNotification('Question saved successfully!', 'success');
            $(button).hide();
            $(button).after('<span class="text-green-600 text-sm">Saved</span>');
        },
        error: function(xhr) {
            if (xhr.status === 400) {
                showNotification('Question already saved', 'warning');
            } else {
                showNotification('Error saving question', 'error');
            }
        }
    });
}

// Unsave question
function unsaveQuestion(savedId, button) {
    if (confirm('Remove this question from saved items?')) {
        $.ajax({
            url: `/unsave-question/${savedId}/`,
            method: 'POST',
            success: function(response) {
                showNotification('Question removed from saved items', 'success');
                $(button).closest('.saved-question-item').remove();
            },
            error: function() {
                showNotification('Error removing question', 'error');
            }
        });
    }
}

// Add note to session
function addSessionNote(sessionId) {
    const note = prompt('Enter your note:');
    if (note && note.trim()) {
        $.ajax({
            url: `/add-note/${sessionId}/`,
            method: 'POST',
            data: {
                'note': note
            },
            success: function(response) {
                showNotification('Note added successfully', 'success');
                location.reload();
            },
            error: function() {
                showNotification('Error adding note', 'error');
            }
        });
    }
}

// Delete note
function deleteNote(noteId, element) {
    if (confirm('Delete this note?')) {
        $.ajax({
            url: `/delete-note/${noteId}/`,
            method: 'POST',
            success: function(response) {
                showNotification('Note deleted', 'success');
                $(element).closest('.note-item').remove();
            },
            error: function() {
                showNotification('Error deleting note', 'error');
            }
        });
    }
}

// Load dashboard stats via AJAX
function loadDashboardStats() {
    ajaxRequest(
        '/api/dashboard-stats/',
        'GET',
        {},
        function(response) {
            updateDashboardUI(response);
        }
    );
}

// Update dashboard UI with AJAX data
function updateDashboardUI(data) {
    $('#total-sessions').text(data.total_sessions);
    $('#completed-sessions').text(data.completed_sessions);
    $('#average-score').text(data.average_score.toFixed(0) + '%');
    
    if (data.trend && data.trend.length > 0) {
        updatePerformanceChart(data.trend);
    }
}

// Update performance chart
function updatePerformanceChart(trendData) {
    const ctx = document.getElementById('performanceChart');
    if (ctx && window.performanceChart) {
        window.performanceChart.data.labels = trendData.map(item => item.date);
        window.performanceChart.data.datasets[0].data = trendData.map(item => item.avg_score);
        window.performanceChart.update();
    }
}

// Search questions
let searchTimeout;
function searchQuestions(searchInput) {
    clearTimeout(searchTimeout);
    const query = $(searchInput).val();
    
    if (query.length >= 2) {
        searchTimeout = setTimeout(() => {
            ajaxRequest(
                '/search/questions/',
                'GET',
                { q: query },
                function(response) {
                    displaySearchResults(response);
                }
            );
        }, 300);
    }
}

// Display search results
function displaySearchResults(results) {
    const resultsContainer = $('#search-results');
    resultsContainer.empty();
    
    if (results.length === 0) {
        resultsContainer.html('<p class="text-gray-500">No results found</p>');
        return;
    }
    
    results.forEach(result => {
        resultsContainer.append(`
            <div class="p-3 border rounded hover:bg-gray-50">
                <a href="${result.url}" class="text-indigo-600 hover:underline">
                    ${result.title}
                </a>
                <p class="text-sm text-gray-500">${result.description}</p>
            </div>
        `);
    });
}

// Filter job roles
function filterJobRoles() {
    const domain = $('#domain-filter').val();
    const difficulty = $('#difficulty-filter').val();
    const search = $('#search-input').val();
    
    window.location.href = `/job-roles/?domain=${domain}&difficulty=${difficulty}&search=${search}`;
}

// Auto-save answer for interview
let autoSaveTimeout;
function autoSaveAnswer(questionId, answerText, timeSpent) {
    clearTimeout(autoSaveTimeout);
    autoSaveTimeout = setTimeout(() => {
        $.ajax({
            url: `/api/sessions/${questionId}/answer/`,
            method: 'POST',
            data: {
                'answer_text': answerText,
                'time_spent_seconds': timeSpent
            },
            success: function(response) {
                $('#save-status').text('Saved');
                setTimeout(() => {
                    $('#save-status').text('');
                }, 2000);
            },
            error: function() {
                $('#save-status').text('Error saving');
            }
        });
    }, 1000);
}

// Timer for interview
let interviewTimer;
let timeElapsed = 0;

function startTimer(displayElement) {
    if (interviewTimer) {
        clearInterval(interviewTimer);
    }
    
    interviewTimer = setInterval(() => {
        timeElapsed++;
        const minutes = Math.floor(timeElapsed / 60);
        const seconds = timeElapsed % 60;
        $(displayElement).text(`${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
        
        // Auto-save periodically
        if (timeElapsed % 30 === 0) {
            const answerText = $('#answer-text').val();
            if (answerText) {
                autoSaveAnswer(currentQuestionId, answerText, timeElapsed);
            }
        }
    }, 1000);
}

function stopTimer() {
    if (interviewTimer) {
        clearInterval(interviewTimer);
        interviewTimer = null;
    }
}

// Export AJAX functions
window.markNotificationRead = markNotificationRead;
window.markAllNotificationsRead = markAllNotificationsRead;
window.saveQuestion = saveQuestion;
window.unsaveQuestion = unsaveQuestion;
window.addSessionNote = addSessionNote;
window.deleteNote = deleteNote;
window.filterJobRoles = filterJobRoles;
window.startTimer = startTimer;
window.stopTimer = stopTimer;