

// === CARTES SPÉCIALES ===

function closeSalaryModal() {
    // ✅ Si c'est un achat chef des achats annulé, on ne fait RIEN côté serveur
    // (le joueur reviendra à la modal chef des achats)
    // On nettoie juste les variables locales
    
    document.getElementById('salary-selection-modal').classList.add('hidden');
    pendingAcquisitionCard = null;
    selectedSalaries = [];
    requiredCost = 0;
    heritageAvailable = 0;
    heritageUsed = 0;
    
    // ✅ Si c'était un achat chef des achats, réafficher la modal chef des achats
    if (currentGame.pending_special && currentGame.pending_special.type === 'chef_achats_purchase') {
        // La modal chef des achats est toujours là en arrière-plan
        // On ne fait rien de spécial, le joueur peut recliquer sur une autre acquisition
    }
}


// ARC-EN-CIEL
function showArcEnCielMode() {
    print("YOUSKKK tu dois pas voir ca")
}

function updateArcRemaining(count) {
    log('Mise à jour du compteur Arc-en-ciel', count);
    document.getElementById('arc-remaining').textContent = count;
}

function finishArcEnCiel() {
    socket.emit('arc_en_ciel_finished', {});
    document.getElementById('arc-en-ciel-banner').classList.add('hidden');
}
// ##########################
// ÉTOILE FILANTE
// ##########################
function showStarModal(discardCards) {
    const modal = document.getElementById('star-modal');
    const discardList = document.getElementById('star-discard-list');
    
    if (!discardCards || discardCards.length === 0) {
        discardList.innerHTML = '<p class="col-span-full text-center text-gray-500">La défausse est vide</p>';
    } else {
        discardList.innerHTML = discardCards.map(card => `
            <div onclick="selectStarCard('${card.id}')" 
                    class="cursor-pointer transform hover:scale-105 transition-all">
                ${createCardHTML(card, false)}
            </div>
        `).join('');
    }
    
    modal.classList.remove('hidden');
}

function selectStarCard(cardId) {
    socket.emit('star_card_selected', { card_id: card_id,  selected_card_id: cardId});
    closeStarModal();
}

function discardStarCard() {
    socket.emit('discard_star_card_selected', { card_id: card_id });
    closeStarModal();    
}

function closeStarModal() {
    document.getElementById('star-modal').classList.add('hidden');
}

socket.on('select_star_card', (data) => {
    log('Vengeance - sélection', data);
    card_id = data.card_id;
    showStarModal(data.discard_cards);
});

// ##########################
// Chance
// ##########################
function showChanceModal(cards) {
    const modal = document.getElementById('chance-modal');
    const cardsList = document.getElementById('chance-cards-list');
    
    cardsList.innerHTML = cards.map(card => `
        <div onclick="selectChanceCard('${card.id}')" 
                class="cursor-pointer transform hover:scale-105 transition-all">
            ${createCardHTML(card, false)}
        </div>
    `).join('');
    
    modal.classList.remove('hidden');
}


socket.on('select_chance_card', (data) => {
    log('Chance - sélection carte', data);
    card_id = data.card_id;
    showChanceModal(data.cards);
});

function closeChanceModal() {
    document.getElementById('chance-modal').classList.add('hidden');
}

function selectChanceCard(cardId) {
    log('selectChanceCard', cardId);
    socket.emit('chance_card_selected', { 
        card_id: card_id,
        selected_card_id: cardId });
    closeChanceModal();
}

function discardChanceCard() {

    socket.emit('discard_chance_card_selected', { 
        card_id: card_id });
    closeChanceModal();

}
// ##########################
// VENGEANCE
// ##########################
let availableTargets = null;
function showVengeanceModal(receivedHardships) {
    log("showVengeanceModal", availableTargets)
    const modal = document.getElementById('vengeance-modal');
    const hardshipsList = document.getElementById('vengeance-hardships-list');
    
    hardshipsList.innerHTML = receivedHardships.map(hardship => `
        <button onclick="selectVengeanceHardship('${hardship.id}')" 
                class="w-full p-3 bg-red-100 border-2 border-red-300 rounded-lg hover:bg-red-200 transition-all text-left">
            <span class="font-semibold">⚠️ ${hardship.subtype}</span>
            <div class="text-xs text-gray-600 mt-1">${getHardshipDescription(hardship.id)}</div>
        </button>
    `).join('');
    
    document.getElementById('vengeance-targets-container').classList.add('hidden');
    modal.classList.remove('hidden');
}

function selectVengeanceHardship(hardshipId) {
    log("selectVengeanceHardship", availableTargets)
    // Afficher la liste des cibles
    const targetsContainer = document.getElementById('vengeance-targets-container');
    const targetsList = document.getElementById('vengeance-targets-list');
    
    targetsList.innerHTML = availableTargets.map(target => `
        <button onclick="selectVengeanceTarget('${target.id}', '${hardshipId}')" 
                class="w-full p-4 bg-gradient-to-r from-red-500 to-orange-500 text-white rounded-lg hover:from-red-600 hover:to-orange-600 transition-all transform hover:scale-105 font-semibold shadow-lg">
            🎯 ${target.name}
        </button>
    `).join('');
    
    targetsContainer.classList.remove('hidden');
}

function selectVengeanceTarget(targetId, hardshipId) {    
    socket.emit('vengeance_selected', {
        card_id: card_id,
        hardship_id: hardshipId,
        target_id: targetId
    });
    
    closeVengeanceModal();
}

function discardVengeance() {
    socket.emit('vengeance_discard', {
        card_id: card_id,
    });
    
    closeVengeanceModal();
}

function closeVengeanceModal() {
    document.getElementById('vengeance-modal').classList.add('hidden');
    selectedVengeanceHardship = null;
    availableVengeanceTargets = [];
}


socket.on('select_vengeance', (data) => {
    log('Vengeance - sélection', data);
    availableTargets = data.available_targets;;
    card_id = data.card_id;
    showVengeanceModal(data.received_hardships);
});

// ##########################################
// ANNIVERSAIRE
// ##########################################
function showBirthdayModal(birthdayPlayerName, availableSalaries, playerId) {
    const modal = document.getElementById('birthday-modal');
    const message = document.getElementById('birthday-message');
    const salariesList = document.getElementById('birthday-salaries-list');
    
    message.textContent = `C'est l'anniversaire de ${birthdayPlayerName} ! Offrez-lui un salaire 🎁`;
    
    salariesList.innerHTML = availableSalaries.map(salary => `
        <div onclick="selectBirthdayGift('${salary.id}', '${playerId}')" 
                class="cursor-pointer p-4 bg-blue-100 border-2 border-blue-300 rounded-lg hover:bg-blue-200 hover:scale-105 transition-all text-center">
            <div class="text-3xl mb-2">💰</div>
            <div class="font-bold text-lg">${salary.subtype}</div>
        </div>
    `).join('');
    
    modal.classList.remove('hidden');
}

function selectBirthdayGift(salaryId, playerId) {
    socket.emit('birthday_gift_selected', { 
        card_id: card_id,
        salary_id: salaryId,
        player_id: playerId        
    });
    document.getElementById('birthday-modal').classList.add('hidden');
}

function showBirthdayWaiting(remaining) {
    const modal = document.getElementById('birthday-waiting-modal');
    document.getElementById('remaining-gifts').textContent = remaining;
    modal.classList.remove('hidden');
}

function updateBirthdayWaiting(remaining) {
    document.getElementById('remaining-gifts').textContent = remaining;
}

function closeBirthdayWaiting() {
    const modal = document.getElementById('birthday-waiting-modal');
    modal.classList.add('hidden');
}

socket.on('select_birthday_gift', (data) => {
    card_id = data.card_id;
    log('Anniversaire - sélection cadeau', data);
    showBirthdayModal(data.birthday_player_name, data.available_salaries, data.player_id);
});

socket.on('show_birthday_waiting', (data) => {
    log('Anniversaire - page d\'attente', data);
    // Compter le nombre de joueurs qui doivent donner
    const otherPlayers = currentGame.players.filter((p, i) => 
        i !== myPlayerId && p.connected
    );
    showBirthdayWaiting(otherPlayers.length);
});

socket.on('update_birthday_waiting', (data) => {
    log('Anniversaire - mise à jour attente', data);
    updateBirthdayWaiting(data.remaining);
});

socket.on('close_birthday_waiting', (data) => {
    log('Anniversaire - fermeture attente', data);
    closeBirthdayWaiting();
});

// ##################################
// TROC
// ##################################
function showTrocModal(availableTargets) {
    const modal = document.getElementById('troc-modal');
    const playersList = document.getElementById('troc-players-list');
    
    playersList.innerHTML = availableTargets.map(target => `
        <button onclick="selectTrocTarget(${target.id})" 
                class="w-full p-4 bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-lg hover:from-blue-600 hover:to-cyan-600 transition-all transform hover:scale-105 font-semibold shadow-lg">
            🎯 ${target.name} (${target.hand_count} carte(s) en main)
        </button>
    `).join('');
    
    modal.classList.remove('hidden');
}

function discardTrocSelection() {
    socket.emit('discard_troc_target_selection', {
        card_id: card_id});
    closeTrocModal();
}

function selectTrocTarget(targetId) {
    log("troc_target_selected")
    socket.emit('troc_target_selected', {
        card_id: card_id,  
        target_id: targetId });
    closeTrocModal();
}

function closeTrocModal() {
    document.getElementById('troc-modal').classList.add('hidden');
}

socket.on('select_troc_target', (data) => {
    log('Troc - sélection cible', data);
    card_id = data.card_id;
    showTrocModal(data.available_targets);
});

// ###########################################
// PISTON
// ###########################################
let piston_card_id;

function showPistonModal(card_id, availableJobs) {
    piston_card_id = card_id;
    const modal = document.getElementById('piston-modal');
    const jobsList = document.getElementById('piston-jobs-list');
    
    jobsList.innerHTML = availableJobs.map(job => `
        <div onclick="selectPistonJob('${job.id}')" 
                class="cursor-pointer p-4 bg-blue-100 border-2 border-blue-400 rounded-lg hover:bg-blue-200 hover:scale-105 transition-all">
            <div class="flex items-center gap-2 mb-2">
                <span class="text-2xl">💼</span>
                <span class="font-bold">${job.subtype}</span>
            </div>
            <div class="text-sm text-gray-600">
                <div>💰 Salaire: ${job.salary}</div>
                <div>📚 Études: ${job.studies}</div>
                ${job.smiles > 0 ? `<div>😊 ${job.smiles}</div>` : ''}
            </div>
        </div>
    `).join('');
    
    modal.classList.remove('hidden');
}

function selectPistonJob(jobId) {
    console.log("success");
    socket.emit('piston_job_selected', { 
        card_id: piston_card_id,
        job_id: jobId });
    closePistonModal();
}

function cancelPistonJobSelection() {
    socket.emit('piston_job_cancel', { 
        card_id: piston_card_id });
    closePistonModal();
}

function closePistonModal() {
    document.getElementById('piston-modal').classList.add('hidden');
}

socket.on('select_piston_job', (data) => {
    log('Piston - sélection métier', data);
    showPistonModal(data.card_id, data.available_jobs);
});

// ###########################################
// === CASINO ===
// ###########################################
function showCasinoBetModal(availableSalaries) {
    
    const salariesHTML = availableSalaries.map(salary => `
        <button onclick="confirmCasinoBet('${salary.id}')" 
                class="w-full p-4 bg-yellow-400 hover:bg-yellow-500 text-black font-bold rounded-lg transform hover:scale-105 transition-all shadow-lg mb-2">
            🎰 Salaire ${salary.subtype}
        </button>
    `).join('');
    
    const modalHTML = `
        <div id="casino-bet-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onclick="if(event.target.id==='casino-bet-modal') closeCasinoBetModal()">
            <div class="bg-gradient-to-b from-yellow-50 to-yellow-100 rounded-xl shadow-2xl p-8 max-w-md w-full border-4 border-yellow-400">
                <h2 class="text-3xl font-bold text-center mb-6 text-yellow-800">
                    🎰 Choisir un salaire
                </h2>
                <div class="space-y-2">
                    ${salariesHTML}
                </div>
                <button onclick="discardCasinoBet()" 
                        class="mt-4 w-full bg-gray-500 text-white py-3 px-6 rounded-lg hover:bg-gray-600 transition-all font-semibold">
                    Annuler
                </button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function openCasinoBetModal() {
    socket.emit('want_to_bet', {});
}

socket.on('select_casino_bet', (data) => {
    log('Casino - sélection Salaire', data);
    showCasinoBetModal(data.available_salaries);
});

function closeCasinoBetModal() {
    const modal = document.getElementById('casino-bet-modal');
    if (modal) modal.remove();
}

function discardCasinoBet() {
    log('discardCasinoBet');
    socket.emit('discard_casino_bet', {});
    closeCasinoBetModal();
}

function confirmCasinoBet(salaryId) {
    log('confirmCasinoBet', {salaryId});
    socket.emit('place_casino_bet', { 
        bet_card_id: salaryId
    });
    closeCasinoBetModal();
}


function updateCasinoDisplay(casinoState) {
    console.log('[CASINO DEBUG]', casinoState);
    const container = document.getElementById('casino-section');
    const firstBetEl = document.getElementById('casino-first-bet-display');
    const secondBetEl = document.getElementById('casino-second-bet-display');
    const betButtonContainer = document.getElementById('casino-bet-button-container');
    const statusEl = document.getElementById('casino-status-text');
    
    if (!casinoState.open) {
        container.classList.add('hidden');
        return;
    }
    
    container.classList.remove('hidden');
    
    // Afficher le premier pari (SANS le montant)
    if (casinoState.first_bet) {
        firstBetEl.innerHTML = `
            <div class="text-2xl mb-2">🎰</div>
            <div class="font-bold text-xl">${casinoState.first_bet.name}</div>
            <div class="text-xs mt-1 text-yellow-300">Montant secret</div>
        `;
    } else {
        firstBetEl.innerHTML = '<p class="text-sm italic">En attente...</p>';
    }
    
    // Afficher le deuxième pari (SANS le montant)
    if (casinoState.second_bet) {
        secondBetEl.innerHTML = `
            <div class="text-2xl mb-2">🎰</div>
            <div class="font-bold text-xl">${casinoState.second_bet.name}</div>
            <div class="text-xs mt-1 text-yellow-300">Montant secret</div>
        `;
    } else {
        secondBetEl.innerHTML = '<p class="text-sm italic">En attente...</p>';
    }
    
    // Mettre à jour le statut
    if (!casinoState.first_bet) {
        statusEl.textContent = "En attente du 1er pari...";
    } else if (!casinoState.second_bet) {
        statusEl.textContent = "En attente du 2e pari...";
    } else {
        statusEl.textContent = "RÉsolution en cours...";
    }
    
    // Afficher le bouton de pari si le joueur peut parier
    if (currentGame && currentGame.players[myPlayerId]) {
        const myPlayer = currentGame.players[myPlayerId];
        const availableSalaries = myPlayer.hand.filter(c => c.type === 'salary');
        
        // ✅ Le joueur peut parier s'il y a de la place, qu'il a des salaires, 
        // que c'est son tour ET que la phase est 'play'
        const isMyTurn = currentGame.current_player === myPlayerId;
        const canBet = availableSalaries.length > 0 && 
                    (!casinoState.first_bet || !casinoState.second_bet) &&
                    isMyTurn &&
                    currentGame.phase === 'play';  // ✅ Nouvelle condition
        
        if (canBet) {
            betButtonContainer.classList.remove('hidden');
        } else {
            betButtonContainer.classList.add('hidden');
        }
    }
}









// === ECOUTES ===





socket.on('arc_en_ciel_mode', (data) => {
    log('Arc-en-ciel - mode activé', data);
    showArcEnCielMode();
});


