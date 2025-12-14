/**
 * Gestionnaire du rendu des cartes
 * Séparation complète de la logique d'affichage
 */
class CardRenderer {
    constructor() {
        this.colors = {
            'job': 'bg-blue-100 border-blue-300',
            'study': 'bg-blue-100 border-blue-300',
            'salary': 'bg-blue-100 border-blue-300',
            'flirt': 'bg-pink-100 border-pink-300',
            'marriage': 'bg-pink-100 border-pink-300',
            'child': 'bg-pink-100 border-pink-300',
            'animal': 'bg-pink-100 border-pink-300',
            'adultere': 'bg-pink-100 border-pink-300',
            'house': 'bg-green-100 border-green-300',
            'travel': 'bg-green-100 border-green-300',
            'hardship': 'bg-red-100 border-red-300',
            'special': 'bg-yellow-100 border-yellow-300',
            'other': 'bg-purple-100 border-purple-300'
        };
        
        this.icons = {
            'job': '💼', 'study': '📚', 'salary': '💰',
            'flirt': '💕', 'marriage': '💍', 'child': '👶',
            'animal': '🐾', 'adultere': '💔', 'house': '🏠',
            'travel': '✈️', 'hardship': '⚠️', 'special': '⭐', 'other': '🎖'
        };
    }
    
    /**
     * Génère le HTML d'une carte
     */
    render(card, options = {}) {
        const {
            canPlay = false,
            canDiscard = false,
            isSmall = false,
            showRules = true,
            onPlay = null,
            onDiscard = null
        } = options;
        
        const label = this.getLabel(card);
        const color = this.colors[card.type] || 'bg-gray-100 border-gray-300';
        const icon = this.icons[card.type] || '🎴';
        const imagePath = card.image ? `/ressources/${card.image}` : '';
        const sizeClass = isSmall ? 'min-w-[100px]' : 'min-w-[140px]';
        const cardId = `card-${card.id}`;
        
        // Gestion du clic pour afficher les règles
        const onClickHandler = showRules && card.rule 
            ? `onclick="window.gameController.ui.modals.showCardRules('${this.escapeHtml(label)}', '${this.escapeHtml(card.rule)}', '${imagePath}')"`
            : '';
        
        return `
            <div class="card ${color} border-2 rounded-lg ${sizeClass} overflow-hidden" 
                 style="height: 200px;" 
                 ${onClickHandler}>
                ${imagePath ? 
                    this.renderWithImage(card, cardId, label, icon, imagePath, canPlay, canDiscard, onPlay, onDiscard) :
                    this.renderTextOnly(card, label, icon, canPlay, canDiscard, onPlay, onDiscard)
                }
            </div>
        `;
    }
    
    /**
     * Rendu avec image
     */
    renderWithImage(card, cardId, label, icon, imagePath, canPlay, canDiscard, onPlay, onDiscard) {
        return `
            <div id="${cardId}" class="card-content h-full w-full relative">
                <!-- Image -->
                <div class="card-image-container h-full w-full flex flex-col relative">
                    <img src="${imagePath}" 
                         alt="${label}" 
                         class="w-full h-full object-contain rounded"
                         onerror="handleImageError('${cardId}')">
                    
                    <!-- Indicateur règles -->
                    ${card.rule ? `
                        <div class="absolute top-2 right-2 bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold shadow-lg">
                            ℹ️
                        </div>
                    ` : ''}
                    
                    <!-- Boutons d'action -->
                    ${this.renderActionButtons(card, canPlay, canDiscard, onPlay, onDiscard)}
                </div>
                
                <!-- Fallback texte -->
                <div class="card-text-fallback hidden h-full w-full flex flex-col justify-between p-3">
                    ${this.renderCardInfo(card, label, icon)}
                    ${this.renderActionButtons(card, canPlay, canDiscard, onPlay, onDiscard)}
                </div>
            </div>
        `;
    }
    
    /**
     * Rendu texte uniquement
     */
    renderTextOnly(card, label, icon, canPlay, canDiscard, onPlay, onDiscard) {
        return `
            <div class="p-3 h-full flex flex-col justify-between">
                ${this.renderCardInfo(card, label, icon)}
                ${this.renderActionButtons(card, canPlay, canDiscard, onPlay, onDiscard)}
            </div>
        `;
    }
    
    /**
     * Informations de la carte
     */
    renderCardInfo(card, label, icon) {
        return `
            <div>
                <div class="flex items-center gap-2 mb-1">
                    <span>${icon}</span>
                    <span class="font-semibold text-sm">${label}</span>
                </div>
                ${card.smiles > 0 ? `
                    <div class="flex items-center gap-1 text-yellow-600">
                        <span>😊</span>
                        <span class="text-sm">${card.smiles}</span>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    /**
     * Boutons d'action
     */
    renderActionButtons(card, canPlay, canDiscard, onPlay, onDiscard) {
        if (!canPlay && !canDiscard) return '';
        
        const playButtonText = card.type === 'hardship' ? 'Attaquer' :
                              card.type === 'special' ? '⭐ Activer' : 'Jouer';
        
        const playButtonColor = card.type === 'hardship' ? 'bg-red-500 hover:bg-red-600' :
                               card.type === 'special' ? 'bg-yellow-500 hover:bg-yellow-600' :
                               'bg-green-500 hover:bg-green-600';
        
        const discardButtonText = card.status === 'intérimaire' && card.type === 'job' 
            ? '👋 Démissionner' 
            : '🗑️ Défausser';
        
        return `
            <div class="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/70 to-transparent">
                ${canPlay ? `
                    <div class="flex gap-1">
                        <button onclick="event.stopPropagation(); ${onPlay ? `window.gameController.playCard('${card.id}')` : ''}" 
                                class="flex-1 ${playButtonColor} text-white text-xs px-2 py-1 rounded font-semibold shadow-lg">
                            ${playButtonText}
                        </button>
                        <button onclick="event.stopPropagation(); ${onDiscard ? `window.gameController.discardCard('${card.id}')` : ''}" 
                                class="flex-1 bg-gray-500 text-white text-xs px-2 py-1 rounded hover:bg-gray-600 font-semibold shadow-lg">
                            Défausser
                        </button>
                    </div>
                ` : ''}
                ${canDiscard && !canPlay ? `
                    <button onclick="event.stopPropagation(); ${onDiscard ? `window.gameController.discardPlayedCard('${card.id}')` : ''}" 
                            class="w-full bg-red-500 text-white text-xs px-2 py-1 rounded hover:bg-red-600 font-semibold shadow-lg">
                        ${discardButtonText}
                    </button>
                ` : ''}
            </div>
        `;
    }
    
    /**
     * Rendu du casino
     */
    renderCasino(casinoState, isMyTurn) {
        const container = document.getElementById('casino-section');
        if (!casinoState.open) {
            container.classList.add('hidden');
            return;
        }
        
        container.classList.remove('hidden');
        
        document.getElementById('casino-first-bet-display').innerHTML = 
            casinoState.first_bet ? this.renderCasinoBet(casinoState.first_bet) :
            '<p class="text-sm italic">En attente...</p>';
        
        document.getElementById('casino-second-bet-display').innerHTML =
            casinoState.second_bet ? this.renderCasinoBet(casinoState.second_bet) :
            '<p class="text-sm italic">En attente...</p>';
        
        // Bouton de pari
        const betButton = document.getElementById('casino-bet-button-container');
        if (isMyTurn && (!casinoState.first_bet || !casinoState.second_bet)) {
            betButton.classList.remove('hidden');
        } else {
            betButton.classList.add('hidden');
        }
    }
    
    renderCasinoBet(bet) {
        return `
            <div class="text-2xl mb-2">🎰</div>
            <div class="font-bold text-xl">${bet.name}</div>
            <div class="text-xs mt-1 text-yellow-300">Montant secret</div>
        `;
    }
    
    /**
     * Obtient le label d'une carte
     */
    getLabel(card) {
        if (card.type === 'job') return card.subtype;
        if (card.type === 'study') return card.subtype === 'double' ? 'Études x2' : 'Études';
        if (card.type === 'salary') return `Salaire ${card.subtype}`;
        if (card.type === 'flirt') return `Flirt (${card.subtype})`;
        if (card.type === 'marriage') return `Mariage (${card.subtype})`;
        if (card.type === 'child') return card.subtype;
        if (card.type === 'animal') return card.subtype;
        if (card.type === 'house') return `Maison ${card.subtype}`;
        if (card.type === 'travel') return 'Voyage';
        if (card.type === 'hardship') return card.subtype;
        if (card.type === 'special') return card.subtype;
        if (card.type === 'adultere') return 'Adultère';
        if (card.type === 'other') {
            if (card.subtype === 'legion') return "Légion d'honneur";
            if (card.subtype === 'prix') return 'Grand Prix';
        }
        return 'Carte';
    }
    
    /**
     * Échappe les caractères HTML
     */
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;',
            '\\': '\\\\',
            '\n': '\\n'
        };
        return text.replace(/[&<>"'\\\n]/g, m => map[m]);
    }
}

// Fonction globale pour gérer les erreurs d'image
window.handleImageError = function(cardElementId) {
    const cardElement = document.getElementById(cardElementId);
    if (cardElement) {
        const imageContainer = cardElement.querySelector('.card-image-container');
        const textFallback = cardElement.querySelector('.card-text-fallback');
        
        if (imageContainer) imageContainer.classList.add('hidden');
        if (textFallback) textFallback.classList.remove('hidden');
    }
};

window.CardRenderer = CardRenderer;