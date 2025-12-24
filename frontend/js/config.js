/**
 * Configuration de l'application
 * Modifier API_BASE_URL selon l'environnement
 */
const CONFIG = {
    // URL de l'API backend
    // Dev: http://localhost:8000
    // Prod: https://votre-app.onrender.com
    API_BASE_URL: 'http://localhost:8000',
    // Plus de clé API côté frontend
    
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
