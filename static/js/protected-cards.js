/**
 * protected-cards.js
 * ─────────────────────────────────────────────────────────────────────────
 * Gère l'affichage visuel des cartes protégées.
 * 
 * Deux approches sont traitées :
 * 1. Cartes HTML classiques (.game-card) : attribut data-protected
 * 2. Web Components <game-card> : attribut 'protected'
 */

/**
 * Ajoute l'attribut 'protected' aux game-card (Web Components)
 * en fonction du flag is_protected dans le JSON de données.
 */
function initProtectedCards() {
  // Traiter les <game-card> Web Components
  document.querySelectorAll('game-card[data-card]').forEach((el) => {
    try {
      const cardData = JSON.parse(el.getAttribute('data-card') || '{}');
      if (cardData.is_protected) {
        el.setAttribute('protected', '');
      }
    } catch (err) {
      console.warn('Failed to parse card data:', err);
    }
  });

  // Traiter les .game-card HTML classiques
  document.querySelectorAll('.game-card[data-card]').forEach((el) => {
    try {
      const cardData = JSON.parse(el.getAttribute('data-card') || '{}');
      if (cardData.is_protected) {
        el.setAttribute('data-protected', 'true');
      } else {
        el.removeAttribute('data-protected');
      }
    } catch (err) {
      console.warn('Failed to parse card data:', err);
    }
  });
}

/**
 * Observer pour détecter quand de nouvelles cartes sont ajoutées au DOM.
 * Cela permet de mettre à jour les styles de protection dynamiquement.
 */
function observeCardUpdates() {
  const observer = new MutationObserver((mutations) => {
    let needsUpdate = false;
    mutations.forEach((mutation) => {
      if (
        mutation.type === 'childList' ||
        (mutation.type === 'attributes' &&
          (mutation.attributeName === 'data-card' ||
           mutation.attributeName === 'data-protected' ||
           mutation.attributeName === 'protected'))
      ) {
        needsUpdate = true;
      }
    });
    if (needsUpdate) {
      initProtectedCards();
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['data-card', 'data-protected', 'protected'],
  });

  return observer;
}

/**
 * Exporte une fonction pour mettre à jour manuellement une carte spécifique.
 * Utile après une action asynchrone.
 */
window.updateProtectedCard = function (cardId, isProtected) {
  // Web Components
  document.querySelectorAll(`game-card[card-id="${cardId}"]`).forEach((el) => {
    if (isProtected) {
      el.setAttribute('protected', '');
    } else {
      el.removeAttribute('protected');
    }
  });

  // HTML classiques
  document.querySelectorAll(`.game-card[data-card]`).forEach((el) => {
    try {
      const cardData = JSON.parse(el.getAttribute('data-card') || '{}');
      if (cardData.id == cardId) {
        if (isProtected) {
          el.setAttribute('data-protected', 'true');
        } else {
          el.removeAttribute('data-protected');
        }
      }
    } catch (err) {
      console.warn('Failed to update card:', err);
    }
  });
};

// Initialiser au chargement
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initProtectedCards();
    observeCardUpdates();
  });
} else {
  initProtectedCards();
  observeCardUpdates();
}