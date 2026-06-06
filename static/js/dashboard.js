/**
 * Jogja Smart Guide — Dashboard JS
 * Renders destination cards, fetches weather data, handles search/filter/sort
 */

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
});


let allDestinations = [];
let userLocation = null;
let modalMap = null; // Leaflet map instance for modal routing

function escapeHTML(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of the Earth in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c;
    return distance;
}

function initDashboard() {
    // DESTINATIONS_DATA is injected from the template
    if (typeof DESTINATIONS_DATA === 'undefined') return;

    allDestinations = [...DESTINATIONS_DATA];

    // Default fallback Jogja Center (Malioboro)
    userLocation = {
        latitude: -7.7929,
        longitude: 110.3658,
        isExact: false
    };

    // Render cards instantly using the cached weather data from backend
    renderCards(allDestinations);

    // Initial load of user location & distance calculations (OSRM Table API)
    refreshJarakDanLokasi();

    // Auto-refresh location and distance every 10 minutes
    setInterval(refreshJarakDanLokasi, 10 * 60 * 1000);

    // Bind manually triggered refresh button
    const refreshBtn = document.getElementById('refresh-distance-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshJarakDanLokasi);
    }

    initSearchFilter();
    initModalEvents();
}




/**
 * Render destination cards to the grid
 */
function renderCards(destinations) {
    const grid = document.getElementById('cards-grid');
    const emptyState = document.getElementById('empty-state');
    if (!grid) return;

    // Clear grid securely
    while (grid.firstChild) {
        grid.removeChild(grid.firstChild);
    }

    if (destinations.length === 0) {
        if (emptyState) emptyState.style.display = 'block';
        return;
    }

    if (emptyState) emptyState.style.display = 'none';

    destinations.forEach((dest, index) => {
        const card = document.createElement('div');
        card.className = 'dest-card animate-fade-in-up';
        card.style.animationDelay = `${index * 0.05}s`;
        card.setAttribute('data-id', dest.id);

        // Image container
        const cardImage = document.createElement('div');
        cardImage.className = 'dest-card-image';

        const img = document.createElement('img');
        img.src = dest.photo_url;
        img.alt = dest.name;
        img.loading = 'lazy';
        img.onerror = function() {
            this.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="220"><rect fill="%23E2E8F0" width="400" height="220"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%2394A3B8" font-family="sans-serif" font-size="16">No Image</text></svg>';
        };
        cardImage.appendChild(img);

        const categorySpan = document.createElement('span');
        categorySpan.className = 'dest-card-category';
        
        const categoryIconSpan = document.createElement('span');
        categoryIconSpan.className = 'material-icons card-category-icon';
        categoryIconSpan.textContent = getCategoryIcon(dest.category);
        
        categorySpan.appendChild(categoryIconSpan);
        categorySpan.appendChild(document.createTextNode(' ' + dest.category));
        cardImage.appendChild(categorySpan);

        const ratingSpan = document.createElement('span');
        ratingSpan.className = 'dest-card-rating';
        
        const ratingIconSpan = document.createElement('span');
        ratingIconSpan.className = 'material-icons star-icon';
        ratingIconSpan.textContent = 'star';
        
        ratingSpan.appendChild(ratingIconSpan);
        ratingSpan.appendChild(document.createTextNode(' ' + dest.rating.toFixed(1)));
        cardImage.appendChild(ratingSpan);

        card.appendChild(cardImage);

        // Body container
        const cardBody = document.createElement('div');
        cardBody.className = 'dest-card-body';

        const title = document.createElement('h3');
        title.className = 'dest-card-name';
        title.textContent = dest.name;
        cardBody.appendChild(title);

        // Badge row (Similarity & Recommendation Score)
        const badgeRow = document.createElement('div');
        badgeRow.className = 'badge-row';

        const simVal = dest.cosine_similarity !== undefined ? dest.cosine_similarity : 0.0;
        const simPercent = Math.round(((simVal + 1.0) / 2.0) * 100);
        const simBadge = document.createElement('span');
        simBadge.className = 'badge-similarity';
        simBadge.title = "Kecocokan DNA wisata dengan preferensi minat Anda";
        
        const simIcon = document.createElement('span');
        simIcon.className = 'material-icons';
        simIcon.style.fontSize = '14px';
        simIcon.textContent = 'favorite';
        simBadge.appendChild(simIcon);
        simBadge.appendChild(document.createTextNode(` Kecocokan: ${simPercent}%`));
        badgeRow.appendChild(simBadge);

        const recVal = dest.recommendation_score !== undefined ? dest.recommendation_score : 50.0;
        const recBadge = document.createElement('span');
        recBadge.className = 'badge-recommendation';
        recBadge.title = "Skor Rekomendasi Pintar (Fuzzy Tahap 2)";
        
        const recIcon = document.createElement('span');
        recIcon.className = 'material-icons';
        recIcon.style.fontSize = '14px';
        recIcon.textContent = 'auto_awesome';
        recBadge.appendChild(recIcon);
        recBadge.appendChild(document.createTextNode(` Skor: ${recVal.toFixed(1)}`));
        badgeRow.appendChild(recBadge);

        cardBody.appendChild(badgeRow);

        const desc = document.createElement('p');
        desc.className = 'dest-card-desc';
        desc.textContent = dest.description;
        cardBody.appendChild(desc);

        // Weather widget container
        const weatherContainer = document.createElement('div');
        weatherContainer.className = 'weather-widget';
        weatherContainer.id = `weather-${dest.id}`;

        const rainVal = dest.weather ? dest.weather.rain_1h : 0;
        const tempVal = dest.weather ? dest.weather.temp : 27;
        const cloudsVal = dest.weather ? dest.weather.clouds_all : 50;
        const windVal = dest.weather ? dest.weather.wind_speed : 2;

        const rainText = `${rainVal} mm`;
        const tempText = `${typeof tempVal === 'number' ? tempVal.toFixed(1) : tempVal}°C`;
        const cloudsText = `${cloudsVal}%`;
        const windText = `${typeof windVal === 'number' ? windVal.toFixed(1) : windVal} m/s`;

        const weatherParams = [
            { icon: 'water_drop', val: rainText, label: 'Hujan' },
            { icon: 'thermostat', val: tempText, label: 'Suhu' },
            { icon: 'cloud', val: cloudsText, label: 'Awan' },
            { icon: 'air', val: windText, label: 'Angin' }
        ];

        weatherParams.forEach(param => {
            const item = document.createElement('div');
            item.className = 'weather-item';

            const wIconDiv = document.createElement('div');
            wIconDiv.className = 'weather-icon';
            const wIconSpan = document.createElement('span');
            wIconSpan.className = 'material-icons weather-icon-mi';
            wIconSpan.textContent = param.icon;
            wIconDiv.appendChild(wIconSpan);
            item.appendChild(wIconDiv);

            const wValue = document.createElement('div');
            wValue.className = 'weather-value';
            wValue.textContent = param.val;
            item.appendChild(wValue);

            const wLabel = document.createElement('div');
            wLabel.className = 'weather-label';
            wLabel.textContent = param.label;
            item.appendChild(wLabel);

            weatherContainer.appendChild(item);
        });

        cardBody.appendChild(weatherContainer);

        // Distance container (always rendered for all users)
        if (userLocation) {
            const distVal = dest.calculated_distance !== undefined 
                ? dest.calculated_distance 
                : calculateDistance(userLocation.latitude, userLocation.longitude, dest.latitude, dest.longitude);
            const distType = dest.distance_type || 'haversine';
            
            const distanceContainer = document.createElement('div');
            distanceContainer.className = 'dest-card-distance';
            
            const distanceIconSpan = document.createElement('span');
            distanceIconSpan.className = 'material-icons distance-icon';
            distanceIconSpan.textContent = 'near_me';
            distanceContainer.appendChild(distanceIconSpan);
            
            const labelText = userLocation.isExact 
                ? `Jarak (${distType === 'osrm' ? 'Rute OSRM' : 'Garis Lurus'}): ${distVal.toFixed(1)} km`
                : `Jarak dari Pusat Kota (Malioboro): ${distVal.toFixed(1)} km`;
                
            distanceContainer.appendChild(document.createTextNode(labelText));
            cardBody.appendChild(distanceContainer);
        }

        // Footer container
        const cardFooter = document.createElement('div');
        cardFooter.className = 'dest-card-footer';

        const priceDiv = document.createElement('div');
        priceDiv.className = 'dest-card-price';
        
        const priceLabelSpan = document.createElement('span');
        priceLabelSpan.className = 'price-label';
        priceLabelSpan.textContent = 'Harga Tiket';
        
        priceDiv.appendChild(priceLabelSpan);
        priceDiv.appendChild(document.createTextNode(' ' + formatRupiah(dest.price)));
        cardFooter.appendChild(priceDiv);

        const detailBtn = document.createElement('span');
        detailBtn.className = 'dest-card-detail-btn';
        detailBtn.textContent = 'Lihat Detail →';
        cardFooter.appendChild(detailBtn);

        cardBody.appendChild(cardFooter);
        card.appendChild(cardBody);

        grid.appendChild(card);
    });
}


/**
 * Get category Google Material Icon
 */
function getCategoryIcon(category) {
    let iconName = 'place';
    switch (category) {
        case 'Alam':
            iconName = 'terrain';
            break;
        case 'Budaya':
            iconName = 'theater_comedy';
            break;
        case 'Kuliner':
            iconName = 'restaurant';
            break;
        case 'Keramaian':
            iconName = 'groups';
            break;
        case 'Petualangan':
            iconName = 'directions_run';
            break;
    }
    return iconName;
}

/**
 * Fetch weather for the user's location and update the top card
 */
async function fetchUserWeather(lat, lon, isExact) {
    const tempEl = document.getElementById('user-weather-temp');
    const rainEl = document.getElementById('user-weather-rain');
    const cloudsEl = document.getElementById('user-weather-clouds');
    const windEl = document.getElementById('user-weather-wind');
    const locationEl = document.getElementById('user-weather-location');

    try {
        const response = await fetch(`/api/weather?lat=${lat}&lon=${lon}`);
        const data = await response.json();

        const rainVal = data.rain && data.rain['1h'] ? data.rain['1h'] : 0;
        const tempVal = data.main ? data.main.temp : '-';
        const cloudsVal = data.clouds ? data.clouds.all : '-';
        const windVal = data.wind ? data.wind.speed : '-';

        if (tempEl) tempEl.textContent = `${typeof tempVal === 'number' ? tempVal.toFixed(1) : tempVal}°C`;
        if (rainEl) rainEl.textContent = `${rainVal} mm`;
        if (cloudsEl) cloudsEl.textContent = `${cloudsVal}%`;
        if (windEl) windEl.textContent = `${typeof windVal === 'number' ? windVal.toFixed(1) : windVal} m/s`;

        if (locationEl) {
            if (isExact) {
                locationEl.textContent = `Lokasi Anda saat ini (${lat.toFixed(4)}, ${lon.toFixed(4)})`;
            } else {
                locationEl.textContent = `Pusat Kota (Malioboro, Yogyakarta)`;
            }
        }
    } catch (error) {
        console.error("Gagal mengambil data cuaca pengguna:", error);
        if (locationEl) {
            locationEl.textContent = "Gagal memuat cuaca lokasi Anda";
        }
    }
}

/**
 * Fetch OSRM road distances for all destinations at once using Table Service
 */
async function fetchOSRMDistances(userLat, userLon) {
    if (!allDestinations.length) return;

    // OSRM Table URL: user coordinate followed by all destinations coordinates
    const coords = [`${userLon},${userLat}`];
    allDestinations.forEach(dest => {
        coords.push(`${dest.longitude},${dest.latitude}`);
    });

    const url = `https://router.project-osrm.org/table/v1/driving/${coords.join(';')}?sources=0&annotations=distance`;

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.code === 'Ok' && data.distances && data.distances[0]) {
            const distancesFromUser = data.distances[0];

            allDestinations.forEach((dest, idx) => {
                const meters = distancesFromUser[idx + 1]; // First coordinate in URL is user, so idx + 1
                if (meters !== null && meters !== undefined) {
                    dest.calculated_distance = meters / 1000.0;
                    dest.distance_type = 'osrm';
                } else {
                    dest.calculated_distance = calculateDistance(userLat, userLon, dest.latitude, dest.longitude);
                    dest.distance_type = 'haversine';
                }
            });
        } else {
            throw new Error("OSRM table response code not Ok");
        }
    } catch (error) {
        console.warn("OSRM Table API failed, falling back to Haversine straight-line distances:", error);
        allDestinations.forEach(dest => {
            dest.calculated_distance = calculateDistance(userLat, userLon, dest.latitude, dest.longitude);
            dest.distance_type = 'haversine';
        });
    }
}

/**
 * Refresh user coordinates and recalculate OSRM/Haversine distances
 */
async function refreshJarakDanLokasi() {
    const refreshBtn = document.getElementById('refresh-distance-btn');
    if (refreshBtn) {
        refreshBtn.classList.add('rotating');
        refreshBtn.disabled = true;
        const label = refreshBtn.querySelector('span:not(.material-icons)');
        if (label) label.textContent = 'Memperbarui...';
    }

    const handleLocation = async (lat, lon, isExact) => {
        userLocation = { latitude: lat, longitude: lon, isExact: isExact };

        // Update user weather widget
        fetchUserWeather(lat, lon, isExact);

        // Calculate road distances using OSRM Table API
        await fetchOSRMDistances(lat, lon);

        // Fetch recommendations and similarity scores from backend based on calculated distances
        try {
            const payload = {
                lat: lat,
                lon: lon,
                distances: allDestinations.map(d => ({
                    id: d.id,
                    distance: d.calculated_distance !== undefined ? d.calculated_distance : calculateDistance(lat, lon, d.latitude, d.longitude)
                }))
            };
            const response = await fetch('/api/recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            if (response.ok) {
                const recommendedDestinations = await response.json();
                recommendedDestinations.forEach(rec => {
                    const dest = allDestinations.find(d => d.id === rec.id);
                    if (dest) {
                        dest.cosine_similarity = rec.cosine_similarity;
                        dest.recommendation_score = rec.recommendation_score;
                        dest.calculated_distance = rec.calculated_distance;
                    }
                });
            } else {
                console.error("Gagal mendapatkan rekomendasi dari server, response status:", response.status);
            }
        } catch (error) {
            console.error("Gagal memperbarui rekomendasi dari server:", error);
        }

        // Apply filters and re-sort destinations
        applyFilters();

        resetRefreshBtn();
    };

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            async (position) => {
                await handleLocation(position.coords.latitude, position.coords.longitude, true);
            },
            async (error) => {
                console.warn("GPS access denied, using Malioboro fallback:", error);
                await handleLocation(-7.7929, 110.3658, false);
            },
            { enableHighAccuracy: true, timeout: 6000 }
        );
    } else {
        await handleLocation(-7.7929, 110.3658, false);
    }
}

function resetRefreshBtn() {
    const refreshBtn = document.getElementById('refresh-distance-btn');
    if (refreshBtn) {
        refreshBtn.classList.remove('rotating');
        refreshBtn.disabled = false;
        const label = refreshBtn.querySelector('span:not(.material-icons)');
        if (label) label.textContent = 'Perbarui Jarak';
    }
}

/**
 * Initialize Leaflet map and plot route using OSRM route service
 */
async function initModalMap(dest) {
    const mapContainer = document.getElementById('modal-route-map');
    if (!mapContainer) return;

    // Destroy previous map instance if it exists
    if (modalMap) {
        modalMap.remove();
        modalMap = null;
    }

    const destLat = dest.latitude;
    const destLon = dest.longitude;
    const userLat = userLocation ? userLocation.latitude : -7.7929;
    const userLon = userLocation ? userLocation.longitude : 110.3658;
    const isExact = userLocation ? userLocation.isExact : false;

    // Initialize Leaflet Map
    modalMap = L.map('modal-route-map').setView([destLat, destLon], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(modalMap);

    // Destination Marker
    L.marker([destLat, destLon]).addTo(modalMap)
        .bindPopup(`<b>${escapeHTML(dest.name)}</b><br>Tujuan Wisata`)
        .openPopup();

    // User Marker
    const userLabel = isExact ? "Lokasi Anda saat ini" : "Pusat Kota (Malioboro) - Fallback";
    L.marker([userLat, userLon]).addTo(modalMap)
        .bindPopup(`<b>${userLabel}</b>`);

    const routePoints = [
        [userLat, userLon],
        [destLat, destLon]
    ];
    let bounds = L.latLngBounds(routePoints);

    // Fetch actual route shape from OSRM Route API
    const routeUrl = `https://router.project-osrm.org/route/v1/driving/${userLon},${userLat};${destLon},${destLat}?overview=full&geometries=geojson`;

    try {
        const response = await fetch(routeUrl);
        const data = await response.json();

        if (data.code === 'Ok' && data.routes && data.routes[0]) {
            const routeGeom = data.routes[0].geometry;

            // Draw actual road route
            const routePath = L.geoJSON(routeGeom, {
                style: {
                    color: '#0D9488',
                    weight: 5,
                    opacity: 0.8
                }
            }).addTo(modalMap);

            bounds = routePath.getBounds();
        } else {
            throw new Error("OSRM Routing response code not Ok");
        }
    } catch (error) {
        console.warn("OSRM Route API failed, rendering straight line fallback:", error);

        // Draw straight line fallback
        const fallbackLine = L.polyline(routePoints, {
            color: '#0D9488',
            weight: 4,
            opacity: 0.8,
            dashArray: '10, 10'
        }).addTo(modalMap);

        bounds = fallbackLine.getBounds();
    }

    modalMap.fitBounds(bounds, { padding: [40, 40] });

    // Call invalidateSize after transition animation completes to fix gray tile sizing issues
    setTimeout(() => {
        if (modalMap) {
            modalMap.invalidateSize();
        }
    }, 300);
}


/**
 * Initialize search, filter, and sort functionality
 */
function initSearchFilter() {
    const searchInput = document.getElementById('search-input');
    const filterCategory = document.getElementById('filter-category');
    const sortBy = document.getElementById('sort-by');

    if (searchInput) {
        searchInput.addEventListener('input', debounce(applyFilters, 300));
    }
    if (filterCategory) {
        filterCategory.addEventListener('change', applyFilters);
    }
    if (sortBy) {
        sortBy.addEventListener('change', applyFilters);
    }
}


/**
 * Apply search, filter, and sort to the destination list
 */
function applyFilters() {
    const searchTerm = (document.getElementById('search-input')?.value || '').toLowerCase().trim();
    const category = document.getElementById('filter-category')?.value || '';
    const sortType = document.getElementById('sort-by')?.value || 'recommendation';

    let filtered = [...allDestinations];

    // Search filter
    if (searchTerm) {
        filtered = filtered.filter(d =>
            d.name.toLowerCase().includes(searchTerm) ||
            d.description.toLowerCase().includes(searchTerm) ||
            d.category.toLowerCase().includes(searchTerm)
        );
    }

    // Category filter
    if (category) {
        filtered = filtered.filter(d => d.category === category);
    }

    // Sort
    switch (sortType) {
        case 'recommendation':
            filtered.sort((a, b) => (b.recommendation_score || 0) - (a.recommendation_score || 0));
            break;
        case 'rating':
            filtered.sort((a, b) => b.rating - a.rating);
            break;
        case 'price-low':
            filtered.sort((a, b) => a.price - b.price);
            break;
        case 'price-high':
            filtered.sort((a, b) => b.price - a.price);
            break;
        case 'name':
            filtered.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case 'random':
        default:
            // Fisher-Yates shuffle with safe temporary variable
            for (let i = filtered.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                const tempVal = filtered[i];
                filtered[i] = filtered[j];
                filtered[j] = tempVal;
            }
            break;
    }

    renderCards(filtered);
}


/**
 * Debounce utility
 */
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}


/**
 * Modal Initialization & Handling
 */
function initModalEvents() {
    const grid = document.getElementById('cards-grid');
    if (grid) {
        grid.addEventListener('click', (e) => {
            const card = e.target.closest('.dest-card');
            if (!card) return;
            
            const destId = parseInt(card.getAttribute('data-id'));
            const dest = allDestinations.find(d => d.id === destId);
            if (dest) {
                openDetailModal(dest);
            }
        });
    }

    // Close on overlay click
    const modal = document.getElementById('detail-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target.id === 'detail-modal') {
                closeDetailModal();
            }
        });
    }

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeDetailModal();
        }
    });
}

function openDetailModal(dest) {
    const modal = document.getElementById('detail-modal');
    if (!modal) return;

    // Populate basic fields
    document.getElementById('modal-img').src = dest.photo_url;
    document.getElementById('modal-img').alt = dest.name;
    document.getElementById('modal-cat').textContent = dest.category;
    document.getElementById('modal-title').textContent = dest.name;
    document.getElementById('modal-rating').textContent = dest.rating.toFixed(1);
    document.getElementById('modal-price').textContent = formatRupiah(dest.price);
    document.getElementById('modal-desc').textContent = dest.description;

    // Populate distance in modal if logged in
    const modalDistanceSection = document.getElementById('modal-distance-section');
    const modalDistanceBox = document.getElementById('modal-distance-box');
    if (modalDistanceSection && modalDistanceBox) {
        if (userLocation) {
            const distVal = dest.calculated_distance !== undefined 
                ? dest.calculated_distance 
                : calculateDistance(userLocation.latitude, userLocation.longitude, dest.latitude, dest.longitude);
            const distType = dest.distance_type || 'haversine';
            
            while (modalDistanceBox.firstChild) {
                modalDistanceBox.removeChild(modalDistanceBox.firstChild);
            }
            
            const distanceIconSpan = document.createElement('span');
            distanceIconSpan.className = 'material-icons distance-icon';
            distanceIconSpan.textContent = 'near_me';
            modalDistanceBox.appendChild(distanceIconSpan);
            
            const labelText = userLocation.isExact 
                ? `Jarak (${distType === 'osrm' ? 'Rute OSRM' : 'Garis Lurus'}): ${distVal.toFixed(1)} km`
                : `Jarak dari Pusat Kota (Malioboro): ${distVal.toFixed(1)} km`;
                
            modalDistanceBox.appendChild(document.createTextNode(labelText));
            modalDistanceSection.style.display = 'block';
        } else {
            modalDistanceSection.style.display = 'none';
        }
    }

    // Load routing map in detail modal
    initModalMap(dest);

    // Populate weather widget in modal safely
    const weatherWidget = document.getElementById('modal-weather-widget');
    const originalWeather = document.getElementById(`weather-${dest.id}`);
    if (weatherWidget && originalWeather) {
        while (weatherWidget.firstChild) {
            weatherWidget.removeChild(weatherWidget.firstChild);
        }
        Array.from(originalWeather.childNodes).forEach(node => {
            weatherWidget.appendChild(node.cloneNode(true));
        });

        // Populate weather index in modal
        let indexSection = document.getElementById('modal-weather-index-section');
        if (!indexSection) {
            indexSection = document.createElement('div');
            indexSection.id = 'modal-weather-index-section';
            indexSection.style.marginTop = 'var(--space-3)';
            indexSection.style.display = 'flex';
            indexSection.style.alignItems = 'center';
            indexSection.style.gap = 'var(--space-2)';
            indexSection.style.padding = 'var(--space-3)';
            indexSection.style.borderRadius = 'var(--radius-lg)';
            indexSection.style.fontSize = 'var(--text-sm)';
            indexSection.style.fontWeight = '600';

            const parentSection = weatherWidget.parentNode;
            parentSection.appendChild(indexSection);
        }

        const wIndex = dest.weather ? dest.weather.weather_index : 0.5;
        let indexLabel = '';
        let indexColor = '';
        let indexBg = '';
        let indexIcon = '';

        if (wIndex >= 0.6) {
            indexLabel = 'Cuaca Sangat Mendukung (Baik)';
            indexColor = 'var(--color-success)';
            indexBg = 'rgba(16, 185, 129, 0.1)';
            indexIcon = 'check_circle';
        } else if (wIndex > 0.4) {
            indexLabel = 'Cuaca Cukup Mendukung (Cukup)';
            indexColor = 'var(--color-warning)';
            indexBg = 'rgba(245, 158, 11, 0.1)';
            indexIcon = 'info';
        } else {
            indexLabel = 'Cuaca Kurang Mendukung (Buruk)';
            indexColor = 'var(--color-error)';
            indexBg = 'rgba(239, 68, 68, 0.1)';
            indexIcon = 'warning';
        }

        indexSection.style.color = indexColor;
        indexSection.style.backgroundColor = indexBg;
        indexSection.style.border = `1px solid ${indexColor}`;
        indexSection.innerHTML = '';

        const iconSpan = document.createElement('span');
        iconSpan.className = 'material-icons';
        iconSpan.style.fontSize = '20px';
        iconSpan.textContent = indexIcon;
        indexSection.appendChild(iconSpan);

        const textSpan = document.createElement('span');
        textSpan.textContent = `${indexLabel} — Skor FIS: ${wIndex.toFixed(2)}`;
        indexSection.appendChild(textSpan);
    }

    // Populate Nature
    const scoreNatureVisual = document.getElementById('score-nature-visual');
    const txtNatureVisual = document.getElementById('txt-nature-visual');
    if (scoreNatureVisual && txtNatureVisual) {
        const visualScore = dest.nature_visual || 3;
        scoreNatureVisual.style.width = (visualScore * 20) + '%';
        
        let labelText = `${visualScore}/5`;
        switch (visualScore) {
            case 1:
                labelText = 'Hampir seluruh area berupa bangunan/jalan/beton (1/5)';
                break;
            case 2:
                labelText = 'Unsur alam sangat sedikit (2/5)';
                break;
            case 3:
                labelText = 'Unsur alami dan buatan relatif seimbang (3/5)';
                break;
            case 4:
                labelText = 'Unsur alami lebih dominan (4/5)';
                break;
            case 5:
                labelText = 'Hampir seluruh area berupa unsur alami (5/5)';
                break;
        }
        txtNatureVisual.textContent = labelText;
    }
    
    populateTags('tags-nature-act', dest.nature_activities);
    populateTags('tags-nature-elem', dest.nature_elements);

    // Populate Crowd
    const txtCrowdReview = document.getElementById('score-crowd-review');
    const txtCrowdRating = document.getElementById('score-crowd-rating');
    const txtCrowdHashtag = document.getElementById('score-crowd-hashtag');
    
    if (txtCrowdReview) txtCrowdReview.textContent = `${dest.crowd_review_count || 1}/5`;
    if (txtCrowdRating) txtCrowdRating.textContent = `${dest.crowd_rating || 3}/5`;
    if (txtCrowdHashtag) txtCrowdHashtag.textContent = `${dest.crowd_hashtag || 1}/5`;
    
    populateTags('tags-crowd-act', dest.crowd_activities);
    populateTags('tags-crowd-fac', dest.crowd_facilities);

    // Populate Culinary
    populateTags('tags-culinary-fac', dest.culinary_facilities);
    populateTags('tags-culinary-act', dest.culinary_activities);
    populateTags('tags-culinary-type', dest.culinary_types);

    // Populate Culture
    populateTags('tags-culture-heritage', dest.culture_heritage);
    populateTags('tags-culture-act', dest.culture_activities);
    populateTags('tags-culture-elem', dest.culture_elements);

    // Populate Effort
    populateTags('tags-effort-acc', dest.effort_accessibility);
    populateTags('tags-effort-eff', dest.effort_effort);
    populateTags('tags-effort-mob', dest.effort_mobility);

    // Show modal with animation
    modal.style.display = 'flex';
    requestAnimationFrame(() => {
        modal.classList.add('show');
    });
}

function closeDetailModal() {
    const modal = document.getElementById('detail-modal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.style.display = 'none';
        }, 250);
    }
}

function populateTags(containerId, tagsData) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Clear container securely
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }
    
    let tags = [];
    if (typeof tagsData === 'string') {
        try { tags = JSON.parse(tagsData); } catch(e) { tags = []; }
    } else if (Array.isArray(tagsData)) {
        tags = tagsData;
    }
    
    if (tags.length === 0) {
        container.style.display = 'none';
        return;
    }
    
    container.style.display = 'flex';
    tags.forEach(tag => {
        const span = document.createElement('span');
        span.className = 'param-tag';
        span.textContent = tag;
        container.appendChild(span);
    });
}
