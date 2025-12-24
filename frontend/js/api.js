    /**
     * Login owner
     */
    async loginOwner(password) {
        const formData = new FormData();
        formData.append('password', password);
        const response = await fetch(`${CONFIG.API_BASE_URL}/login`, {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'Login owner échoué');
        }
        return data;
    },
/**
 * API Client - Communication avec le backend FastAPI
 * Toutes les fonctions retournent des Promises
 */

const API = {
    /**
     * Requête HTTP générique
     */
    async request(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const method = (options.method || 'GET').toUpperCase();
        const defaultHeaders = {
            'Content-Type': 'application/json',
        };
        const defaultOptions = {
            headers: {
                ...defaultHeaders,
                ...(options.headers || {})
            },
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            // Gérer les réponses sans contenu (204)
            if (response.status === 204) {
                return null;
            }
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || `HTTP error ${response.status}`);
            }
            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    },

    // ==================== TRADES ====================

    /**
     * Créer un nouveau trade
     */
    async createTrade(tradeData) {
        return this.request('/trades', {
            method: 'POST',
            body: JSON.stringify(tradeData),
        });
    },

    /**
     * Récupérer la liste des trades avec pagination et filtres
     */
    async getTrades(params = {}) {
        const queryParams = new URLSearchParams();
        
        if (params.page) queryParams.append('page', params.page);
        if (params.pageSize) queryParams.append('page_size', params.pageSize);
        if (params.instrument) queryParams.append('instrument', params.instrument);
        if (params.session) queryParams.append('session', params.session);
        if (params.setup) queryParams.append('setup', params.setup);
        if (params.direction) queryParams.append('direction', params.direction);
        if (params.dateFrom) queryParams.append('date_from', params.dateFrom);
        if (params.dateTo) queryParams.append('date_to', params.dateTo);
        if (params.isWinner !== undefined) queryParams.append('is_winner', params.isWinner);

        const queryString = queryParams.toString();
        return this.request(`/trades${queryString ? '?' + queryString : ''}`);
    },

    /**
     * Récupérer un trade par ID
     */
    async getTrade(tradeId) {
        return this.request(`/trades/${tradeId}`);
    },

    /**
     * Mettre à jour un trade
     */
    async updateTrade(tradeId, tradeData) {
        return this.request(`/trades/${tradeId}`, {
            method: 'PUT',
            body: JSON.stringify(tradeData),
        });
    },

    /**
     * Supprimer un trade
     */
    async deleteTrade(tradeId) {
        return this.request(`/trades/${tradeId}`, {
            method: 'DELETE',
        });
    },

    /**
     * Récupérer les options de filtrage
     */
    async getFilterOptions() {
        return this.request('/trades/filters');
    },

    // ==================== IMAGES ====================

    /**
     * Uploader des images pour un trade
     */
    async uploadImages(tradeId, files, imageType = 'analysis') {
        const formData = new FormData();
        
        for (const file of files) {
            formData.append('files', file);
        }
        formData.append('image_type', imageType);


        const url = `${CONFIG.API_BASE_URL}/trades/${tradeId}/images`;
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        return response.json();
    },

    /**
     * Récupérer les images d'un trade
     */
    async getTradeImages(tradeId) {
        return this.request(`/trades/${tradeId}/images`);
    },

    /**
     * Supprimer une image
     */
    async deleteImage(imageId) {
        return this.request(`/trades/images/${imageId}`, {
            method: 'DELETE',
        });
    },

    // ==================== STATISTICS ====================

    /**
     * Récupérer les statistiques globales
     */
    async getGlobalStats(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.dateFrom) queryParams.append('date_from', params.dateFrom);
        if (params.dateTo) queryParams.append('date_to', params.dateTo);
        if (params.instrument) queryParams.append('instrument', params.instrument);
        if (params.setup) queryParams.append('setup', params.setup);

        const queryString = queryParams.toString();
        return this.request(`/stats/global${queryString ? '?' + queryString : ''}`);
    },

    /**
     * Statistiques par setup
     */
    async getStatsBySetup(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.dateFrom) queryParams.append('date_from', params.dateFrom);
        if (params.dateTo) queryParams.append('date_to', params.dateTo);

        const queryString = queryParams.toString();
        return this.request(`/stats/by-setup${queryString ? '?' + queryString : ''}`);
    },

    /**
     * Statistiques par session
     */
    async getStatsBySession(params = {}) {
        const queryParams = new URLSearchParams();
        if (params.dateFrom) queryParams.append('date_from', params.dateFrom);
        if (params.dateTo) queryParams.append('date_to', params.dateTo);

        const queryString = queryParams.toString();
        return this.request(`/stats/by-session${queryString ? '?' + queryString : ''}`);
    },

    /**
     * Statistiques journalières
     */
    async getDailyStats(days = 30) {
        return this.request(`/stats/daily?days=${days}`);
    },

    /**
     * Statistiques hebdomadaires
     */
    async getWeeklyStats(weeks = 12) {
        return this.request(`/stats/weekly?weeks=${weeks}`);
    },

    /**
     * Statistiques des erreurs
     */
    async getErrorStats() {
        return this.request('/stats/errors');
    },

    /**
     * Corrélation état mental
     */
    async getMentalStats() {
        return this.request('/stats/mental');
    },

    /**
     * Courbe d'equity
     */
    async getEquityCurve() {
        return this.request('/stats/equity-curve');
    },
};
