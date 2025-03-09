// Initialize map and markers
let map;
let markers = [];
const defaultLocation = [40.7128, -74.0060]; // Default location (New York City)

// Initialize map
function initMap() {
    try {
        console.log('Initializing map...');
        
        // Create the map
        map = L.map('map', {
            center: defaultLocation,
            zoom: 12
        });

        // Add the OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        console.log('Map initialized successfully');
        
        // Fetch courts immediately
        fetchNearbyCourts(defaultLocation);
    } catch (error) {
        console.error('Error initializing map:', error);
        showError('Error initializing map. Please refresh the page.');
    }
}

// Get user's location
function getUserLocation() {
    const button = document.querySelector('.location-button');
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Getting location...';

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const userLocation = [position.coords.latitude, position.coords.longitude];
                map.setView(userLocation, 13);
                fetchNearbyCourts(userLocation);
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-location-arrow mr-2"></i>Use My Location';
            },
            error => {
                console.error('Error getting location:', error);
                showError('Unable to get your location. Please enter it manually.');
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-location-arrow mr-2"></i>Use My Location';
            },
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            }
        );
    } else {
        showError('Geolocation is not supported by your browser.');
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-location-arrow mr-2"></i>Use My Location';
    }
}

// Fetch nearby courts
function fetchNearbyCourts(location) {
    console.log('Fetching courts for location:', location);
    const courtsContainer = document.getElementById('courts-container');
    
    // Show loading state
    courtsContainer.innerHTML = `
        <div class="text-center text-gray-500 py-4">
            <div class="loading-spinner"></div>
            <p class="mt-2">Loading courts...</p>
        </div>
    `;

    fetch('/courts', {
        headers: {
            'Accept': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(courts => {
            // Clear existing markers
            markers.forEach(marker => marker.remove());
            markers = [];

            // Clear courts list
            courtsContainer.innerHTML = '';

            if (courts.length === 0) {
                courtsContainer.innerHTML = `
                    <div class="text-center text-gray-500 py-4">
                        <i class="fas fa-tennis-ball text-4xl mb-2"></i>
                        <p>No courts found in this area.</p>
                    </div>
                `;
                return;
            }

            courts.forEach(court => {
                // Add marker to map
                const marker = L.marker([court.latitude, court.longitude])
                    .bindPopup(`
                        <div class="text-center">
                            <h3 class="font-medium">${escapeHtml(court.name)}</h3>
                            <p class="text-sm text-gray-600">${escapeHtml(court.address)}</p>
                            <p class="text-sm font-medium mt-2">$${court.price_per_hour}/hour</p>
                            <a href="/book/${court.id}" class="inline-block mt-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded hover:bg-indigo-700">
                                Book Court
                            </a>
                        </div>
                    `)
                    .addTo(map);
                markers.push(marker);

                // Add court to list
                courtsContainer.innerHTML += `
                    <div class="court-item border-b border-gray-200 pb-4 last:border-b-0 last:pb-0">
                        <div class="flex justify-between items-start">
                            <div>
                                <h3 class="text-lg font-medium text-gray-900">${escapeHtml(court.name)}</h3>
                                <p class="text-sm text-gray-600">${escapeHtml(court.address)}</p>
                                <p class="text-sm font-medium text-gray-900 mt-1">$${court.price_per_hour}/hour</p>
                            </div>
                            <a href="/book/${court.id}" 
                               class="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                                Book
                            </a>
                        </div>
                    </div>
                `;
            });

            // Fit map bounds to show all markers
            if (markers.length > 0) {
                const group = new L.featureGroup(markers);
                map.fitBounds(group.getBounds().pad(0.1));
            }
        })
        .catch(error => {
            console.error('Error fetching courts:', error);
            showError('Error loading courts. Please try again.');
        });
}

// Show error message
function showError(message) {
    const courtsContainer = document.getElementById('courts-container');
    courtsContainer.innerHTML = `
        <div class="text-center text-red-500 py-4">
            <i class="fas fa-exclamation-circle text-4xl mb-2"></i>
            <p>${escapeHtml(message)}</p>
        </div>
    `;
}

// Escape HTML to prevent XSS
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Initialize map when page loads
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('map')) {
        initMap();
    }
});
