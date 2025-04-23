// Scripts específicos para a área administrativa

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar formulário de login
    initLoginForm();
    
    // Inicializar formulário de registro de ponto de coleta
    initRegistroForm();
});

// Função para inicializar o formulário de login
function initLoginForm() {
    const loginForm = document.getElementById('login-form');
    if (!loginForm) return;
    
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Obter dados do formulário
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        // Validar campos
        if (!email || !password) {
            showMessage('Por favor, preencha todos os campos', 'error');
            return;
        }
        
        // Criar FormData para envio
        const formData = new FormData();
        formData.append('email', email);
        formData.append('password', password);
        
        // Exibir indicador de carregamento
        showLoading();
        
        // Enviar requisição para a API
        fetch('/api/admin/login', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.error) {
                showMessage(data.error, 'error');
            } else if (data.success) {
                showMessage('Login realizado com sucesso!', 'success');
                
                // Redirecionar para a página de registro de ponto
                setTimeout(function() {
                    window.location.href = data.redirect || '/registroponto';
                }, 1000);
            }
        })
        .catch(error => {
            hideLoading();
            showMessage('Erro ao processar a requisição. Tente novamente.', 'error');
            console.error('Erro:', error);
        });
    });
}

// Função para inicializar o formulário de registro de ponto de coleta
function initRegistroForm() {
    const registroForm = document.getElementById('registro-form');
    if (!registroForm) return;
    
    registroForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validar formulário
        if (!validateForm(registroForm)) {
            return;
        }
        
        // Criar FormData para envio
        const formData = new FormData(registroForm);
        
        // Exibir indicador de carregamento
        showLoading();
        
        // Enviar requisição para a API
        fetch('/api/admin/registrar-ponto', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.error) {
                showMessage(data.error, 'error');
            } else if (data.success) {
                showMessage(data.message, 'success');
                
                // Limpar formulário
                registroForm.reset();
            }
        })
        .catch(error => {
            hideLoading();
            showMessage('Erro ao processar a requisição. Tente novamente.', 'error');
            console.error('Erro:', error);
        });
    });
}

// Função para validar formulário
function validateForm(form) {
    let isValid = true;
    
    // Verificar campos obrigatórios
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('invalid');
            
            // Adicionar mensagem de erro se não existir
            let errorMsg = field.parentNode.querySelector('.error-message');
            if (!errorMsg) {
                errorMsg = document.createElement('div');
                errorMsg.className = 'error-message';
                errorMsg.style.color = 'red';
                errorMsg.style.fontSize = '0.8rem';
                errorMsg.style.marginTop = '5px';
                field.parentNode.appendChild(errorMsg);
            }
            errorMsg.textContent = 'Este campo é obrigatório';
        } else {
            field.classList.remove('invalid');
            const errorMsg = field.parentNode.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.remove();
            }
        }
    });
    
    // Validar CNPJ se existir
    const cnpjField = form.querySelector('#cnpj');
    if (cnpjField && cnpjField.value.trim()) {
        if (!validateCNPJ(cnpjField.value)) {
            isValid = false;
            cnpjField.classList.add('invalid');
            
            // Adicionar mensagem de erro se não existir
            let errorMsg = cnpjField.parentNode.querySelector('.error-message');
            if (!errorMsg) {
                errorMsg = document.createElement('div');
                errorMsg.className = 'error-message';
                errorMsg.style.color = 'red';
                errorMsg.style.fontSize = '0.8rem';
                errorMsg.style.marginTop = '5px';
                cnpjField.parentNode.appendChild(errorMsg);
            }
            errorMsg.textContent = 'Por favor, insira um CNPJ válido';
        }
    }
    
    return isValid;
}

// Função para validar CNPJ
function validateCNPJ(cnpj) {
    cnpj = cnpj.replace(/[^\d]+/g, '');
    
    if (cnpj === '') return false;
    
    // Elimina CNPJs inválidos conhecidos
    if (cnpj.length !== 14 ||
        cnpj === "00000000000000" || 
        cnpj === "11111111111111" || 
        cnpj === "22222222222222" || 
        cnpj === "33333333333333" || 
        cnpj === "44444444444444" || 
        cnpj === "55555555555555" || 
        cnpj === "66666666666666" || 
        cnpj === "77777777777777" || 
        cnpj === "88888888888888" || 
        cnpj === "99999999999999")
        return false;
    
    // Valida DVs
    let tamanho = cnpj.length - 2;
    let numeros = cnpj.substring(0, tamanho);
    let digitos = cnpj.substring(tamanho);
    let soma = 0;
    let pos = tamanho - 7;
    
    for (let i = tamanho; i >= 1; i--) {
        soma += numeros.charAt(tamanho - i) * pos--;
        if (pos < 2) pos = 9;
    }
    
    let resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
    if (resultado != digitos.charAt(0)) return false;
    
    tamanho = tamanho + 1;
    numeros = cnpj.substring(0, tamanho);
    soma = 0;
    pos = tamanho - 7;
    
    for (let i = tamanho; i >= 1; i--) {
        soma += numeros.charAt(tamanho - i) * pos--;
        if (pos < 2) pos = 9;
    }
    
    resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
    if (resultado != digitos.charAt(1)) return false;
    
    return true;
}

// Função para exibir mensagem
function showMessage(message, type) {
    // Verificar se já existe uma mensagem
    let messageContainer = document.querySelector('.message-container');
    
    if (!messageContainer) {
        // Criar container de mensagem
        messageContainer = document.createElement('div');
        messageContainer.className = 'message-container';
        document.body.appendChild(messageContainer);
    }
    
    // Criar elemento de mensagem
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}`;
    messageElement.textContent = message;
    
    // Adicionar botão de fechar
    const closeButton = document.createElement('button');
    closeButton.className = 'close-button';
    closeButton.innerHTML = '&times;';
    closeButton.addEventListener('click', function() {
        messageElement.remove();
    });
    
    messageElement.appendChild(closeButton);
    messageContainer.appendChild(messageElement);
    
    // Remover mensagem após 5 segundos
    setTimeout(function() {
        if (messageElement.parentNode) {
            messageElement.remove();
        }
    }, 5000);
}

// Função para exibir indicador de carregamento
function showLoading() {
    // Verificar se já existe um indicador de carregamento
    if (document.querySelector('.loading-overlay')) return;
    
    // Criar overlay de carregamento
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    
    // Criar spinner
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    
    loadingOverlay.appendChild(spinner);
    document.body.appendChild(loadingOverlay);
}

// Função para ocultar indicador de carregamento
function hideLoading() {
    const loadingOverlay = document.querySelector('.loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

// Função para fazer logout
function logout() {
    // Redirecionar para a rota de logout
    window.location.href = '/admin/logout';
}

// Adicionar estilos para mensagens e indicador de carregamento
(function() {
    const style = document.createElement('style');
    style.textContent = `
        .message-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 300px;
        }
        
        .message {
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            position: relative;
            animation: slideIn 0.3s ease-out;
        }
        
        .message.success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .message.error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .close-button {
            position: absolute;
            top: 5px;
            right: 5px;
            background: none;
            border: none;
            font-size: 16px;
            cursor: pointer;
            color: inherit;
        }
        
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
})();
