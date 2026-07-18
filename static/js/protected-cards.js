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
      const shouldBeProtected = !!cardData.is_protected;
      const isCurrentlyProtected = el.hasAttribute('protected');
      // On n'écrit l'attribut que si sa valeur doit réellement changer,
      // sinon on redéclenche inutilement le MutationObserver.
      if (shouldBeProtected && !isCurrentlyProtected) {
        el.setAttribute('protected', '');
      } else if (!shouldBeProtected && isCurrentlyProtected) {
        el.removeAttribute('protected');
      }
    } catch (err) {
      console.warn('Failed to parse card data:', err);
    }
  });

  // Traiter les .game-card HTML classiques
  document.querySelectorAll('.game-card[data-card]').forEach((el) => {
    try {
      const cardData = JSON.parse(el.getAttribute('data-card') || '{}');
      const shouldBeProtected = !!cardData.is_protected;
      const isCurrentlyProtected = el.getAttribute('data-protected') === 'true';
      if (shouldBeProtected && !isCurrentlyProtected) {
        el.setAttribute('data-protected', 'true');
      } else if (!shouldBeProtected && isCurrentlyProtected) {
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
    for (const mutation of mutations) {
      if (mutation.type === 'childList') {
        needsUpdate = true;
        break;
      }
      if (mutation.type === 'attributes' && mutation.attributeName === 'data-card') {
        needsUpdate = true;
        break;
      }
    }
    if (needsUpdate) {
      scheduleUpdate();
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    // On ne surveille QUE 'data-card' : c'est la source de vérité.
    // 'protected' / 'data-protected' sont des attributs qu'on écrit
    // nous-mêmes ; les observer créerait une boucle de rétroaction
    // (mutation -> initProtectedCards -> setAttribute -> mutation -> ...).
    attributeFilter: ['data-card'],
  });

  return observer;
}

/**
 * Regroupe les mises à jour rafales (ex: plusieurs cartes ajoutées d'un coup)
 * en un seul passage, plutôt que de relancer initProtectedCards pour
 * chaque mutation individuelle.
 */
let updateScheduled = false;
function scheduleUpdate() {
  if (updateScheduled) return;
  updateScheduled = true;
  requestAnimationFrame(() => {
    updateScheduled = false;
    initProtectedCards();
  });
}

/**
 * Exporte une fonction pour mettre à jour manuellement une carte spécifique.
 * Utile après une action asynchrone.
 */
window.updateProtectedCard = function (cardId, isProtected) {
  // Web Components
  document.querySelectorAll(`game-card[card-id="${cardId}"]`).forEach((el) => {
    const isCurrentlyProtected = el.hasAttribute('protected');
    if (isProtected && !isCurrentlyProtected) {
      el.setAttribute('protected', '');
    } else if (!isProtected && isCurrentlyProtected) {
      el.removeAttribute('protected');
    }
  });

  // HTML classiques
  document.querySelectorAll(`.game-card[data-card]`).forEach((el) => {
    try {
      const cardData = JSON.parse(el.getAttribute('data-card') || '{}');
      if (cardData.id == cardId) {
        const isCurrentlyProtected = el.getAttribute('data-protected') === 'true';
        if (isProtected && !isCurrentlyProtected) {
          el.setAttribute('data-protected', 'true');
        } else if (!isProtected && isCurrentlyProtected) {
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