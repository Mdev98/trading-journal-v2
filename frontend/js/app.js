/**
 * Application principale - Trading Journal
 * Gère l'interface utilisateur et les interactions
 */

// ==================== STATE ====================
const state = {
    currentView: 'dashboard',
    currentPage: 1,
    totalPages: 1,
    selectedTradeId: null,
    filesToUpload: [],
    filters: {},
    isOwner: false,
};

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initDragDrop();
    initFileInput();
    initLogin();
    loadDashboard();
});

function initLogin() {
    // Afficher le bouton login si non owner
    if (!state.isOwner) {
        addLoginButton();
    }
    // Formulaire login
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const password = document.getElementById('owner-password').value;
            try {
                await API.loginOwner(password);
                state.isOwner = true;
                closeLoginModal();
                showNotification('Connecté comme owner', 'success');
                updateOwnerUI();
            } catch (err) {
                document.getElementById('login-error').textContent = err.message;
                document.getElementById('login-error').style.display = 'block';
            }
        // Vérifier la présence du JWT au chargement
        if (localStorage.getItem('owner_jwt')) {
            state.isOwner = true;
            updateOwnerUI && updateOwnerUI();
        }
        });
    }
}

function addLoginButton() {
    const header = document.querySelector('.header');
    if (header && !document.getElementById('owner-login-btn')) {
        const btn = document.createElement('button');
        btn.id = 'owner-login-btn';
        btn.className = 'btn btn-secondary';
        btn.textContent = 'Connexion Owner';
        btn.onclick = openLoginModal;
        header.appendChild(btn);
    }
}

function openLoginModal() {
    document.getElementById('login-modal').style.display = 'block';
}
function closeLoginModal() {
    document.getElementById('login-modal').style.display = 'none';
    document.getElementById('login-error').style.display = 'none';
}

function updateOwnerUI() {
    // Afficher les boutons CRUD si owner
    document.querySelectorAll('.btn-add, .btn-edit, .btn-delete, #upload-btn').forEach(btn => {
        btn.style.display = state.isOwner ? '' : 'none';
    });
    // Cacher le bouton login
    const loginBtn = document.getElementById('owner-login-btn');
    if (loginBtn) loginBtn.style.display = 'none';
}

/**
 * Initialiser la navigation
 */
function initNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const view = e.target.dataset.view;
            switchView(view);
        });
    });
}

/**
 * Changer de vue
 */
function switchView(viewName) {
    // Mettre à jour les classes actives
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.toggle('active', link.dataset.view === viewName);
    });

    document.querySelectorAll('.view').forEach(view => {
        view.classList.toggle('active', view.id === `${viewName}-view`);
    });

    state.currentView = viewName;

    // Charger les données de la vue
    switch (viewName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'trades':
            loadTrades();
            loadFilterOptions();
            break;
        case 'stats':
            loadAllStats();
            break;
    }
}

// ==================== DASHBOARD ====================

/**
 * Charger le dashboard
 */
async function loadDashboard() {
    try {
        // Charger les stats globales
        const stats = await API.getGlobalStats();
        updateStatsCards(stats);

        // Charger les derniers trades
        const tradesResponse = await API.getTrades({ page: 1, pageSize: 10 });
        renderRecentTrades(tradesResponse.trades);
    } catch (error) {
        showNotification('Erreur de chargement du dashboard', 'error');
    }
}

/**
 * Mettre à jour les cartes de stats
 */
function updateStatsCards(stats) {
    const setValue = (id, value, isPositive = null) => {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = value;
            el.classList.remove('positive', 'negative');
            if (isPositive === true) el.classList.add('positive');
            if (isPositive === false) el.classList.add('negative');
        }
    };

    setValue('stat-total-trades', stats.total_trades);
    setValue('stat-winrate', `${stats.winrate}%`, stats.winrate >= 50);
    setValue('stat-expectancy', `${stats.expectancy}R`, stats.expectancy > 0);
    setValue('stat-total-r', `${stats.total_r > 0 ? '+' : ''}${stats.total_r}R`, stats.total_r > 0);
    setValue('stat-pnl', `$${stats.total_pnl_usd.toLocaleString()}`, stats.total_pnl_usd > 0);
    setValue('stat-drawdown', `${stats.max_drawdown_r}R`, false);
    setValue('stat-discipline', `${stats.discipline_rate}%`, stats.discipline_rate >= 80);
    setValue('stat-pf', stats.profit_factor, stats.profit_factor > 1);
}

/**
 * Afficher les trades récents
 */
function renderRecentTrades(trades) {
    const tbody = document.getElementById('recent-trades-body');
    
    if (!trades || trades.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    <div class="empty-state-icon">📊</div>
                    <p>Aucun trade enregistré</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = trades.map(trade => `
        <tr>
            <td>${formatDate(trade.date)}</td>
            <td>${trade.instrument}</td>
            <td>${trade.setup}</td>
            <td><span class="badge badge-${trade.direction.toLowerCase()}">${trade.direction}</span></td>
            <td class="${getResultClass(trade.result_r)}">${formatResult(trade.result_r)}</td>
            <td class="${getResultClass(trade.pnl_usd)}">${formatPnL(trade.pnl_usd)}</td>
            <td class="cell-actions">
                <button class="btn btn-sm btn-outline" onclick="viewTradeDetail(${trade.id})">👁</button>
                <button class="btn btn-sm btn-outline" onclick="openImagesModal(${trade.id})">📷</button>
            </td>
        </tr>
    `).join('');
}

// ==================== TRADES LIST ====================

/**
 * Charger la liste des trades
 */
async function loadTrades(page = 1) {
    try {
        state.currentPage = page;
        
        const params = {
            page,
            pageSize: CONFIG.PAGE_SIZE,
            ...state.filters,
        };

        const response = await API.getTrades(params);
        state.totalPages = response.total_pages;

        renderTradesTable(response.trades);
        renderPagination();
    } catch (error) {
        showNotification('Erreur de chargement des trades', 'error');
    }
}

/**
 * Charger les options de filtrage
 */
async function loadFilterOptions() {
    try {
        const options = await API.getFilterOptions();

        // Remplir les selects
        populateSelect('filter-instrument', options.instruments);
        populateSelect('filter-setup', options.setups);
    } catch (error) {
        console.error('Error loading filter options:', error);
    }
}

/**
 * Remplir un select avec des options
 */
function populateSelect(selectId, values) {
    const select = document.getElementById(selectId);
    if (!select) return;

    // Garder la première option (Tous)
    const firstOption = select.options[0];
    select.innerHTML = '';
    select.appendChild(firstOption);

    values.forEach(value => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = value;
        select.appendChild(option);
    });
}

/**
 * Afficher la table des trades
 */
function renderTradesTable(trades) {
    const tbody = document.getElementById('all-trades-body');

    if (!trades || trades.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="12" class="empty-state">
                    <div class="empty-state-icon">📊</div>
                    <p>Aucun trade trouvé</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = trades.map(trade => `
        <tr>
            <td>${formatDate(trade.date)}</td>
            <td>${trade.instrument}</td>
            <td>${trade.session}</td>
            <td>${trade.setup}</td>
            <td><span class="badge badge-${trade.direction.toLowerCase()}">${trade.direction}</span></td>
            <td>${trade.entry}</td>
            <td>${trade.rr_expected}</td>
            <td class="${getResultClass(trade.result_r)}">${formatResult(trade.result_r)}</td>
            <td class="${getResultClass(trade.pnl_usd)}">${formatPnL(trade.pnl_usd)}</td>
            <td><span class="badge ${trade.respected_plan ? 'badge-success' : 'badge-danger'}">${trade.respected_plan ? '✓' : '✗'}</span></td>
            <td>${trade.images ? trade.images.length : 0}</td>
            <td class="cell-actions">
                <button class="btn btn-sm btn-outline" onclick="viewTradeDetail(${trade.id})" title="Voir">👁</button>
                <button class="btn btn-sm btn-outline" onclick="openImagesModal(${trade.id})" title="Images">📷</button>
                <button class="btn btn-sm btn-outline" onclick="editTrade(${trade.id})" title="Modifier">✏️</button>
                <button class="btn btn-sm btn-danger" onclick="confirmDeleteTrade(${trade.id})" title="Supprimer">🗑</button>
            </td>
        </tr>
    `).join('');
}

/**
 * Afficher la pagination
 */
function renderPagination() {
    const container = document.getElementById('pagination');
    if (state.totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '';

    // Bouton précédent
    html += `<button class="btn btn-outline" onclick="loadTrades(${state.currentPage - 1})" ${state.currentPage === 1 ? 'disabled' : ''}>←</button>`;

    // Pages
    for (let i = 1; i <= state.totalPages; i++) {
        if (
            i === 1 ||
            i === state.totalPages ||
            (i >= state.currentPage - 2 && i <= state.currentPage + 2)
        ) {
            html += `<button class="btn ${i === state.currentPage ? 'btn-primary active' : 'btn-outline'}" onclick="loadTrades(${i})">${i}</button>`;
        } else if (i === state.currentPage - 3 || i === state.currentPage + 3) {
            html += `<span style="padding: 0 8px;">...</span>`;
        }
    }

    // Bouton suivant
    html += `<button class="btn btn-outline" onclick="loadTrades(${state.currentPage + 1})" ${state.currentPage === state.totalPages ? 'disabled' : ''}>→</button>`;

    container.innerHTML = html;
}

/**
 * Appliquer les filtres
 */
function applyFilters() {
    state.filters = {
        dateFrom: document.getElementById('filter-date-from').value || undefined,
        dateTo: document.getElementById('filter-date-to').value || undefined,
        instrument: document.getElementById('filter-instrument').value || undefined,
        setup: document.getElementById('filter-setup').value || undefined,
        session: document.getElementById('filter-session').value || undefined,
    };

    loadTrades(1);
}

/**
 * Réinitialiser les filtres
 */
function clearFilters() {
    document.getElementById('filter-date-from').value = '';
    document.getElementById('filter-date-to').value = '';
    document.getElementById('filter-instrument').value = '';
    document.getElementById('filter-setup').value = '';
    document.getElementById('filter-session').value = '';

    state.filters = {};
    loadTrades(1);
}

// ==================== STATISTICS ====================

/**
 * Charger toutes les statistiques
 */
async function loadAllStats() {
    try {
        const [setupStats, sessionStats, errorStats, mentalStats] = await Promise.all([
            API.getStatsBySetup(),
            API.getStatsBySession(),
            API.getErrorStats(),
            API.getMentalStats(),
        ]);

        renderSetupStats(setupStats);
        renderSessionStats(sessionStats);
        renderErrorStats(errorStats);
        renderMentalStats(mentalStats);
    } catch (error) {
        showNotification('Erreur de chargement des statistiques', 'error');
    }
}

function renderSetupStats(stats) {
    const tbody = document.getElementById('setup-stats-body');
    if (!stats || stats.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state">Aucune donnée</td></tr>';
        return;
    }

    tbody.innerHTML = stats.map(s => `
        <tr>
            <td>${s.setup}</td>
            <td>${s.total_trades}</td>
            <td class="${s.winrate >= 50 ? 'cell-positive' : 'cell-negative'}">${s.winrate}%</td>
            <td class="${s.expectancy > 0 ? 'cell-positive' : 'cell-negative'}">${s.expectancy}R</td>
            <td class="${s.total_r > 0 ? 'cell-positive' : 'cell-negative'}">${s.total_r}R</td>
            <td>${s.profit_factor}</td>
        </tr>
    `).join('');
}

function renderSessionStats(stats) {
    const tbody = document.getElementById('session-stats-body');
    if (!stats || stats.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Aucune donnée</td></tr>';
        return;
    }

    tbody.innerHTML = stats.map(s => `
        <tr>
            <td>${s.session}</td>
            <td>${s.total_trades}</td>
            <td class="${s.winrate >= 50 ? 'cell-positive' : 'cell-negative'}">${s.winrate}%</td>
            <td class="${s.expectancy > 0 ? 'cell-positive' : 'cell-negative'}">${s.expectancy}R</td>
            <td class="${s.total_r > 0 ? 'cell-positive' : 'cell-negative'}">${s.total_r}R</td>
        </tr>
    `).join('');
}

function renderErrorStats(stats) {
    const tbody = document.getElementById('error-stats-body');
    if (!stats || stats.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-state">Aucune erreur enregistrée 🎉</td></tr>';
        return;
    }

    tbody.innerHTML = stats.map(s => `
        <tr>
            <td>${s.error_type}</td>
            <td>${s.count}</td>
            <td>${s.percentage}%</td>
            <td class="cell-negative">${s.avg_loss_r}R</td>
        </tr>
    `).join('');
}

function renderMentalStats(stats) {
    const tbody = document.getElementById('mental-stats-body');
    if (!stats || stats.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-state">Aucune donnée</td></tr>';
        return;
    }

    const stateLabels = {
        1: '😰 Très mauvais',
        2: '😟 Mauvais',
        3: '😐 Neutre',
        4: '🙂 Bon',
        5: '😄 Excellent'
    };

    tbody.innerHTML = stats.map(s => `
        <tr>
            <td>${stateLabels[s.mental_state] || s.mental_state}</td>
            <td>${s.total_trades}</td>
            <td class="${s.winrate >= 50 ? 'cell-positive' : 'cell-negative'}">${s.winrate}%</td>
            <td class="${s.avg_result_r > 0 ? 'cell-positive' : 'cell-negative'}">${s.avg_result_r}R</td>
        </tr>
    `).join('');
}

// ==================== TRADE MODAL ====================

/**
 * Ouvrir le modal de création/édition de trade
 */
function openTradeModal(tradeId = null) {
    const modal = document.getElementById('trade-modal');
    const form = document.getElementById('trade-form');
    const title = document.getElementById('modal-title');

    form.reset();
    document.getElementById('trade-id').value = '';
    document.getElementById('error-type-group').style.display = 'none';

    if (tradeId) {
        title.textContent = 'Modifier le Trade';
        loadTradeForEdit(tradeId);
    } else {
        title.textContent = 'Nouveau Trade';
        // Pré-remplir la date avec maintenant
        const now = new Date();
        document.getElementById('trade-date').value = now.toISOString().slice(0, 16);
    }

    modal.classList.add('active');
}

/**
 * Fermer le modal de trade
 */
function closeTradeModal() {
    document.getElementById('trade-modal').classList.remove('active');
}

/**
 * Charger un trade pour édition
 */
async function loadTradeForEdit(tradeId) {
    try {
        const trade = await API.getTrade(tradeId);

        document.getElementById('trade-id').value = trade.id;
        document.getElementById('trade-date').value = trade.date.slice(0, 16);
        document.getElementById('trade-instrument').value = trade.instrument;
        document.getElementById('trade-session').value = trade.session;
        document.getElementById('trade-setup').value = trade.setup;
        document.getElementById('trade-direction').value = trade.direction;
        document.getElementById('trade-timeframe').value = trade.timeframe;
        document.getElementById('trade-entry').value = trade.entry;
        document.getElementById('trade-sl').value = trade.stop_loss;
        document.getElementById('trade-tp').value = trade.take_profit || '';
        document.getElementById('trade-risk-pct').value = trade.risk_pct;
        document.getElementById('trade-risk-usd').value = trade.risk_usd;
        document.getElementById('trade-rr').value = trade.rr_expected;
        document.getElementById('trade-result-r').value = trade.result_r || '';
        document.getElementById('trade-pnl').value = trade.pnl_usd || '';
        document.getElementById('trade-duration').value = trade.duration_min || '';
        document.getElementById('trade-plan').value = trade.respected_plan.toString();
        document.getElementById('trade-error').value = trade.error.toString();
        document.getElementById('trade-error-type').value = trade.error_type;
        document.getElementById('trade-mental').value = trade.mental_state || '';
        document.getElementById('trade-notes').value = trade.notes || '';

        if (trade.error) {
            document.getElementById('error-type-group').style.display = 'flex';
        }
    } catch (error) {
        showNotification('Erreur de chargement du trade', 'error');
    }
}

/**
 * Toggle affichage du type d'erreur
 */
function toggleErrorType() {
    const errorSelect = document.getElementById('trade-error');
    const errorTypeGroup = document.getElementById('error-type-group');
    errorTypeGroup.style.display = errorSelect.value === 'true' ? 'flex' : 'none';
}

/**
 * Soumettre le formulaire de trade
 */
async function handleTradeSubmit(event) {
    event.preventDefault();

    const tradeId = document.getElementById('trade-id').value;
    
    const tradeData = {
        date: document.getElementById('trade-date').value + ':00',
        instrument: document.getElementById('trade-instrument').value.toUpperCase(),
        session: document.getElementById('trade-session').value,
        setup: document.getElementById('trade-setup').value,
        direction: document.getElementById('trade-direction').value,
        timeframe: document.getElementById('trade-timeframe').value,
        entry: parseFloat(document.getElementById('trade-entry').value),
        stop_loss: parseFloat(document.getElementById('trade-sl').value),
        take_profit: parseFloat(document.getElementById('trade-tp').value) || null,
        risk_pct: parseFloat(document.getElementById('trade-risk-pct').value),
        risk_usd: parseFloat(document.getElementById('trade-risk-usd').value),
        rr_expected: parseFloat(document.getElementById('trade-rr').value),
        result_r: parseFloat(document.getElementById('trade-result-r').value) || null,
        pnl_usd: parseFloat(document.getElementById('trade-pnl').value) || null,
        duration_min: parseInt(document.getElementById('trade-duration').value) || null,
        respected_plan: document.getElementById('trade-plan').value === 'true',
        error: document.getElementById('trade-error').value === 'true',
        error_type: document.getElementById('trade-error').value === 'true' 
            ? document.getElementById('trade-error-type').value 
            : 'None',
        mental_state: parseInt(document.getElementById('trade-mental').value) || null,
        notes: document.getElementById('trade-notes').value || null,
    };

    try {
        if (tradeId) {
            await API.updateTrade(tradeId, tradeData);
            showNotification('Trade mis à jour avec succès', 'success');
        } else {
            await API.createTrade(tradeData);
            showNotification('Trade créé avec succès', 'success');
        }

        closeTradeModal();
        
        // Rafraîchir la vue courante
        if (state.currentView === 'dashboard') {
            loadDashboard();
        } else if (state.currentView === 'trades') {
            loadTrades(state.currentPage);
        }
    } catch (error) {
        showNotification(`Erreur: ${error.message}`, 'error');
    }
}

/**
 * Alias pour édition
 */
function editTrade(tradeId) {
    openTradeModal(tradeId);
}

/**
 * Confirmer la suppression d'un trade
 */
async function confirmDeleteTrade(tradeId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce trade ?')) {
        return;
    }

    try {
        await API.deleteTrade(tradeId);
        showNotification('Trade supprimé', 'success');
        loadTrades(state.currentPage);
    } catch (error) {
        showNotification(`Erreur: ${error.message}`, 'error');
    }
}

// ==================== IMAGES MODAL ====================

/**
 * Ouvrir le modal d'images
 */
async function openImagesModal(tradeId) {
    state.selectedTradeId = tradeId;
    state.filesToUpload = [];
    
    document.getElementById('upload-btn').disabled = true;
    document.getElementById('images-modal').classList.add('active');
    
    await loadTradeImages(tradeId);
}

/**
 * Fermer le modal d'images
 */
function closeImagesModal() {
    document.getElementById('images-modal').classList.remove('active');
    state.selectedTradeId = null;
    state.filesToUpload = [];
}

/**
 * Charger les images d'un trade
 */
async function loadTradeImages(tradeId) {
    const gallery = document.getElementById('images-gallery');
    
    try {
        const images = await API.getTradeImages(tradeId);
        
        if (!images || images.length === 0) {
            gallery.innerHTML = '<div class="empty-state"><p>Aucune image</p></div>';
            return;
        }

        gallery.innerHTML = images.map(img => {
            const imgUrl = getImageUrl(img.image_url);
            return `
            <div class="image-card">
                <img src="${imgUrl}" alt="${img.image_type}" onclick="openFullImage('${imgUrl}')">
                <div class="image-card-overlay">
                    <span class="image-type-badge">${img.image_type}</span>
                    <button class="image-delete-btn" onclick="deleteImage(${img.id})">🗑</button>
                </div>
            </div>
        `;
        }).join('');
    } catch (error) {
        gallery.innerHTML = '<div class="empty-state"><p>Erreur de chargement</p></div>';
    }
}

/**
 * Initialiser le drag & drop
 */
function initDragDrop() {
    const uploadZone = document.getElementById('upload-zone');
    
    if (!uploadZone) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => uploadZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadZone.addEventListener(eventName, () => uploadZone.classList.remove('dragover'), false);
    });

    uploadZone.addEventListener('drop', handleDrop, false);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDrop(e) {
    const files = e.dataTransfer.files;
    handleFiles(files);
}

/**
 * Initialiser l'input file
 */
function initFileInput() {
    const input = document.getElementById('image-input');
    if (input) {
        input.addEventListener('change', (e) => handleFiles(e.target.files));
    }
}

/**
 * Gérer les fichiers sélectionnés
 */
function handleFiles(files) {
    state.filesToUpload = Array.from(files);
    document.getElementById('upload-btn').disabled = state.filesToUpload.length === 0;
    
    // Feedback visuel
    const placeholder = document.querySelector('.upload-placeholder p');
    if (placeholder) {
        placeholder.textContent = `${state.filesToUpload.length} fichier(s) sélectionné(s)`;
    }
}

/**
 * Uploader les images
 */
async function uploadImages() {
    if (!state.selectedTradeId || state.filesToUpload.length === 0) return;

    const imageType = document.getElementById('upload-image-type').value;
    const btn = document.getElementById('upload-btn');
    
    btn.disabled = true;
    btn.textContent = 'Upload...';

    try {
        await API.uploadImages(state.selectedTradeId, state.filesToUpload, imageType);
        showNotification('Images uploadées avec succès', 'success');
        
        // Reset
        state.filesToUpload = [];
        document.getElementById('image-input').value = '';
        document.querySelector('.upload-placeholder p').textContent = 'Cliquez ou glissez des images ici';
        
        // Recharger la galerie
        await loadTradeImages(state.selectedTradeId);
    } catch (error) {
        showNotification(`Erreur: ${error.message}`, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Uploader';
    }
}

/**
 * Supprimer une image
 */
async function deleteImage(imageId) {
    if (!confirm('Supprimer cette image ?')) return;

    try {
        await API.deleteImage(imageId);
        showNotification('Image supprimée', 'success');
        await loadTradeImages(state.selectedTradeId);
    } catch (error) {
        showNotification(`Erreur: ${error.message}`, 'error');
    }
}

/**
 * Ouvrir une image en plein écran
 */
function openFullImage(url) {
    window.open(url, '_blank');
}

// ==================== TRADE DETAIL MODAL ====================

/**
 * Voir le détail d'un trade
 */
async function viewTradeDetail(tradeId) {
    try {
        const trade = await API.getTrade(tradeId);
        renderTradeDetail(trade);
        document.getElementById('detail-modal').classList.add('active');
    } catch (error) {
        showNotification('Erreur de chargement', 'error');
    }
}

/**
 * Fermer le modal de détail
 */
function closeDetailModal() {
    document.getElementById('detail-modal').classList.remove('active');
}

/**
 * Afficher le détail d'un trade
 */
function renderTradeDetail(trade) {
    const content = document.getElementById('detail-content');
    
    content.innerHTML = `
        <div class="trade-detail">
            <div class="trade-detail-group">
                <h3>Informations</h3>
                <div class="trade-detail-item">
                    <label>Date</label>
                    <span>${formatDate(trade.date)}</span>
                </div>
                <div class="trade-detail-item">
                    <label>Instrument</label>
                    <span>${trade.instrument}</span>
                </div>
                <div class="trade-detail-item">
                    <label>Session</label>
                    <span>${trade.session}</span>
                </div>
                <div class="trade-detail-item">
                    <label>Setup</label>
                    <span>${trade.setup}</span>
                </div>
                <div class="trade-detail-item">
                    <label>Direction</label>
                    <span class="badge badge-${trade.direction.toLowerCase()}">${trade.direction}</span>
                </div>
                <div class="trade-detail-item">
                    <label>Timeframe</label>
                    <span>${trade.timeframe}</span>
                </div>
            </div>

            <div class="trade-detail-group">
                <h3>Niveaux</h3>
                <div class="trade-detail-item">
                    <label>Entry</label>
                    <span>${trade.entry}</span>
                </div>
                <div class="trade-detail-item">
                    <label>Stop Loss</label>
                    <span>${trade.stop_loss}</span>
                </div>
                <div class="trade-detail-item">
                    <label>Take Profit</label>
                    <span>${trade.take_profit || '-'}</span>
                </div>
                <div class="trade-detail-item">
                    <label>Risk %</label>
                    <span>${trade.risk_pct}%</span>
                </div>
                <div class="trade-detail-item">
                    <label>Risk USD</label>
                    <span>$${trade.risk_usd}</span>
                </div>
                <div class="trade-detail-item">
                    <label>RR Attendu</label>
                    <span>${trade.rr_expected}</span>
                </div>
            </div>

            <div class="trade-detail-group">
                <h3>Résultats</h3>
                <div class="trade-detail-item">
                    <label>Résultat (R)</label>
                    <span class="${getResultClass(trade.result_r)}">${formatResult(trade.result_r)}</span>
                </div>
                <div class="trade-detail-item">
                    <label>P&L</label>
                    <span class="${getResultClass(trade.pnl_usd)}">${formatPnL(trade.pnl_usd)}</span>
                </div>
                <div class="trade-detail-item">
                    <label>Durée</label>
                    <span>${trade.duration_min ? `${trade.duration_min} min` : '-'}</span>
                </div>
                <div class="trade-detail-item">
                    <label>Plan respecté</label>
                    <span class="badge ${trade.respected_plan ? 'badge-success' : 'badge-danger'}">${trade.respected_plan ? 'Oui' : 'Non'}</span>
                </div>
                <div class="trade-detail-item">
                    <label>Erreur</label>
                    <span>${trade.error ? trade.error_type : 'Non'}</span>
                </div>
                <div class="trade-detail-item">
                    <label>État mental</label>
                    <span>${trade.mental_state || '-'}/5</span>
                </div>
            </div>

            ${trade.notes ? `
                <div class="trade-detail-group" style="grid-column: 1 / -1;">
                    <h3>Notes</h3>
                    <p>${trade.notes}</p>
                </div>
            ` : ''}

            ${trade.images && trade.images.length > 0 ? `
                <div class="trade-detail-images">
                    <h3>Images (${trade.images.length})</h3>
                    <div class="images-gallery">
                        ${trade.images.map(img => {
                            const imgUrl = getImageUrl(img.image_url);
                            return `
                            <div class="image-card">
                                <img src="${imgUrl}" alt="${img.image_type}" onclick="openFullImage('${imgUrl}')">
                                <div class="image-card-overlay">
                                    <span class="image-type-badge">${img.image_type}</span>
                                </div>
                            </div>
                        `;
                        }).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

// ==================== UTILITIES ====================

/**
 * Obtenir l'URL complète d'une image
 * Gère les URLs Supabase (complètes) et locales (relatives)
 */
function getImageUrl(imageUrl) {
    // Si c'est déjà une URL complète (Supabase), la retourner telle quelle
    if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
        return imageUrl;
    }
    // Sinon, c'est une URL locale, ajouter le BASE_URL
    return `${CONFIG.API_BASE_URL}${imageUrl}`;
}

/**
 * Formater une date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString(CONFIG.DATE_FORMAT, CONFIG.DATETIME_FORMAT);
}

/**
 * Formater le résultat en R
 */
function formatResult(value) {
    if (value === null || value === undefined) return '-';
    const sign = value > 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}R`;
}

/**
 * Formater le P&L
 */
function formatPnL(value) {
    if (value === null || value === undefined) return '-';
    const sign = value > 0 ? '+' : '';
    return `${sign}$${value.toFixed(2)}`;
}

/**
 * Obtenir la classe CSS pour un résultat
 */
function getResultClass(value) {
    if (value === null || value === undefined) return 'cell-neutral';
    if (value > 0) return 'cell-positive';
    if (value < 0) return 'cell-negative';
    return 'cell-neutral';
}

/**
 * Afficher une notification
 */
function showNotification(message, type = 'success') {
    // Supprimer les notifications existantes
    document.querySelectorAll('.notification').forEach(n => n.remove());

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}
