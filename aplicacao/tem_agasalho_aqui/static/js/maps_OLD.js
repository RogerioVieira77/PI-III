/*// Script para integração com Google Maps e funcionalidades de geolocalização

// Variável global para o mapa
let map;
let markers = [];
let infoWindow;

// Função para inicializar o mapa do Google
function initGoogleMap() {
    // Verificar se o contêiner do mapa existe
    const mapContainer = document.getElementById('map');
    if (!mapContainer) return;

    // Coordenadas iniciais (São Paulo, Brasil)
    const initialPosition = { lat: -23.5505, lng: -46.6333 };

    // Criar o mapa
    map = new google.maps.Map(mapContainer, {
        center: initialPosition,
        zoom: 12,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        mapTypeControl: true,
        streetViewControl: true,
        fullscreenControl: true
    });

    // Criar janela de informações
    infoWindow = new google.maps.InfoWindow();

    // Adicionar evento de clique no mapa
    map.addListener('click', function() {
        infoWindow.close();
    });

    // Tentar obter a localização atual do usuário
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };

                // Centralizar o mapa na localização do usuário
                map.setCenter(userLocation);

                // Adicionar marcador na localização do usuário
                const userMarker = new google.maps.Marker({
                    position: userLocation,
                    map: map,
                    title: 'Sua localização',
                    icon: {
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 10,
                        fillColor: '#4285F4',
                        fillOpacity: 1,
                        strokeColor: '#FFFFFF',
                        strokeWeight: 2
                    }
                });

                // Buscar pontos de coleta próximos à localização do usuário
                reverseGeocode(userLocation.lat, userLocation.lng);
            },
            function() {
                // Caso o usuário não permita compartilhar a localização
                console.log('Usuário não permitiu compartilhar a localização');
            }
        );
    }

    // Configurar o campo de busca
    setupSearchField();
}

// Função para configurar o campo de busca por CEP
function setupSearchField() {
    const searchInput = document.querySelector('.search-input');
    const searchButton = document.querySelector('.search-button');

    if (!searchInput || !searchButton) return;

    // Adicionar evento de clique no botão de busca
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

// Função para buscar pontos de coleta por CEP
function searchCollectionPoints(cep) {
    // Limpar CEP (remover caracteres não numéricos)
    cep = cep.replace(/\D/g, '');

    // Validar formato do CEP
    if (cep.length !== 8) {
        alert('Por favor, insira um CEP válido com 8 dígitos');
        return;
    }

    // Exibir indicador de carregamento
    const mapContainer = document.getElementById('map');
    if (mapContainer) {
        mapContainer.innerHTML = '<div class="loading-indicator">Buscando pontos de coleta...</div>';
    }

    // Fazer requisição à API
    fetch(`/api/pontos-coleta?cep=${cep}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao buscar pontos de coleta');
            }
            return response.json();
        })
        .then(data => {
            // Reinicializar o mapa
            initGoogleMap();

            // Centralizar o mapa na localização do CEP
            const cepLocation = {
                lat: data.latitude,
                lng: data.longitude
            };
            map.setCenter(cepLocation);

            // Adicionar marcador na localização do CEP
            const cepMarker = new google.maps.Marker({
                position: cepLocation,
                map: map,
                title: `CEP: ${cep}`,
                icon: {
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 10,
                    fillColor: '#4285F4',
                    fillOpacity: 1,
                    strokeColor: '#FFFFFF',
                    strokeWeight: 2
                }
            });

            // Adicionar marcadores para os pontos de coleta
            data.pontos_coleta.forEach(ponto => {
                addCollectionPointMarker(ponto);
            });

            // Ajustar o zoom para mostrar todos os marcadores
            if (markers.length > 0) {
                const bounds = new google.maps.LatLngBounds();
                markers.forEach(marker => {
                    bounds.extend(marker.getPosition());
                });
                bounds.extend(cepLocation);
                map.fitBounds(bounds);
            }

            // Atualizar a lista de pontos de coleta
            updateCollectionPointsList(data.pontos_coleta);
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Não foi possível buscar pontos de coleta para este CEP. Por favor, tente novamente.');
            
            // Reinicializar o mapa em caso de erro
            initGoogleMap();
        });
}

// Função para adicionar marcador de ponto de coleta no mapa
function addCollectionPointMarker(ponto) {
    const position = {
        lat: ponto.latitude,
        lng: ponto.longitude
    };

    const marker = new google.maps.Marker({
        position: position,
        map: map,
        title: ponto.nickname,
        icon: {
            url: 'static/images/HeartBoxlogo.png',
            scaledSize: new google.maps.Size(30, 30)
        },
        animation: google.maps.Animation.DROP
    });

    // Conteúdo da janela de informações
    const contentString = `
        <div class="info-window">
            <h3>${ponto.nickname}</h3>
            <p><strong>Endereço:</strong> ${ponto.address}</p>
            <p><strong>Telefone:</strong> ${ponto.phone}</p>
            <p><strong>Horário:</strong> ${ponto.opening_hours}</p>
            ${ponto.website ? `<p><strong>Site:</strong> <a href="${ponto.website}" target="_blank">${ponto.website}</a></p>` : ''}
            ${ponto.observations ? `<p><strong>Observações:</strong> ${ponto.observations}</p>` : ''}
            <p><strong>Distância:</strong> ${ponto.distance.toFixed(2)} km</p>
            <a href="https://www.google.com/maps/dir/?api=1&destination=${ponto.latitude},${ponto.longitude}" target="_blank" class="directions-link">Como chegar</a>
        </div>
    `;

    // Adicionar evento de clique no marcador
    marker.addListener('click', function() {
        infoWindow.setContent(contentString);
        infoWindow.open(map, marker);
    });

    // Adicionar marcador à lista de marcadores
    markers.push(marker);

    return marker;
}

// Função para atualizar a lista de pontos de coleta na página
function updateCollectionPointsList(pontos) {
    const listContainer = document.getElementById('collection-points-list');
    if (!listContainer) return;

    // Limpar lista atual
    listContainer.innerHTML = '';

    // Verificar se há pontos de coleta
    if (pontos.length === 0) {
        listContainer.innerHTML = '<p class="no-results">Nenhum ponto de coleta encontrado próximo a este CEP.</p>';
        return;
    }

    // Criar título da lista
    const listTitle = document.createElement('h2');
    listTitle.className = 'list-title';
    listTitle.textContent = 'Pontos de Coleta Encontrados';
    listContainer.appendChild(listTitle);

    // Criar lista de pontos
    const list = document.createElement('div');
    list.className = 'collection-points-list';

    // Adicionar cada ponto à lista
    pontos.forEach((ponto, index) => {
        const pointItem = document.createElement('div');
        pointItem.className = 'collection-point-item';
        pointItem.innerHTML = `
            <h3>${ponto.nickname}</h3>
            <p><strong>Endereço:</strong> ${ponto.address}</p>
            <p><strong>Telefone:</strong> ${ponto.phone}</p>
            <p><strong>Horário:</strong> ${ponto.opening_hours}</p>
            ${ponto.website ? `<p><strong>Site:</strong> <a href="${ponto.website}" target="_blank">${ponto.website}</a></p>` : ''}
            <p><strong>Distância:</strong> ${ponto.distance.toFixed(2)} km</p>
            <button class="show-on-map-btn" data-index="${index}">Ver no mapa</button>
            <a href="https://www.google.com/maps/dir/?api=1&destination=${ponto.latitude},${ponto.longitude}" target="_blank" class="directions-link">Como chegar</a>
        `;

        // Adicionar evento de clique no botão "Ver no mapa"
        pointItem.querySelector('.show-on-map-btn').addEventListener('click', function() {
            const markerIndex = parseInt(this.getAttribute('data-index'));
            if (markers[markerIndex]) {
                // Centralizar o mapa no marcador
                map.setCenter(markers[markerIndex].getPosition());
                map.setZoom(15);
                
                // Abrir a janela de informações
                google.maps.event.trigger(markers[markerIndex], 'click');
                
                // Rolar a página até o mapa
                document.getElementById('map').scrollIntoView({ behavior: 'smooth' });
            }
        });

        list.appendChild(pointItem);
    });

    listContainer.appendChild(list);
}

// Função para fazer geocodificação reversa (coordenadas para endereço)
function reverseGeocode(lat, lng) {
    // Usar a API do Nominatim para obter o endereço a partir das coordenadas
    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`, {
        headers: {
            'User-Agent': 'AgasalhoAqui/1.0'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Extrair o CEP do resultado
        let postalCode = '';
        if (data.address && data.address.postcode) {
            postalCode = data.address.postcode.replace(/\D/g, '');
        }

        // Se encontrou um CEP, buscar pontos de coleta
        if (postalCode) {
            const searchInput = document.querySelector('.search-input');
            if (searchInput) {
                searchInput.value = postalCode;
            }
            searchCollectionPoints(postalCode);
        }
    })
    .catch(error => {
        console.error('Erro na geocodificação reversa:', error);
    });
}

// Inicializar o mapa quando a API do Google Maps estiver carregada
function initMap() {
    // Esta função será chamada pela API do Google Maps quando estiver carregada
    initGoogleMap();
}

// Adicionar evento para inicializar o mapa quando a página for carregada
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se estamos na página de pontos de coleta
    if (document.querySelector('.map-container')) {
        // Se a API do Google Maps já estiver carregada
        if (typeof google !== 'undefined' && typeof google.maps !== 'undefined') {
            initGoogleMap();
        }
        // Caso contrário, a função initMap será chamada quando a API for carregada
    }
});

let map;
let markers = [];

// Inicializa o mapa Google
function initMap() {
    // Centraliza inicialmente no Brasil
    map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: -23.5505, lng: -46.6333 }, // São Paulo como padrão
        zoom: 10,
    });
    
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
                throw new Error('Erro na busca de pontos de coleta');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                document.getElementById('collection-points-list').innerHTML = 
                    `<p class="error-message">${data.error}</p>`;
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
            displayCollectionPoints(data.points);
        })
        .catch(error => {
            console.error('Erro:', error);
            document.getElementById('collection-points-list').innerHTML = 
                '<p class="error-message">Erro ao buscar pontos de coleta. Tente novamente mais tarde.</p>';
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
            </div>
        `;
    });
    
    html += '</div>';
    listContainer.innerHTML = html;
}

// Limpa todos os marcadores do mapa
function clearMarkers() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];
}
*/

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
                `<p class="error-message">Erro ao buscar pontos de coleta: ${error.message}</p>`;
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
        console.log("Adicionando marcador:", point.latitude, point.longitude); // Debug
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
                <h3>${point.name || 'Nome não disponível'}</h3>
                <p><strong>Endereço:</strong> ${point.address || 'Não disponível'}</p>
                <p><strong>Telefone:</strong> ${point.phone || 'Não disponível'}</p>
                <p><strong>Horário:</strong> ${point.opening_hours || 'Não disponível'}</p>
                ${point.website ? `<p><strong>Website:</strong> <a href="${point.website}" target="_blank">${point.website}</a></p>` : ''}
                ${point.email ? `<p><strong>Email:</strong> <a href="mailto:${point.email}">${point.email}</a></p>` : ''}
            </div>
        `;
    });
    
    html += '</div>';
    listContainer.innerHTML = html;
}

// Limpa todos os marcadores do mapa
function clearMarkers() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];
}