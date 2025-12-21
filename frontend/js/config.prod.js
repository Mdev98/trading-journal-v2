/**
 * Configuration de l'application - PRODUCTION
 * Remplacer l'URL par celle de votre backend Render
 */
const CONFIG = {
    // URL de l'API backend sur Render
    // Remplacez par votre URL Render après déploiement
    API_BASE_URL: 'https://trading-journal-api.onrender.com',
    
    // Nombre de trades par page
    PAGE_SIZE: 20,
    
    // Formats de date
    DATE_FORMAT: 'fr-FR',
    DATETIME_FORMAT: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }
};

// Freeze pour éviter les modifications accidentelles
Object.freeze(CONFIG);
