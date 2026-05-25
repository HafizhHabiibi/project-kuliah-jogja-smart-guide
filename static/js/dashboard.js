/**
 * Jogja Smart Guide — Dashboard JS
 * Renders destination cards, fetches weather data, handles search/filter/sort
 */

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
});


let allDestinations = [];
let userLocation = null;

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

    if (typeof IS_USER_LOGGED_IN !== 'undefined' && IS_USER_LOGGED_IN) {
        // Default fallback Jogja Center (Malioboro)
        userLocation = {
            latitude: -7.7929,
            longitude: 110.3658,
            isExact: false
        };

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(position => {
                userLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    isExact: true
                };
                renderCards(allDestinations);
            }, error => {
                console.warn("Geolocation access denied or failed, using city center fallback:", error);
            });
        }
    }

    renderCards(allDestinations);
    fetchAllWeatherData();
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

        const desc = document.createElement('p');
        desc.className = 'dest-card-desc';
        desc.textContent = dest.description;
        cardBody.appendChild(desc);

        // Weather widget container
        const weatherContainer = document.createElement('div');
        weatherContainer.className = 'weather-widget';
        weatherContainer.id = `weather-${dest.id}`;

        const weatherParams = [
            { icon: 'water_drop', label: 'Hujan' },
            { icon: 'thermostat', label: 'Suhu' },
            { icon: 'cloud', label: 'Awan' },
            { icon: 'air', label: 'Angin' }
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
            const wSkeleton = document.createElement('div');
            wSkeleton.className = 'weather-skeleton';
            wValue.appendChild(wSkeleton);
            item.appendChild(wValue);

            const wLabel = document.createElement('div');
            wLabel.className = 'weather-label';
            wLabel.textContent = param.label;
            item.appendChild(wLabel);

            weatherContainer.appendChild(item);
        });

        cardBody.appendChild(weatherContainer);

        // Distance container (if logged in and location is set)
        if (typeof IS_USER_LOGGED_IN !== 'undefined' && IS_USER_LOGGED_IN && userLocation) {
            const distance = calculateDistance(
                userLocation.latitude,
                userLocation.longitude,
                dest.latitude,
                dest.longitude
            );
            
            const distanceContainer = document.createElement('div');
            distanceContainer.className = 'dest-card-distance';
            
            const distanceIconSpan = document.createElement('span');
            distanceIconSpan.className = 'material-icons distance-icon';
            distanceIconSpan.textContent = 'near_me';
            distanceContainer.appendChild(distanceIconSpan);
            
            const labelText = userLocation.isExact 
                ? `Jarak dari lokasi Anda: ${distance.toFixed(1)} km`
                : `Jarak dari Pusat Kota (Malioboro): ${distance.toFixed(1)} km`;
                
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
        case 'Sejarah':
            iconName = 'history_edu';
            break;
        case 'Alam':
            iconName = 'terrain';
            break;
        case 'Pantai':
            iconName = 'beach_access';
            break;
        case 'Budaya':
            iconName = 'theater_comedy';
            break;
        case 'Belanja':
            iconName = 'shopping_bag';
            break;
        case 'Hiburan':
            iconName = 'attractions';
            break;
    }
    return iconName;
}

/**
 * Fetch weather data for all destinations
 */
async function fetchAllWeatherData() {
    // Small delay between requests to avoid rate limiting
    for (const dest of allDestinations) {
        fetchWeather(dest);
        await new Promise(resolve => setTimeout(resolve, 200));
    }
}


/**
 * Fetch weather for a single destination and update its widget
 */
async function fetchWeather(dest) {
    const widget = document.getElementById(`weather-${dest.id}`);
    if (!widget) return;

    try {
        const response = await fetch(`/api/weather?lat=${dest.latitude}&lon=${dest.longitude}`);
        const data = await response.json();

        const rainVal = data.rain && data.rain['1h'] ? data.rain['1h'] : 0;
        const tempVal = data.main ? data.main.temp : '-';
        const cloudsVal = data.clouds ? data.clouds.all : '-';
        const windVal = data.wind ? data.wind.speed : '-';

        const rainText = `${rainVal} mm`;
        const tempText = `${typeof tempVal === 'number' ? tempVal.toFixed(1) : tempVal}°C`;
        const cloudsText = `${cloudsVal}%`;
        const windText = `${typeof windVal === 'number' ? windVal.toFixed(1) : windVal} m/s`;

        // Clear widget securely
        while (widget.firstChild) {
            widget.removeChild(widget.firstChild);
        }

        const items = [
            { icon: 'water_drop', val: rainText, label: 'Hujan' },
            { icon: 'thermostat', val: tempText, label: 'Suhu' },
            { icon: 'cloud', val: cloudsText, label: 'Awan' },
            { icon: 'air', val: windText, label: 'Angin' }
        ];

        items.forEach(itemData => {
            const item = document.createElement('div');
            item.className = 'weather-item';

            const wIconDiv = document.createElement('div');
            wIconDiv.className = 'weather-icon';
            const wIconSpan = document.createElement('span');
            wIconSpan.className = 'material-icons weather-icon-mi';
            wIconSpan.textContent = itemData.icon;
            wIconDiv.appendChild(wIconSpan);
            item.appendChild(wIconDiv);

            const wValue = document.createElement('div');
            wValue.className = 'weather-value';
            wValue.textContent = itemData.val;
            item.appendChild(wValue);

            const wLabel = document.createElement('div');
            wLabel.className = 'weather-label';
            wLabel.textContent = itemData.label;
            item.appendChild(wLabel);

            widget.appendChild(item);
        });

    } catch (error) {
        console.error(`Weather fetch error for ${dest.name}:`, error);
    }
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
    const sortType = document.getElementById('sort-by')?.value || 'random';

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

    // Re-fetch weather for visible cards
    filtered.forEach((dest, index) => {
        setTimeout(() => fetchWeather(dest), index * 150);
    });
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
        if (typeof IS_USER_LOGGED_IN !== 'undefined' && IS_USER_LOGGED_IN && userLocation) {
            const distance = calculateDistance(
                userLocation.latitude,
                userLocation.longitude,
                dest.latitude,
                dest.longitude
            );
            
            while (modalDistanceBox.firstChild) {
                modalDistanceBox.removeChild(modalDistanceBox.firstChild);
            }
            
            const distanceIconSpan = document.createElement('span');
            distanceIconSpan.className = 'material-icons distance-icon';
            distanceIconSpan.textContent = 'near_me';
            modalDistanceBox.appendChild(distanceIconSpan);
            
            const labelText = userLocation.isExact 
                ? `Jarak dari lokasi Anda: ${distance.toFixed(1)} km`
                : `Jarak dari Pusat Kota (Malioboro): ${distance.toFixed(1)} km`;
                
            modalDistanceBox.appendChild(document.createTextNode(labelText));
            modalDistanceSection.style.display = 'block';
        } else {
            modalDistanceSection.style.display = 'none';
        }
    }

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
