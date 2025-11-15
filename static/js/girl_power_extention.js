// #########################
// dragon et daenerys
// #########################
function showBurnCardModal(targetPlayerName, availableCards) {
    console.log('[DEBUG] Available cards:', availableCards);
    
    const modal = document.getElementById('burn-card-modal');
    const message = document.getElementById('burn-target-message');
    const cardsList = document.getElementById('burn-cards-list');
    
    message.innerHTML = `Choisissez une carte de <span class="font-bold text-red-600">${targetPlayerName}</span> à détruire`;
    
    // ✅ Utiliser createCardHTML() existant
    cardsList.innerHTML = availableCards.map(card => `
        <div class="burn-card-wrapper" data-card-id="${card.id}">
            ${createCardHTML(card, false, false, false, false)}
        </div>
    `).join('');
    
    // ✅ Ajouter les événements onclick après insertion dans le DOM
    availableCards.forEach(card => {
        const wrapper = cardsList.querySelector(`[data-card-id="${card.id}"]`);
        if (wrapper) {
            wrapper.style.cursor = 'pointer';
            wrapper.onclick = () => selectBurnTarget(card.id);
            
            // Ajouter un effet hover
            wrapper.onmouseenter = () => {
                wrapper.style.transform = 'scale(1.05)';
                wrapper.style.transition = 'transform 0.2s';
            };
            wrapper.onmouseleave = () => {
                wrapper.style.transform = 'scale(1)';
            };
        }
    });
    
    modal.classList.remove('hidden');
}

function discardBurnSelection() {
    socket.emit('discard_Burn_target_selection', {
        card_id: card_id});
    closeBurnModal();
}

function selectBurnTarget(targetId) {
    log("Burn_target_selected")
    socket.emit('Burn_target_selected', {
        card_id: card_id,  
        target_card_id: targetId });
    closeBurnModal();
}

function closeBurnModal() {
    document.getElementById('burn-card-modal').classList.add('hidden');
}

socket.on('select_burn_card', (data) => {
    log('Burn - sélection cible', data);
    card_id = data.card_id;
    showBurnCardModal(data.player_name, data.available_targets);
});

// ################################
// Erreur D'étiquetage
// ################################
let etiquetageCardId = null;
let etiquetageTargetPlayerId = null;
let etiquetageTargetPlayerName = null;
let etiquetageSelectedCurrentChild = null;
let etiquetageSelectedTargetChild = null;

/**
 * Affiche la modal de sélection du joueur cible
 */
function showEtiquetageTargetModal(targets) {
    console.log("[showEtiquetageTargetModal]", targets);
    
    const modal = document.getElementById('etiquetage-target-modal');
    const targetsList = document.getElementById('etiquetage-targets-list');
    
    // Générer la liste des joueurs
    targetsList.innerHTML = targets.map(target => {
        const isImmune = target.immune || false;
        const buttonClass = isImmune 
            ? 'w-full p-4 bg-gray-400 text-gray-700 rounded-lg cursor-not-allowed opacity-50' 
            : 'w-full p-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all transform hover:scale-105 font-semibold shadow-lg';
        const onClick = isImmune ? '' : `onclick="selectEtiquetageTarget('${target.id}', '${target.name.replace(/'/g, "\\'")}')"`;
        const immuneText = isImmune ? ' 🛡️ (Pas d\'enfants)' : '';
        
        return `
            <button ${onClick} ${isImmune ? 'disabled' : ''} 
                    class="${buttonClass}">
                🎯 ${target.name}${immuneText}
            </button>
        `;
    }).join('');
    
    modal.classList.remove('hidden');
}

/**
 * Sélectionne un joueur cible et passe à la page suivante
 */
function selectEtiquetageTarget(targetId, targetName) {
    console.log("[selectEtiquetageTarget]", targetId, targetName);
    
    etiquetageTargetPlayerId = parseInt(targetId);
    etiquetageTargetPlayerName = targetName;
    
    // Émettre l'événement au serveur
    socket.emit('erreur_etiquetage_target_selected', {
        card_id: etiquetageCardId,
        target_id: etiquetageTargetPlayerId
    });
    
    closeEtiquetageTargetModal();
}

/**
 * Annule la sélection du joueur cible
 */
function discardEtiquetageTargetSelection() {
    console.log("[discardEtiquetageTargetSelection]");
    
    socket.emit('erreur_etiquetage_discard', {
        card_id: etiquetageCardId
    });
    
    closeEtiquetageTargetModal();
}

/**
 * Ferme la modal de sélection du joueur cible
 */
function closeEtiquetageTargetModal() {
    document.getElementById('etiquetage-target-modal').classList.add('hidden');
    etiquetageTargetPlayerId = null;
    etiquetageTargetPlayerName = null;
}

/**
 * Affiche la modal de sélection des enfants à échanger
 */
function showEtiquetageChildrenModal(currentChildren, targetChildren, targetName) {
    console.log("[showEtiquetageChildrenModal]", currentChildren, targetChildren);
    
    const modal = document.getElementById('etiquetage-children-modal');
    const currentList = document.getElementById('etiquetage-current-children-list');
    const targetList = document.getElementById('etiquetage-target-children-list');
    const targetNameSpan = document.getElementById('etiquetage-target-name');
    
    // Réinitialiser les sélections
    etiquetageSelectedCurrentChild = null;
    etiquetageSelectedTargetChild = null;
    
    // Afficher le nom du joueur cible
    targetNameSpan.textContent = targetName;
    
    // Générer la liste des enfants du joueur courant
    currentList.innerHTML = currentChildren.map(child => `
        <div onclick="toggleCurrentChildSelection('${child.id}')" 
             id="current-child-${child.id}"
             class="etiquetage-child-selectable p-3 bg-blue-100 border-2 border-blue-300 rounded-lg text-center hover:bg-blue-200">
            <div class="text-2xl mb-1">👶</div>
            <div class="font-bold">${child.subtype}</div>
        </div>
    `).join('');
    
    // Générer la liste des enfants du joueur cible
    targetList.innerHTML = targetChildren.map(child => `
        <div onclick="toggleTargetChildSelection('${child.id}')" 
             id="target-child-${child.id}"
             class="etiquetage-child-selectable p-3 bg-red-100 border-2 border-red-300 rounded-lg text-center hover:bg-red-200">
            <div class="text-2xl mb-1">👶</div>
            <div class="font-bold">${child.subtype}</div>
        </div>
    `).join('');
    
    updateEtiquetageValidation();
    modal.classList.remove('hidden');
}

/**
 * Toggle la sélection d'un enfant du joueur courant
 */
function toggleCurrentChildSelection(childId) {
    console.log("[toggleCurrentChildSelection]", childId);
    
    // Désélectionner l'ancien enfant s'il existe
    if (etiquetageSelectedCurrentChild) {
        const oldElement = document.getElementById(`current-child-${etiquetageSelectedCurrentChild}`);
        if (oldElement) {
            oldElement.classList.remove('etiquetage-child-selected');
        }
    }
    
    // Si on clique sur le même enfant, on le désélectionne
    if (etiquetageSelectedCurrentChild === childId) {
        etiquetageSelectedCurrentChild = null;
    } else {
        // Sélectionner le nouvel enfant
        etiquetageSelectedCurrentChild = childId;
        const newElement = document.getElementById(`current-child-${childId}`);
        if (newElement) {
            newElement.classList.add('etiquetage-child-selected');
        }
    }
    
    updateEtiquetageValidation();
}

/**
 * Toggle la sélection d'un enfant du joueur cible
 */
function toggleTargetChildSelection(childId) {
    console.log("[toggleTargetChildSelection]", childId);
    
    // Désélectionner l'ancien enfant s'il existe
    if (etiquetageSelectedTargetChild) {
        const oldElement = document.getElementById(`target-child-${etiquetageSelectedTargetChild}`);
        if (oldElement) {
            oldElement.classList.remove('etiquetage-child-selected');
        }
    }
    
    // Si on clique sur le même enfant, on le désélectionne
    if (etiquetageSelectedTargetChild === childId) {
        etiquetageSelectedTargetChild = null;
    } else {
        // Sélectionner le nouvel enfant
        etiquetageSelectedTargetChild = childId;
        const newElement = document.getElementById(`target-child-${childId}`);
        if (newElement) {
            newElement.classList.add('etiquetage-child-selected');
        }
    }
    
    updateEtiquetageValidation();
}

/**
 * Met à jour l'état de validation (active/désactive le bouton confirmer)
 */
function updateEtiquetageValidation() {
    const confirmBtn = document.getElementById('etiquetage-confirm-btn');
    const messageEl = document.getElementById('etiquetage-validation-message');
    
    // Vérifier si les deux enfants sont sélectionnés
    const bothSelected = etiquetageSelectedCurrentChild && etiquetageSelectedTargetChild;
    
    if (bothSelected) {
        confirmBtn.disabled = false;
        messageEl.innerHTML = '<span class="text-green-600 font-semibold">✅ Prêt à échanger !</span>';
    } else {
        confirmBtn.disabled = true;
        if (!etiquetageSelectedCurrentChild && !etiquetageSelectedTargetChild) {
            messageEl.innerHTML = '<span class="text-orange-600">Sélectionnez un enfant dans chaque liste</span>';
        } else if (!etiquetageSelectedCurrentChild) {
            messageEl.innerHTML = '<span class="text-orange-600">Sélectionnez un de vos enfants</span>';
        } else {
            messageEl.innerHTML = '<span class="text-orange-600">Sélectionnez un enfant de la cible</span>';
        }
    }
}

/**
 * Confirme la sélection des enfants et envoie au serveur
 */
function confirmEtiquetageChildrenSelection() {
    console.log("[confirmEtiquetageChildrenSelection]", etiquetageSelectedCurrentChild, etiquetageSelectedTargetChild);
    
    if (!etiquetageSelectedCurrentChild || !etiquetageSelectedTargetChild) {
        alert('Veuillez sélectionner un enfant dans chaque liste');
        return;
    }
    
    socket.emit('erreur_etiquetage_children_selected', {
        card_id: etiquetageCardId,
        current_child_id: etiquetageSelectedCurrentChild,
        target_child_id: etiquetageSelectedTargetChild
    });
    
    closeEtiquetageChildrenModal();
}

/**
 * Annule la sélection des enfants
 */
function discardEtiquetageChildrenSelection() {
    console.log("[discardEtiquetageChildrenSelection]");
    
    socket.emit('erreur_etiquetage_discard', {
        card_id: etiquetageCardId
    });
    
    closeEtiquetageChildrenModal();
}

/**
 * Ferme la modal de sélection des enfants
 */
function closeEtiquetageChildrenModal() {
    document.getElementById('etiquetage-children-modal').classList.add('hidden');
    etiquetageSelectedCurrentChild = null;
    etiquetageSelectedTargetChild = null;
}

/**
 * Réception de la demande de sélection du joueur cible
 */
socket.on('select_etiquetage_target', (data) => {
    console.log('[select_etiquetage_target]', data);
    etiquetageCardId = data.card_id;
    showEtiquetageTargetModal(data.targets);
});

/**
 * Réception de la demande de sélection des enfants
 */
socket.on('select_etiquetage_children', (data) => {
    console.log('[select_etiquetage_children]', data);
    etiquetageCardId = data.card_id;
    showEtiquetageChildrenModal(
        data.current_children, 
        data.target_children,
        etiquetageTargetPlayerName || 'la cible'
    );
});
// ###############################
// Coup de Foudre
// ###############################

function showCoupDeFoudreModal(availableTargets) {
    console.log("[showCoupDeFoudreModal]", availableTargets);
    
    const modal = document.getElementById('coup-de-foudre-modal');
    const targetsList = document.getElementById('coup-de-foudre-targets-list');
    
    targetsList.innerHTML = availableTargets.map(target => {
        const isImmune = target.immune || false;
        const buttonClass = isImmune 
            ? 'w-full p-4 bg-gray-400 text-gray-700 rounded-lg cursor-not-allowed opacity-50' 
            : 'w-full p-4 bg-gradient-to-r from-pink-500 to-red-500 text-white rounded-lg hover:from-pink-600 hover:to-red-600 transition-all transform hover:scale-105 font-semibold shadow-lg';
        const onClick = isImmune ? '' : `onclick="selectCoupDeFoudreTarget(${target.id})"`;
        const immuneText = isImmune ? ' 🛡️ (Pas marié)' : '';
        
        return `
            <button ${onClick} ${isImmune ? 'disabled' : ''} 
                    class="${buttonClass}">
                💘 ${target.name}${immuneText}
            </button>
        `;
    }).join('');
    
    modal.classList.remove('hidden');
}

function selectCoupDeFoudreTarget(targetId) {
    console.log("[selectCoupDeFoudreTarget]", cardId, targetId);
    
    socket.emit('coup_de_foudre_selected', {
        card_id: cardId,
        target_player_id: targetId
    });
    
    closeCoupDeFoudreModal();
}

function discardCoupDeFoudre() {
    console.log("[discardCoupDeFoudre]");
    
    socket.emit('coup_de_foudre_discard', {
        card_id: cardId
    });
    
    closeCoupDeFoudreModal();
}

function closeCoupDeFoudreModal() {
    document.getElementById('coup-de-foudre-modal').classList.add('hidden');
}

socket.on('select_coup_de_foudre_target', (data) => {
    console.log('[select_coup_de_foudre_target]', data);
    cardId = data.card_id;
    showCoupDeFoudreModal(data.available_targets);
});

// #################################
// sabre
// #################################
let sabreTargetPlayer = null;
let sabreSelectedHardship = null;

function showSabreModal(targetPlayer, receivedHardships) {
    log("showSabreModal", targetPlayer);
    log("showSabreModal", receivedHardships);
    const modal = document.getElementById('sabre-modal');
    const targetName = document.getElementById('sabre-target-name');
    const hardshipsList = document.getElementById('sabre-hardships-list');
    
    sabreTargetPlayer = targetPlayer;
    targetName.textContent = targetPlayer.name;
    
    hardshipsList.innerHTML = receivedHardships.map(hardship => `
        <button onclick="selectSabreHardship('${hardship.id}')" 
                class="w-full p-3 bg-red-100 border-2 border-red-300 rounded-lg hover:bg-red-200 transition-all text-left">
            <span class="font-semibold">⚠️ ${hardship.subtype}</span>
            <div class="text-xs text-gray-600 mt-1">${getHardshipDescription(hardship.subtype)}</div>
        </button>
    `).join('');
    
    modal.classList.remove('hidden');
}

function selectSabreHardship(hardshipId) {
    sabreSelectedHardship = hardshipId;
    
    socket.emit('sabre_selected', {
        card_id: card_id,
        target_id: sabreTargetPlayer.id,
        hardship_id: hardshipId
    });
    
    closeSabreModal();
}

function discardSabre() {
    socket.emit('sabre_discard', {
        card_id: card_id,
    });
    
    closeSabreModal();
}

function closeSabreModal() {
    document.getElementById('sabre-modal').classList.add('hidden');
    sabreTargetPlayer = null;
    sabreSelectedHardship = null;
}


socket.on('select_sabre', (data) => {
    log('Sabre - sélection', data);
    card_id = data.card_id;
    showSabreModal(data.target_player, data.received_hardships);
});

// #################################
// GIRL POWER - Sélection carte spéciale
// #################################

/**
 * Affiche la modal de sélection de carte spéciale pour Girl Power
 */
function showGirlPowerModal(specialCards) {
    console.log("[showGirlPowerModal]", specialCards);
    
    const modal = document.getElementById('girl-power-modal');
    const cardsList = document.getElementById('girl-power-cards-list');
    
    if (!specialCards || specialCards.length === 0) {
        cardsList.innerHTML = `
            <div class="col-span-full text-center p-8 bg-purple-50 rounded-lg border-2 border-purple-200">
                <div class="text-4xl mb-3">💜</div>
                <p class="text-gray-600 font-semibold">Aucune carte spéciale utilisable</p>
                <p class="text-sm text-gray-500 mt-2">Vous devez avoir des filles posées pour utiliser Girl Power</p>
            </div>
        `;
    } else {
        cardsList.innerHTML = specialCards.map(card => `
            <div class="girl-power-card-wrapper" 
                 data-card-id="${card.id}"
                 onclick="selectGirlPowerCard('${card.id}')">
                ${createCardHTML(card, false, false, false, false)}
            </div>
        `).join('');
        
        // Ajouter les effets hover après insertion
        specialCards.forEach(card => {
            const wrapper = cardsList.querySelector(`[data-card-id="${card.id}"]`);
            if (wrapper) {
                wrapper.style.cursor = 'pointer';
                
                wrapper.onmouseenter = () => {
                    wrapper.style.transform = 'scale(1.05)';
                    wrapper.style.transition = 'transform 0.2s';
                };
                wrapper.onmouseleave = () => {
                    wrapper.style.transform = 'scale(1)';
                };
            }
        });
    }
    
    modal.classList.remove('hidden');
}

/**
 * Sélectionne une carte spéciale pour Girl Power
 */
function selectGirlPowerCard(selectedCardId) {
    console.log("[selectGirlPowerCard]", selectedCardId);
    
    socket.emit('girl_power_card_selected', {
        card_id: cardId,
        selected_card_id: selectedCardId
    });
    
    closeGirlPowerModal();
}

/**
 * Annule la sélection Girl Power
 */
function discardGirlPowerSelection() {
    console.log("[discardGirlPowerSelection]");
    
    socket.emit('girl_power_discard', {
        card_id: cardId
    });
    
    closeGirlPowerModal();
}

/**
 * Ferme la modal Girl Power
 */
function closeGirlPowerModal() {
    document.getElementById('girl-power-modal').classList.add('hidden');
}

/**
 * Réception de la demande de sélection de carte spéciale
 */
socket.on('select_girl_power_card', (data) => {
    console.log('[select_girl_power_card]', data);
    cardId = data.card_id;
    showGirlPowerModal(data.special_cards);
});
// #################################
// Redistribution des tâches
// #################################

let redistributionInitialData = null;
let redistributionCurrentState = {};

/**
 * Affiche la modal de redistribution des tâches
 */
function showRedistributionModal(initialData) {
    console.log("[showRedistributionModal]", initialData);
    
    redistributionInitialData = initialData;
    
    // Initialiser l'état courant avec les données initiales
    redistributionCurrentState = {};
    Object.keys(initialData).forEach(playerId => {
        redistributionCurrentState[playerId] = [...initialData[playerId][0]]; // Copie des job IDs
    });
    
    const modal = document.createElement('div');
    modal.id = 'redistribution-modal';
    modal.className = 'modal fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
    
    const html = `
        <div class="bg-white rounded-xl shadow-2xl p-8 max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <h2 class="text-3xl font-bold text-center mb-4 text-purple-800">
                🔄 Redistribution des Tâches
            </h2>
            <p class="text-center mb-6 text-gray-600">
                Réorganisez les métiers entre les joueurs (chaque joueur doit garder le même nombre de métiers)
            </p>
            
            <!-- Conteneur des joueurs -->
            <div id="redistribution-players-container" class="space-y-6 mb-6">
                <!-- Généré dynamiquement -->
            </div>
            
            <!-- Message de validation -->
            <div id="redistribution-validation-message" class="mb-4 text-center text-sm">
                <span class="text-gray-600">Réorganisez les métiers comme vous le souhaitez</span>
            </div>
            
            <!-- Boutons d'action -->
            <div class="flex gap-3">
                <button onclick="confirmRedistribution()" 
                        id="redistribution-confirm-btn"
                        class="flex-1 bg-green-500 text-white py-3 px-6 rounded-lg hover:bg-green-600 transition-all font-semibold shadow-lg">
                    ✅ Valider la redistribution
                </button>
                <button onclick="resetRedistribution()" 
                        class="flex-1 bg-blue-500 text-white py-3 px-6 rounded-lg hover:bg-blue-600 transition-all font-semibold shadow-lg">
                    🔄 Réinitialiser
                </button>
                <button onclick="discardRedistribution()" 
                        class="flex-1 bg-gray-500 text-white py-3 px-6 rounded-lg hover:bg-gray-600 transition-all font-semibold shadow-lg">
                    ❌ Annuler
                </button>
            </div>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
    
    renderRedistributionPlayers();
}

/**
 * Affiche les joueurs et leurs métiers
 */
function renderRedistributionPlayers() {
    const container = document.getElementById('redistribution-players-container');
    if (!container) return;
    
    let html = '';
    
    // Récupérer les infos des joueurs depuis currentGame
    Object.keys(redistributionCurrentState).forEach(playerId => {
        const player = currentGame.players[parseInt(playerId)];
        const jobIds = redistributionCurrentState[playerId];
        const initialJobCount = redistributionInitialData[playerId][1];
        
        html += `
            <div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border-2 border-purple-300 p-4">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-xl font-bold text-purple-800">
                        👤 ${player.name}
                    </h3>
                    <span class="text-sm font-semibold ${jobIds.length === initialJobCount ? 'text-green-600' : 'text-red-600'}">
                        ${jobIds.length}/${initialJobCount} métier(s)
                    </span>
                </div>
                
                <div id="player-${playerId}-jobs" 
                     class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 min-h-[100px] p-3 bg-white rounded-lg border-2 border-dashed ${jobIds.length === initialJobCount ? 'border-green-300' : 'border-red-300'}"
                     ondrop="handleJobDrop(event, ${playerId})" 
                     ondragover="handleJobDragOver(event)">
                    <!-- Métiers générés dynamiquement -->
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Rendre les métiers pour chaque joueur
    Object.keys(redistributionCurrentState).forEach(playerId => {
        renderPlayerJobs(playerId);
    });
    
    updateRedistributionValidation();
}

/**
 * Affiche les métiers d'un joueur spécifique
 */
function renderPlayerJobs(playerId) {
    const container = document.getElementById(`player-${playerId}-jobs`);
    if (!container) return;
    
    const jobIds = redistributionCurrentState[playerId];
    
    if (jobIds.length === 0) {
        container.innerHTML = '<div class="col-span-full text-center text-gray-400 italic py-4">Zone vide - Glissez un métier ici</div>';
        return;
    }
    
    let html = '';
    
    jobIds.forEach(jobId => {
        // Trouver le métier dans tous les joueurs
        let jobCard = null;
        let originalPlayerId = null;
        
        Object.keys(redistributionInitialData).forEach(pId => {
            const player = currentGame.players[parseInt(pId)];
            const job = player.played["vie professionnelle"].find(c => c.id === jobId && c.type === 'job');
            if (job) {
                jobCard = job;
                originalPlayerId = pId;
            }
        });
        
        if (!jobCard) return;
        
        html += `
            <div draggable="true" 
                 ondragstart="handleJobDragStart(event, '${jobId}', ${playerId})"
                 class="bg-blue-100 border-2 border-blue-400 rounded-lg p-3 cursor-move hover:shadow-lg hover:scale-105 transition-all">
                <div class="flex items-center gap-2 mb-2">
                    <span class="text-2xl">💼</span>
                    <span class="font-bold text-sm">${jobCard.subtype}</span>
                </div>
                <div class="grid grid-cols-2 gap-1 text-xs text-gray-700">
                    <div class="flex items-center gap-1">
                        <span>💰</span>
                        <span>${jobCard.salary}</span>
                    </div>
                    <div class="flex items-center gap-1">
                        <span>📚</span>
                        <span>${jobCard.studies}</span>
                    </div>
                    ${jobCard.smiles > 0 ? `
                        <div class="flex items-center gap-1 col-span-2">
                            <span>😊</span>
                            <span>${jobCard.smiles}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Gestion du drag & drop
 */
let draggedJobId = null;
let draggedFromPlayerId = null;

function handleJobDragStart(event, jobId, fromPlayerId) {
    draggedJobId = jobId;
    draggedFromPlayerId = fromPlayerId;
    event.dataTransfer.effectAllowed = 'move';
    event.target.style.opacity = '0.5';
}

function handleJobDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
}

function handleJobDrop(event, toPlayerId) {
    event.preventDefault();
    
    if (!draggedJobId || draggedFromPlayerId === null) return;
    
    // Retirer le métier du joueur d'origine
    const fromIndex = redistributionCurrentState[draggedFromPlayerId].indexOf(draggedJobId);
    if (fromIndex > -1) {
        redistributionCurrentState[draggedFromPlayerId].splice(fromIndex, 1);
    }
    
    // Ajouter le métier au nouveau joueur
    redistributionCurrentState[toPlayerId].push(draggedJobId);
    
    // Rafraîchir l'affichage
    renderRedistributionPlayers();
    
    // Réinitialiser
    draggedJobId = null;
    draggedFromPlayerId = null;
}

// Réinitialiser l'opacité après le drag
document.addEventListener('dragend', (event) => {
    event.target.style.opacity = '1';
});

/**
 * Valide que chaque joueur a le bon nombre de métiers
 */
function updateRedistributionValidation() {
    const messageEl = document.getElementById('redistribution-validation-message');
    const confirmBtn = document.getElementById('redistribution-confirm-btn');
    
    let isValid = true;
    let errorMessages = [];
    
    Object.keys(redistributionInitialData).forEach(playerId => {
        const initialCount = redistributionInitialData[playerId][1];
        const currentCount = redistributionCurrentState[playerId].length;
        
        if (currentCount !== initialCount) {
            isValid = false;
            const player = currentGame.players[parseInt(playerId)];
            errorMessages.push(`${player.name}: ${currentCount}/${initialCount} métiers`);
        }
    });
    
    if (isValid) {
        messageEl.innerHTML = '<span class="text-green-600 font-semibold">✅ Redistribution valide !</span>';
        confirmBtn.disabled = false;
    } else {
        messageEl.innerHTML = `<span class="text-red-600 font-semibold">⚠️ ${errorMessages.join(' • ')}</span>`;
        confirmBtn.disabled = true;
    }
}

/**
 * Confirme la redistribution
 */
function confirmRedistribution() {
    console.log("[confirmRedistribution]", redistributionCurrentState);
    
    socket.emit('redistribution_finish', {
        card_id: cardId,
        distribution: redistributionCurrentState
    });
    
    closeRedistributionModal();
}

/**
 * Réinitialise à l'état initial
 */
function resetRedistribution() {
    Object.keys(redistributionInitialData).forEach(playerId => {
        redistributionCurrentState[playerId] = [...redistributionInitialData[playerId][0]];
    });
    
    renderRedistributionPlayers();
}

/**
 * Annule la redistribution
 */
function discardRedistribution() {
    console.log("[discardRedistribution]");
    
    // Pas d'événement serveur nécessaire, juste fermer la modal
    closeRedistributionModal();
}

/**
 * Ferme la modal
 */
function closeRedistributionModal() {
    const modal = document.getElementById('redistribution-modal');
    if (modal) {
        modal.remove();
    }
    redistributionInitialData = null;
    redistributionCurrentState = {};
    cardId = null;
}

/**
 * Réception de la demande de redistribution
 */
socket.on('redistribution_des_taches', (data) => {
    console.log('[redistribution_des_taches]', data);
    cardId = data.card_id;
    showRedistributionModal(data.data_initial);
});