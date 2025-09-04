/**
 * GUTO - Sistema de Utilitários
 * Biblioteca JavaScript centralizada para funcionalidades administrativas
 * 
 * @author Equipe GUTO
 * @version 2.0
 * @since 2025-09-01
 */

// Global utilities namespace
window.GUTO = window.GUTO || {};
window.GUTO.Utils = {
    // Configuration
    config: {
        animationDuration: 300,
        debounceDelay: 300,
        autoRefreshInterval: 30000,
        maxToastNotifications: 5,
        dateFormat: 'dd/mm/yyyy',
        timeFormat: 'HH:mm'
    },

    // Utility functions
    debounce: function(func, delay = 300) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    },

    throttle: function(func, limit = 100) {
        let inThrottle;
        return function () {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    formatDate: function(date, format = 'dd/mm/yyyy HH:mm') {
        const d = new Date(date);
        const day = String(d.getDate()).padStart(2, '0');
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const year = d.getFullYear();
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        
        return format
            .replace('dd', day)
            .replace('mm', month)
            .replace('yyyy', year)
            .replace('HH', hours)
            .replace('mm', minutes);
    },

    timeAgo: function(date) {
        const now = new Date();
        const diffMs = now - new Date(date);
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) return 'agora mesmo';
        if (diffMins < 60) return `há ${diffMins} minuto${diffMins > 1 ? 's' : ''}`;
        if (diffHours < 24) return `há ${diffHours} hora${diffHours > 1 ? 's' : ''}`;
        if (diffDays < 7) return `há ${diffDays} dia${diffDays > 1 ? 's' : ''}`;
        
        return this.formatDate(date);
    },

    generateId: function(prefix = 'guto') {
        return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    },

    sanitizeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    copyToClipboard: async function(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('success', 'Copiado para a área de transferência!');
            return true;
        } catch (err) {
            console.error('Erro ao copiar:', err);
            return false;
        }
    },

    downloadFile: function(data, filename, type = 'text/plain') {
        const blob = new Blob([data], { type });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
};

// Toast notification system
window.GUTO.Toast = {
    container: null,
    notifications: new Map(),

    init: function() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'guto-toast-container';
            this.container.className = 'fixed top-4 right-4 z-50 space-y-2 max-w-sm';
            document.body.appendChild(this.container);
        }
    },

    show: function(type = 'info', message, options = {}) {
        this.init();
        
        const id = GUTO.Utils.generateId('toast');
        const toast = this.createToastElement(id, type, message, options);
        
        this.container.appendChild(toast);
        this.notifications.set(id, toast);
        
        // Animate in
        requestAnimationFrame(() => {
            toast.classList.add('translate-x-0', 'opacity-100');
        });
        
        // Auto dismiss
        if (options.autoDismiss !== false) {
            setTimeout(() => this.dismiss(id), options.duration || 5000);
        }
        
        // Limit max notifications
        if (this.notifications.size > GUTO.Utils.config.maxToastNotifications) {
            const firstId = this.notifications.keys().next().value;
            this.dismiss(firstId);
        }
        
        return id;
    },

    createToastElement: function(id, type, message, options) {
        const typeConfig = {
            success: { icon: 'check-circle', color: 'bg-green-500' },
            error: { icon: 'times-circle', color: 'bg-red-500' },
            warning: { icon: 'exclamation-triangle', color: 'bg-yellow-500' },
            info: { icon: 'info-circle', color: 'bg-blue-500' }
        };
        
        const config = typeConfig[type] || typeConfig.info;
        
        const toast = document.createElement('div');
        toast.id = id;
        toast.className = `transform translate-x-full opacity-0 transition-all duration-300 ${config.color} text-white p-4 rounded-lg shadow-lg`;
        
        toast.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${config.icon} mr-3"></i>
                <div class="flex-1">
                    ${options.title ? `<div class="font-semibold">${options.title}</div>` : ''}
                    <div class="${options.title ? 'text-sm opacity-90' : ''}">${message}</div>
                </div>
                <button onclick="GUTO.Toast.dismiss('${id}')" class="ml-3 text-white hover:text-gray-200 transition-colors">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        return toast;
    },

    dismiss: function(id) {
        const toast = this.notifications.get(id);
        if (!toast) return;
        
        toast.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            this.notifications.delete(id);
        }, 300);
    },

    dismissAll: function() {
        this.notifications.forEach((toast, id) => this.dismiss(id));
    }
};

// Modal system
window.GUTO.Modal = {
    active: null,
    
    show: function(modalId, options = {}) {
        const modal = document.getElementById(modalId);
        if (!modal) {
            console.error(`Modal ${modalId} não encontrado`);
            return false;
        }
        
        this.active = modalId;
        modal.classList.remove('hidden');
        
        // Focus management
        const firstFocusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (firstFocusable) {
            setTimeout(() => firstFocusable.focus(), 100);
        }
        
        // Close on escape
        if (options.escapeKey !== false) {
            this.addEscapeListener();
        }
        
        // Close on backdrop click
        if (options.backdropClose !== false) {
            this.addBackdropListener(modalId);
        }
        
        return true;
    },
    
    hide: function(modalId = null) {
        const id = modalId || this.active;
        if (!id) return false;
        
        const modal = document.getElementById(id);
        if (modal) {
            modal.classList.add('hidden');
        }
        
        if (this.active === id) {
            this.active = null;
        }
        
        this.removeListeners();
        return true;
    },
    
    addEscapeListener: function() {
        document.addEventListener('keydown', this.escapeHandler);
    },
    
    escapeHandler: function(e) {
        if (e.key === 'Escape' && GUTO.Modal.active) {
            GUTO.Modal.hide();
        }
    },
    
    addBackdropListener: function(modalId) {
        const modal = document.getElementById(modalId);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.hide(modalId);
            }
        });
    },
    
    removeListeners: function() {
        document.removeEventListener('keydown', this.escapeHandler);
    }
};

// Loading overlay
window.GUTO.Loading = {
    overlay: null,
    
    show: function(message = 'Carregando...') {
        this.hide(); // Remove existing overlay
        
        this.overlay = document.createElement('div');
        this.overlay.className = 'fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center';
        this.overlay.innerHTML = `
            <div class="bg-white rounded-lg p-6 shadow-xl">
                <div class="flex items-center">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mr-4"></div>
                    <span class="text-gray-700">${message}</span>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.overlay);
    },
    
    hide: function() {
        if (this.overlay) {
            document.body.removeChild(this.overlay);
            this.overlay = null;
        }
    }
};

// Form utilities
window.GUTO.Form = {
    validate: function(form) {
        const errors = {};
        const inputs = form.querySelectorAll('[data-validate]');
        
        inputs.forEach(input => {
            const rules = input.dataset.validate.split('|');
            const value = input.value.trim();
            const name = input.name || input.id;
            
            rules.forEach(rule => {
                const [ruleName, ruleValue] = rule.split(':');
                
                switch(ruleName) {
                    case 'required':
                        if (!value) {
                            errors[name] = 'Este campo é obrigatório';
                        }
                        break;
                    case 'min':
                        if (value.length < parseInt(ruleValue)) {
                            errors[name] = `Mínimo de ${ruleValue} caracteres`;
                        }
                        break;
                    case 'max':
                        if (value.length > parseInt(ruleValue)) {
                            errors[name] = `Máximo de ${ruleValue} caracteres`;
                        }
                        break;
                    case 'email':
                        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                        if (value && !emailRegex.test(value)) {
                            errors[name] = 'Email inválido';
                        }
                        break;
                }
            });
        });
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    },
    
    showErrors: function(errors) {
        // Clear existing errors
        document.querySelectorAll('.error-message').forEach(el => el.remove());
        document.querySelectorAll('.border-red-500').forEach(el => {
            el.classList.remove('border-red-500');
        });
        
        // Show new errors
        Object.keys(errors).forEach(field => {
            const input = document.querySelector(`[name="${field}"], #${field}`);
            if (input) {
                input.classList.add('border-red-500');
                
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message text-red-500 text-sm mt-1';
                errorDiv.textContent = errors[field];
                
                input.parentNode.appendChild(errorDiv);
            }
        });
    },
    
    serialize: function(form) {
        const data = {};
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            const name = input.name || input.id;
            if (!name) return;
            
            if (input.type === 'checkbox') {
                data[name] = input.checked;
            } else if (input.type === 'radio') {
                if (input.checked) {
                    data[name] = input.value;
                }
            } else {
                data[name] = input.value;
            }
        });
        
        return data;
    }
};

// Table utilities
window.GUTO.Table = {
    sort: function(table, columnIndex, direction = 'asc') {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aVal = a.cells[columnIndex].textContent.trim();
            const bVal = b.cells[columnIndex].textContent.trim();
            
            // Try to parse as numbers
            const aNum = parseFloat(aVal);
            const bNum = parseFloat(bVal);
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return direction === 'asc' ? aNum - bNum : bNum - aNum;
            }
            
            // String comparison
            return direction === 'asc' 
                ? aVal.localeCompare(bVal)
                : bVal.localeCompare(aVal);
        });
        
        // Reorder rows
        rows.forEach(row => tbody.appendChild(row));
    },
    
    filter: function(table, searchTerm, columns = []) {
        const tbody = table.querySelector('tbody');
        const rows = tbody.querySelectorAll('tr');
        const term = searchTerm.toLowerCase();
        
        let visibleCount = 0;
        
        rows.forEach(row => {
            const cells = Array.from(row.cells);
            const searchableText = columns.length > 0
                ? columns.map(i => cells[i]?.textContent || '').join(' ')
                : row.textContent;
            
            if (searchableText.toLowerCase().includes(term)) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });
        
        return visibleCount;
    },
    
    paginate: function(table, page = 1, itemsPerPage = 10) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr:not([style*="display: none"])'));
        const totalPages = Math.ceil(rows.length / itemsPerPage);
        const startIndex = (page - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        
        rows.forEach((row, index) => {
            if (index >= startIndex && index < endIndex) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
        
        return {
            currentPage: page,
            totalPages,
            totalItems: rows.length,
            itemsPerPage
        };
    }
};

// Search utilities
window.GUTO.Search = {
    highlightTerms: function(text, searchTerm) {
        if (!searchTerm) return text;
        
        const regex = new RegExp(`(${searchTerm})`, 'gi');
        return text.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
    },
    
    createSearchHandler: function(input, callback, delay = 300) {
        return GUTO.Utils.debounce((e) => {
            const term = e.target.value.trim();
            callback(term);
        }, delay);
    }
};

// Analytics utilities
window.GUTO.Analytics = {
    track: function(event, data = {}) {
        // Basic tracking - can be extended for Google Analytics, etc.
        console.log('Analytics Event:', event, data);
        
        // Store in localStorage for basic tracking
        const events = JSON.parse(localStorage.getItem('guto_analytics') || '[]');
        events.push({
            event,
            data,
            timestamp: new Date().toISOString(),
            url: window.location.href
        });
        
        // Keep only last 100 events
        if (events.length > 100) {
            events.splice(0, events.length - 100);
        }
        
        localStorage.setItem('guto_analytics', JSON.stringify(events));
    },
    
    getEvents: function(limit = 50) {
        const events = JSON.parse(localStorage.getItem('guto_analytics') || '[]');
        return events.slice(-limit);
    },
    
    clearEvents: function() {
        localStorage.removeItem('guto_analytics');
    }
};

// Auto-refresh system
window.GUTO.AutoRefresh = {
    intervals: new Map(),
    
    start: function(key, callback, interval = 30000) {
        this.stop(key); // Clear existing interval
        
        const intervalId = setInterval(() => {
            try {
                callback();
            } catch (error) {
                console.error(`Auto-refresh error for ${key}:`, error);
                this.stop(key);
            }
        }, interval);
        
        this.intervals.set(key, intervalId);
    },
    
    stop: function(key) {
        const intervalId = this.intervals.get(key);
        if (intervalId) {
            clearInterval(intervalId);
            this.intervals.delete(key);
        }
    },
    
    stopAll: function() {
        this.intervals.forEach((intervalId, key) => {
            clearInterval(intervalId);
        });
        this.intervals.clear();
    }
};

// Storage utilities
window.GUTO.Storage = {
    set: function(key, value, expiry = null) {
        const data = {
            value,
            timestamp: Date.now(),
            expiry: expiry ? Date.now() + expiry : null
        };
        localStorage.setItem(`guto_${key}`, JSON.stringify(data));
    },
    
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(`guto_${key}`);
            if (!item) return defaultValue;
            
            const data = JSON.parse(item);
            
            // Check expiry
            if (data.expiry && Date.now() > data.expiry) {
                this.remove(key);
                return defaultValue;
            }
            
            return data.value;
        } catch (error) {
            console.error('Storage get error:', error);
            return defaultValue;
        }
    },
    
    remove: function(key) {
        localStorage.removeItem(`guto_${key}`);
    },
    
    clear: function() {
        const keys = Object.keys(localStorage);
        keys.forEach(key => {
            if (key.startsWith('guto_')) {
                localStorage.removeItem(key);
            }
        });
    }
};

// Charts utilities (for future use)
window.GUTO.Charts = {
    colors: {
        primary: '#4F46E5',
        secondary: '#7C3AED',
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
        info: '#3B82F6'
    },
    
    generateColors: function(count) {
        const colors = Object.values(this.colors);
        const result = [];
        
        for (let i = 0; i < count; i++) {
            result.push(colors[i % colors.length]);
        }
        
        return result;
    }
};

// Initialize common features
document.addEventListener('DOMContentLoaded', function() {
    // Initialize toast system
    GUTO.Toast.init();
    
    // Track page views
    GUTO.Analytics.track('page_view', {
        page: window.location.pathname,
        title: document.title
    });
    
    // Add global error handler
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        GUTO.Toast.show('error', 'Ocorreu um erro inesperado. Tente novamente.');
    });
    
    // Add unload handler to clean up intervals
    window.addEventListener('beforeunload', function() {
        GUTO.AutoRefresh.stopAll();
    });
    
    console.log('🚀 GUTO Utilities loaded successfully');
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.GUTO;
}