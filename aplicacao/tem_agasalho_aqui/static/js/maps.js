let map;
let markers = [];

// Inicializa o mapa Google
function initMap() {
    // Centraliza inicialmente no Brasil
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: -23.5505, lng: -46.6333 }, // São Paulo como padrão
        zoom: 10,
    });
    
    // Adiciona o campo de busca se não existir
    if (!document.querySelector('.search-input')) {
        const searchContainer = document.querySelector('.search-container');
        searchContainer.innerHTML = `
            <input type="text" class="search-input" placeholder="Insira seu CEP" aria-label="Insira seu CEP">
            <button class="search-button">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
                </svg>
            </button>
        `;
    }
    
    // Configurar o evento de clique do botão de busca
    document.querySelector('.search-button').addEventListener('click', function() {
        const cep = document.querySelector('.search-input').value.trim();
        if (cep) {
            searchCollectionPoints(cep);
        } else {
            alert("Por favor, digite um CEP válido");
        }
    });
    
    // Permitir busca ao pressionar Enter no campo de busca
    document.querySelector('.search-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const cep = this.value.trim();
            if (cep) {
                searchCollectionPoints(cep);
            } else {
                alert("Por favor, digite um CEP válido");
            }
        }
    });
}

// Busca pontos de coleta pelo CEP usando a API
function searchCollectionPoints(cep) {
    // Limpar marcadores existentes
    clearMarkers();
    
    // Mostrar indicador de carregamento
    document.getElementById('collection-points-list').innerHTML = '<p>Buscando pontos próximos...</p>';
    
    // Fazer requisição à API
    fetch(`/api/pontos-coleta?cep=${cep}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erro na resposta: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Dados recebidos da API:", data); // Debug
            
            if (data.error) {
                document.getElementById('collection-points-list').innerHTML = 
                    `<p class="error-message">${data.error}</p>`;
                // Adicionar pop-up para erro de CEP
                alert("O CEP informado está incorreto ou não existe na base do Google Maps");
                return;
            }
            
            // Centralizar mapa na localização do CEP
            if (data.location) {
                map.setCenter({
                    lat: data.location.latitude, 
                    lng: data.location.longitude
                });
                map.setZoom(13);
            }
            
            // Mostrar pontos de coleta no mapa e na lista
            displayCollectionPoints(data.points || []);
        })
        .catch(error => {
            console.error('Erro detalhado:', error);
            document.getElementById('collection-points-list').innerHTML = 
                `<p class="error-message">CEP não encontrado ou inválido.</p>`;
            
            // Adicionar pop-up para erro na busca
            alert("O CEP informado está incorreto ou não existe na base do Google Maps");
        });
}

// Exibe os pontos de coleta no mapa e na lista
function displayCollectionPoints(points) {
    const listContainer = document.getElementById('collection-points-list');
    
    if (!points || points.length === 0) {
        listContainer.innerHTML = '<p>Nenhum ponto de coleta encontrado próximo a este CEP.</p>';
        return;
    }
    
    // Criar marcadores no mapa
    points.forEach(point => {
        const marker = new google.maps.Marker({
            position: { lat: point.latitude, lng: point.longitude },
            map: map,
            title: point.name
        });
        
        // Adicionar informações ao clicar no marcador
        const infoWindow = new google.maps.InfoWindow({
            content: `
                <div class="info-window">
                    <h3>${point.name}</h3>
                    <p>${point.address}</p>
                    <p>${point.phone}</p>
                </div>
            `
        });
        
        marker.addListener('click', () => {
            infoWindow.open(map, marker);
        });
        
        markers.push(marker);
    });
    
    // Criar lista de pontos
    let html = '<h2>Pontos de Coleta Encontrados</h2><div class="collection-points">';
    
    points.forEach(point => {
        html += `
            <div class="collection-point-card">
                <h3>${point.name}</h3>
                <p><strong>Endereço:</strong> ${point.address}, ${point.city}, ${point.state}</p>
                <p><strong>Telefone:</strong> ${point.phone}</p>
                <p><strong>Horário:</strong> ${point.opening_hours}</p>
                ${point.website ? `<p><strong>Website:</strong> <a href="${point.website}" target="_blank">${point.website}</a></p>` : ''}
                ${point.email ? `<p><strong>Email:</strong> <a href="mailto:${point.email}">${point.email}</a></p>` : ''}
                <p><strong>Distância:</strong> ${point.distance.toFixed(2)} km</p>
            </div>
        `;
    });
    
    html += '</div>';
    listContainer.innerHTML = html;
    
    // Adicionar estilo para os cards
    const style = document.createElement('style');
    style.textContent = `
        .collection-point-card {
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .collection-point-card h3 {
            margin-top: 0;
            color: var(--accent-color);
            border-bottom: 1px solid #eee;
            padding-bottom: 8px;
            margin-bottom: 12px;
        }
        .collection-point-card p {
            margin: 8px 0;
        }
        .collection-points {
            margin-bottom: 30px;
        }
    `;
    document.head.appendChild(style);
}

// Limpa todos os marcadores do mapa
function clearMarkers() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];
}