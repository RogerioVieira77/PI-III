// Script para integração com Google Maps e funcionalidades de geolocalização

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
