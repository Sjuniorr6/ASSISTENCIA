/**
 * Sistema de Validação Client-Side
 * Validação em tempo real para formulários
 */

class FormValidator {
    constructor(formId, options = {}) {
        this.form = document.getElementById(formId);
        this.options = {
            validateOnInput: true,
            validateOnBlur: true,
            showErrors: true,
            ...options
        };
        
        this.errors = {};
        this.init();
    }
    
    init() {
        if (!this.form) return;
        
        // Adiciona listeners para todos os campos
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (this.options.validateOnInput) {
                input.addEventListener('input', () => this.validateField(input));
            }
            if (this.options.validateOnBlur) {
                input.addEventListener('blur', () => this.validateField(input));
            }
        });
        
        // Listener para submissão do formulário
        this.form.addEventListener('submit', (e) => this.validateForm(e));
    }
    
    validateField(field) {
        const fieldName = field.name;
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';
        
        // Remove classes de erro anteriores
        this.removeFieldError(field);
        
        // Validações específicas por tipo de campo
        switch (fieldName) {
            case 'nome':
                if (!value) {
                    isValid = false;
                    errorMessage = 'Nome é obrigatório';
                } else if (value.length < 2) {
                    isValid = false;
                    errorMessage = 'Nome deve ter pelo menos 2 caracteres';
                }
                break;
                
            case 'telefone':
                if (value && !this.isValidPhone(value)) {
                    isValid = false;
                    errorMessage = 'Telefone inválido';
                }
                break;
                
            case 'email':
                if (value && !this.isValidEmail(value)) {
                    isValid = false;
                    errorMessage = 'Email inválido';
                }
                break;
                
            case 'cpf_cnpj':
                if (value && !this.isValidCPFCNPJ(value)) {
                    isValid = false;
                    errorMessage = 'CPF/CNPJ inválido';
                }
                break;
                
            case 'cep':
                if (value && !this.isValidCEP(value)) {
                    isValid = false;
                    errorMessage = 'CEP inválido';
                }
                break;
                
            case 'valor_total':
                if (value && !this.isValidNumber(value)) {
                    isValid = false;
                    errorMessage = 'Valor deve ser um número válido';
                }
                break;
        }
        
        // Validações gerais
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'Este campo é obrigatório';
        }
        
        // Aplica resultado da validação
        if (!isValid) {
            this.addFieldError(field, errorMessage);
            this.errors[fieldName] = errorMessage;
        } else {
            delete this.errors[fieldName];
        }
        
        return isValid;
    }
    
    validateForm(e) {
        const inputs = this.form.querySelectorAll('input, select, textarea');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            this.showFormError('Por favor, corrija os erros no formulário.');
        }
        
        return isValid;
    }
    
    addFieldError(field, message) {
        field.classList.add('error');
        field.style.borderColor = '#dc2626';
        
        if (this.options.showErrors) {
            // Remove mensagem de erro anterior
            this.removeFieldError(field);
            
            // Cria nova mensagem de erro
            const errorDiv = document.createElement('div');
            errorDiv.className = 'field-error-message';
            errorDiv.style.cssText = `
                color: #dc2626;
                font-size: 0.75rem;
                margin-top: 0.25rem;
                display: block;
            `;
            errorDiv.textContent = message;
            
            // Insere após o campo
            field.parentNode.appendChild(errorDiv);
        }
    }
    
    removeFieldError(field) {
        field.classList.remove('error');
        field.style.borderColor = '';
        
        // Remove mensagem de erro
        const errorMessage = field.parentNode.querySelector('.field-error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }
    
    showFormError(message) {
        // Remove mensagem anterior
        this.removeFormError();
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error-message';
        errorDiv.style.cssText = `
            background-color: #fef2f2;
            border: 1px solid #fecaca;
            color: #dc2626;
            padding: 0.75rem;
            border-radius: 0.375rem;
            margin-bottom: 1rem;
            font-size: 0.875rem;
        `;
        errorDiv.textContent = message;
        
        // Insere no início do formulário
        this.form.insertBefore(errorDiv, this.form.firstChild);
    }
    
    removeFormError() {
        const errorMessage = this.form.querySelector('.form-error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }
    
    // Métodos de validação específicos
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    isValidPhone(phone) {
        const phoneRegex = /^[\d\s\(\)\-\+]+$/;
        return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10;
    }
    
    isValidCPFCNPJ(value) {
        const cleanValue = value.replace(/\D/g, '');
        return cleanValue.length === 11 || cleanValue.length === 14;
    }
    
    isValidCEP(cep) {
        const cleanCEP = cep.replace(/\D/g, '');
        return cleanCEP.length === 8;
    }
    
    isValidNumber(value) {
        return !isNaN(parseFloat(value)) && isFinite(value);
    }
    
    // Métodos públicos
    getErrors() {
        return this.errors;
    }
    
    hasErrors() {
        return Object.keys(this.errors).length > 0;
    }
    
    clearErrors() {
        this.errors = {};
        const inputs = this.form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => this.removeFieldError(input));
        this.removeFormError();
    }
}

// Função global para inicializar validação
function initFormValidation(formId, options = {}) {
    return new FormValidator(formId, options);
}

// Auto-inicialização para formulários com data-validate
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('[data-validate]');
    forms.forEach(form => {
        new FormValidator(form.id, {
            validateOnInput: true,
            validateOnBlur: true,
            showErrors: true
        });
    });
}); 