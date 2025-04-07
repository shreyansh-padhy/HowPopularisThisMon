let trendsChart = null;  // Global variable to store the chart instance

// Add these functions at the beginning of your script.js
async function fetchWikipediaViews(pokemon) {
    const response = await fetch(`https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/${pokemon}/monthly/2023010100/2023123100`);
    const data = await response.json();
    return data;
}

async function fetchRedditMetrics(pokemon) {
    const response = await fetch(`https://www.reddit.com/search.json?q=${pokemon}&limit=100`);
    const data = await response.json();
    return data;
}

async function fetchYoutubeMetrics(pokemon) {
    const response = await fetch(`https://www.googleapis.com/youtube/v3/search?part=snippet&q=${pokemon}&key=${CONFIG.API_KEYS.youtube.api_key}&maxResults=50`);
    const data = await response.json();
    return data;
}

function showLoader() {
    const resultDiv = document.getElementById('result');
    const searchButton = document.getElementById('searchButton');
    const pokemonInput = document.getElementById('pokemonInput');
    
    // Disable input and button
    searchButton.disabled = true;
    pokemonInput.disabled = true;
    searchButton.classList.add('disabled');
    pokemonInput.classList.add('disabled');
    
    // Show Pokeball loader
    resultDiv.innerHTML = `
        <div class="loader-container">
            <div class="pokeball-loader"></div>
            <p style="margin-top: 20px;">Fetching Pokémon data...</p>
        </div>
    `;
}

function hideLoader() {
    const searchButton = document.getElementById('searchButton');
    const pokemonInput = document.getElementById('pokemonInput');
    
    // Re-enable input and button
    searchButton.disabled = false;
    pokemonInput.disabled = false;
    searchButton.classList.remove('disabled');
    pokemonInput.classList.remove('disabled');
}

// Update your getMetrics function
async function getMetrics() {
    const pokemon = document.getElementById('pokemonInput').value.trim();
    
    if (!pokemon) {
        document.getElementById('result').innerHTML = '<p class="error">Please enter a Pokémon name</p>';
        return;
    }

    if (!is_valid_pokemon(pokemon)) {
        document.getElementById('result').innerHTML = '<p class="error">Please enter a valid Pokémon name</p>';
        return;
    }

    showLoader();

    try {
        const [wikiData, redditData, youtubeData] = await Promise.all([
            fetchWikipediaViews(pokemon),
            fetchRedditMetrics(pokemon),
            fetchYoutubeMetrics(pokemon)
        ]);

        // Process the data and create metrics object
        const metrics = processMetrics(pokemon, wikiData, redditData, youtubeData);
        displayMetrics(metrics);
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('result').innerHTML = '<p class="error">Error fetching data.</p>';
    } finally {
        hideLoader();
    }
}

function displayMetrics(data) {
    const resultDiv = document.getElementById('result');
    
    try {
        let html = `
            <div class="metrics-container">
                <h2>${data.pokemon} Popularity Metrics</h2>
                <div class="total-score">
                    <h3>Overall Popularity Score</h3>
                    <div class="score-circle">${(data.total_score * 100).toFixed(1)}</div>
                </div>
                <div class="metrics-grid">
                    <div class="metric-card trends-card">
                        <h4>Google Trends</h4>
                        <canvas id="trendsChart"></canvas>
                        <p class="metric-value">Average Score: ${(data.metrics.google_trends.avg_value).toFixed(1)}</p>
                    </div>
                    
                    <div class="metric-card">
                        <h4>Wikipedia Views</h4>
                        <p>
                            <span class="metric-label">Monthly Average:</span><br>
                            <span class="metric-value">${Math.round(data.metrics.wikipedia.monthly_avg).toLocaleString()}</span>
                        </p>
                        <p>
                            <span class="metric-label">Total Views:</span><br>
                            <span class="metric-value">${Math.round(data.metrics.wikipedia.total_views).toLocaleString()}</span>
                        </p>
                    </div>
                    
                    <div class="metric-card">
                        <h4>Reddit Activity</h4>
                        <p>
                            <span class="metric-label">Total Posts:</span><br>
                            <span class="metric-value">${data.metrics.reddit.total_posts.toLocaleString()}</span>
                        </p>
                        <p>
                            <span class="metric-label">Total Upvotes:</span><br>
                            <span class="metric-value">${data.metrics.reddit.total_upvotes.toLocaleString()}</span>
                        </p>
                        <p>
                            <span class="metric-label">Average Upvotes:</span><br>
                            <span class="metric-value">${data.metrics.reddit.avg_upvotes.toFixed(1)}</span>
                        </p>
                    </div>
                    
                    <div class="metric-card">
                        <h4>YouTube Presence</h4>
                        <p><small>Based on the 50 most relevant videos</small></p>
                        <p>
                            <span class="metric-label">Videos Found:</span><br>
                            <span class="metric-value">${data.metrics.youtube.total_videos.toLocaleString()}</span>
                        </p>
                        <p>
                            <span class="metric-label">Total Views:</span><br>
                            <span class="metric-value">${data.metrics.youtube.total_views.toLocaleString()}</span>
                        </p>
                        <p>
                            <span class="metric-label">Average Views per Video:</span><br>
                            <span class="metric-value">${Math.round(data.metrics.youtube.avg_views).toLocaleString()}</span>
                        </p>
                        <p>
                            <span class="metric-label">Total Likes:</span><br>
                            <span class="metric-value">${data.metrics.youtube.total_likes.toLocaleString()}</span>
                        </p>
                    </div>
                </div>
            </div>
        `;
        
        // Add fallback data notice if using fallback trends
        if (data.using_fallback_trends) {
            html = html.replace(
                '<h4>Google Trends</h4>',
                '<h4>Google Trends (Estimated)</h4>' +
                '<p class="metric-label">Using estimated data due to API limitations</p>'
            );
        }
        
        resultDiv.innerHTML = html;
        
        if (data.metrics.google_trends.trend_values.length > 0) {
            createTrendsChart(data.metrics.google_trends.trend_values, data.pokemon);
        }
    } catch (error) {
        console.error('Error displaying metrics:', error);
        resultDiv.innerHTML = '<p class="error">Error displaying metrics data.</p>';
    }
}

function createTrendsChart(trends, pokemon) {
    const ctx = document.getElementById('trendsChart').getContext('2d');
    if (trendsChart) {
        trendsChart.destroy();
    }
    
    trendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({length: trends.length}, (_, i) => `Week ${i + 1}`),
            datasets: [{
                label: `${pokemon} Popularity`,
                data: trends,
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                fill: true,
                tension: 0.3,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: `Popularity Trends for ${pokemon}`,
                    font: {
                        size: 16
                    }
                },
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Popularity Score'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time Period'
                    }
                }
            }
        }
    });
}

// Add this at the end of your script.js file
document.getElementById('pokemonInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        getMetrics();
    }
});
