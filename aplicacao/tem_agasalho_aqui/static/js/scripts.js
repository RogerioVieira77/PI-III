// Scripts para o projeto "Agasalho Aqui"

// Função para inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar recursos de acessibilidade
    initAccessibility();
    
    // Inicializar formulários
    initForms();
    
    // Inicializar mapa se estiver na página de pontos de coleta
    if (document.querySelector('.map-container')) {
        initMap();
    }
});

// Funções de acessibilidade
function initAccessibility() {
    // Adicionar controles de acessibilidade se não existirem
    if (!document.querySelector('.accessibility-controls')) {
        const accessibilityControls = document.createElement('div');
        accessibilityControls.className = 'accessibility-controls';
        
        // Botão para aumentar fonte
        const increaseFontBtn = document.createElement('button');
        increaseFontBtn.className = 'accessibility-button';
        increaseFontBtn.innerHTML = 'A+';
        increaseFontBtn.title = 'Aumentar tamanho da fonte';
        increaseFontBtn.onclick = function() { changeFontSize(1); };
        
        // Botão para diminuir fonte
        const decreaseFontBtn = document.createElement('button');
        decreaseFontBtn.className = 'accessibility-button';
        decreaseFontBtn.innerHTML = 'A-';
        decreaseFontBtn.title = 'Diminuir tamanho da fonte';
        decreaseFontBtn.onclick = function() { changeFontSize(-1); };
        
        // Botão para alto contraste
        const contrastBtn = document.createElement('button');
        contrastBtn.className = 'accessibility-button';
        contrastBtn.innerHTML = 'Contraste';
        contrastBtn.title = 'Alternar alto contraste';
        contrastBtn.onclick = toggleContrast;
        
        // Adicionar botões ao controle
        accessibilityControls.appendChild(increaseFontBtn);
        accessibilityControls.appendChild(decreaseFontBtn);
        accessibilityControls.appendChild(contrastBtn);
        
        // Adicionar controles ao corpo do documento
        document.body.appendChild(accessibilityControls);
    }
}

// Função para alterar o tamanho da fonte
function changeFontSize(direction) {
    const body = document.body;
    
    // Verificar o tamanho atual da fonte
    if (direction > 0) {
        if (body.classList.contains('font-size-larger')) {
            return; // Já está no tamanho máximo
        } else if (body.classList.contains('font-size-large')) {
            body.classList.remove('font-size-large');
            body.classList.add('font-size-larger');
        } else {
            body.classList.add('font-size-large');
        }
    } else {
        if (body.classList.contains('font-size-larger')) {
            body.classList.remove('font-size-larger');
            body.classList.add('font-size-large');
        } else if (body.classList.contains('font-size-large')) {
            body.classList.remove('font-size-large');
        } else {
            return; // Já está no tamanho mínimo
        }
    }
    
    // Salvar preferência no localStorage
    localStorage.setItem('fontSizePreference', body.className);
}

// Função para alternar o modo de alto contraste
function toggleContrast() {
    const body = document.body;
    
    if (body.classList.contains('high-contrast')) {
        body.classList.remove('high-contrast');
    } else {
        body.classList.add('high-contrast');
    }
    
    // Salvar preferência no localStorage
    localStorage.setItem('contrastPreference', body.classList.contains('high-contrast'));
}

// Função para inicializar formulários
function initForms() {
    // Formulário de cadastro
    const cadastroForm = document.getElementById('cadastro-form');
    if (cadastroForm) {
        cadastroForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validar formulário
            if (validateForm(cadastroForm)) {
                // Enviar dados por email (simulação)
                alert('Formulário enviado com sucesso! Em breve entraremos em contato.');
                cadastroForm.reset();
            }
        });
    }
    
    // Formulário de login administrativo
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Simulação de login (será substituído pelo backend)
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Simulação básica (será implementada no backend)
            if (email && password) {
                window.location.href = 'registroponto.html';
            } else {
                alert('E-mail ou Senha inválidos');
            }
        });
    }
    
    // Formulário de registro de ponto de coleta
    const registroForm = document.getElementById('registro-form');
    if (registroForm) {
        registroForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validar formulário
            if (validateForm(registroForm)) {
                // Simulação de registro (será implementado no backend)
                alert('Ponto de coleta registrado com sucesso!');
                registroForm.reset();
            }
        });
    }
}

// Função para validar formulários
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
    
    // Validar email se existir
    const emailField = form.querySelector('input[type="email"]');
    if (emailField && emailField.value.trim()) {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(emailField.value)) {
            isValid = false;
            emailField.classList.add('invalid');
            
            // Adicionar mensagem de erro se não existir
            let errorMsg = emailField.parentNode.querySelector('.error-message');
            if (!errorMsg) {
                errorMsg = document.createElement('div');
                errorMsg.className = 'error-message';
                errorMsg.style.color = 'red';
                errorMsg.style.fontSize = '0.8rem';
                errorMsg.style.marginTop = '5px';
                emailField.parentNode.appendChild(errorMsg);
            }
            errorMsg.textContent = 'Por favor, insira um e-mail válido';
        }
    }
    
    return isValid;
}

// Função para inicializar o mapa (será implementada com API do Google Maps)
function initMap() {
    // Verificar se o contêiner do mapa existe
    const mapContainer = document.querySelector('.map-container');
    if (!mapContainer) return;
    
    // Simulação de mapa (será substituído pela implementação real com Google Maps)
    mapContainer.innerHTML = '<div style="background-color: #e9ecef; height: 100%; display: flex; align-items: center; justify-content: center;"><p>Mapa será carregado aqui com a API do Google Maps</p></div>';
    
    // Implementação do campo de busca por CEP
    const searchInput = document.querySelector('.search-input');
    const searchButton = document.querySelector('.search-button');
    
    if (searchInput && searchButton) {
        searchButton.addEventListener('click', function() {
            const cep = searchInput.value.trim();
            if (cep) {
                searchCollectionPoints(cep);
            } else {
                alert('Por favor, insira um CEP válido');
            }
        });
        
        // Permitir busca ao pressionar Enter
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const cep = searchInput.value.trim();
                if (cep) {
                    searchCollectionPoints(cep);
                } else {
                    alert('Por favor, insira um CEP válido');
                }
            }
        });
    }
}

// Função para buscar pontos de coleta por CEP (simulação)
function searchCollectionPoints(cep) {
    // Simulação de busca (será implementada no backend)
    console.log(`Buscando pontos de coleta próximos ao CEP: ${cep}`);
    
    // Simulação de resultado
    alert(`Buscando pontos de coleta próximos ao CEP: ${cep}\nEsta funcionalidade será implementada com a API do Google Maps e o backend.`);
}

// Carregar preferências de acessibilidade salvas
window.addEventListener('load', function() {
    // Carregar tamanho da fonte
    const fontSizePreference = localStorage.getItem('fontSizePreference');
    if (fontSizePreference) {
        document.body.className = fontSizePreference;
    }
    
    // Carregar preferência de contraste
    const contrastPreference = localStorage.getItem('contrastPreference');
    if (contrastPreference === 'true') {
        document.body.classList.add('high-contrast');
    }
});
