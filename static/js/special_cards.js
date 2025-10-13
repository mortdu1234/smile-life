

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

// ÉTOILE FILANTE
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
    socket.emit('discard_card_selected', { card_id: cardId });
    closeStarModal();
}

function closeStarModal() {
    document.getElementById('star-modal').classList.add('hidden');
}

// CHANCE
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

function selectChanceCard(cardId) {
    socket.emit('chance_card_selected', { card_id: cardId });
    document.getElementById('chance-modal').classList.add('hidden');
}

// VENGEANCE
function showVengeanceModal(receivedHardships, availableTargets) {
    const modal = document.getElementById('vengeance-modal');
    const hardshipsList = document.getElementById('vengeance-hardships-list');
    
    selectedVengeanceHardship = null;
    availableVengeanceTargets = availableTargets;
    
    hardshipsList.innerHTML = receivedHardships.map(hardship => `
        <button onclick="selectVengeanceHardship('${hardship}')" 
                class="w-full p-3 bg-red-100 border-2 border-red-300 rounded-lg hover:bg-red-200 transition-all text-left">
            <span class="font-semibold">⚠️ ${hardship}</span>
            <div class="text-xs text-gray-600 mt-1">${getHardshipDescription(hardship)}</div>
        </button>
    `).join('');
    
    document.getElementById('vengeance-targets-container').classList.add('hidden');
    modal.classList.remove('hidden');
}

function selectVengeanceHardship(hardshipType) {
    selectedVengeanceHardship = hardshipType;
    
    // Afficher la liste des cibles
    const targetsContainer = document.getElementById('vengeance-targets-container');
    const targetsList = document.getElementById('vengeance-targets-list');
    
    targetsList.innerHTML = availableVengeanceTargets.map(target => `
        <button onclick="selectVengeanceTarget(${target.id})" 
                class="w-full p-4 bg-gradient-to-r from-red-500 to-orange-500 text-white rounded-lg hover:from-red-600 hover:to-orange-600 transition-all transform hover:scale-105 font-semibold shadow-lg">
            🎯 ${target.name}
        </button>
    `).join('');
    
    targetsContainer.classList.remove('hidden');
}

function selectVengeanceTarget(targetId) {
    if (!selectedVengeanceHardship) return;
    
    socket.emit('vengeance_selected', {
        hardship_type: selectedVengeanceHardship,
        target_id: targetId
    });
    
    closeVengeanceModal();
}

function closeVengeanceModal() {
    document.getElementById('vengeance-modal').classList.add('hidden');
    selectedVengeanceHardship = null;
    availableVengeanceTargets = [];
}

// ANNIVERSAIRE
function showBirthdayModal(birthdayPlayerName, availableSalaries) {
    const modal = document.getElementById('birthday-modal');
    const message = document.getElementById('birthday-message');
    const salariesList = document.getElementById('birthday-salaries-list');
    
    message.textContent = `C'est l'anniversaire de ${birthdayPlayerName} ! Offrez-lui un salaire 🎁`;
    
    salariesList.innerHTML = availableSalaries.map(salary => `
        <div onclick="selectBirthdayGift('${salary.id}')" 
                class="cursor-pointer p-4 bg-blue-100 border-2 border-blue-300 rounded-lg hover:bg-blue-200 hover:scale-105 transition-all text-center">
            <div class="text-3xl mb-2">💰</div>
            <div class="font-bold text-lg">${salary.subtype}</div>
        </div>
    `).join('');
    
    modal.classList.remove('hidden');
}

function selectBirthdayGift(salaryId) {
    socket.emit('birthday_gift_selected', { salary_id: salaryId });
    document.getElementById('birthday-modal').classList.add('hidden');
}

// TROC
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

function selectTrocTarget(targetId) {
    socket.emit('troc_target_selected', { target_id: targetId });
    closeTrocModal();
}

function closeTrocModal() {
    document.getElementById('troc-modal').classList.add('hidden');
}

// PISTON
function showPistonModal(availableJobs) {
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
    socket.emit('piston_job_selected', { job_id: jobId });
    closePistonModal();
}

function closePistonModal() {
    document.getElementById('piston-modal').classList.add('hidden');
}

// === CASINO ===
function openCasinoBetModal(isOpener = false) {
    const myPlayer = currentGame.players[myPlayerId];
    const availableSalaries = myPlayer.hand.filter(c => c.type === 'salary');
    
    if (availableSalaries.length === 0) {
        if (isOpener) {
            // L'ouvreur peut refuser s'il n'a pas de salaires
            skipCasinoBet();
        } else {
            alert('Vous n\'avez pas de salaires disponibles pour parier');
        }
        return;
    }
    
    const salariesHTML = availableSalaries.map(salary => `
        <button onclick="placeCasinoBet('${salary.id}')" 
                class="w-full p-4 bg-yellow-400 hover:bg-yellow-500 text-black font-bold rounded-lg transform hover:scale-105 transition-all shadow-lg mb-2">
            🎰 Salaire ${salary.subtype}
        </button>
    `).join('');
    
    let refuseButtonHTML = '';
    if (isOpener) {
        refuseButtonHTML = `
            <button onclick="skipCasinoBet()" 
                    class="w-full bg-orange-500 hover:bg-orange-600 text-white py-3 px-6 rounded-lg transition-all font-semibold">
                ⛔ Refuser de miser (le casino reste ouvert)
            </button>
        `;
    }
    
    const modalHTML = `
        <div id="casino-bet-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onclick="if(event.target.id==='casino-bet-modal') closeCasinoBetModal()">
            <div class="bg-gradient-to-b from-yellow-50 to-yellow-100 rounded-xl shadow-2xl p-8 max-w-md w-full border-4 border-yellow-400">
                <h2 class="text-3xl font-bold text-center mb-6 text-yellow-800">
                    🎰 Choisir un salaire
                </h2>
                ${isOpener ? '<p class="text-center mb-4 text-sm text-gray-700 italic">Vous pouvez refuser de miser, le casino restera ouvert</p>' : ''}
                <div class="space-y-2">
                    ${salariesHTML}
                </div>
                ${refuseButtonHTML}
                <button onclick="closeCasinoBetModal()" 
                        class="mt-4 w-full bg-gray-500 text-white py-3 px-6 rounded-lg hover:bg-gray-600 transition-all font-semibold">
                    Annuler
                </button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function closeCasinoBetModal() {
    const modal = document.getElementById('casino-bet-modal');
    if (modal) modal.remove();
}

function skipCasinoBet() {
    log('Refuser de miser au casino');
    socket.emit('skip_casino_bet', {});
    closeCasinoBetModal();
}

function placeCasinoBet(salaryId) {
    log('Placer pari casino', {salaryId});
    socket.emit('place_casino_bet', { 
        salary_id: salaryId,
        is_opener: false
    });
    closeCasinoBetModal();
}


function updateCasinoDisplay(casinoState) {
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
            <div class="font-bold text-xl">${casinoState.first_bet.player_name}</div>
            <div class="text-xs mt-1 text-yellow-300">Montant secret</div>
        `;
    } else {
        firstBetEl.innerHTML = '<p class="text-sm italic">En attente...</p>';
    }
    
    // Afficher le deuxième pari (SANS le montant)
    if (casinoState.second_bet) {
        secondBetEl.innerHTML = `
            <div class="text-2xl mb-2">🎰</div>
            <div class="font-bold text-xl">${casinoState.second_bet.player_name}</div>
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
socket.on('select_birthday_gift', (data) => {
    log('Anniversaire - sélection cadeau', data);
    showBirthdayModal(data.birthday_player_name, data.available_salaries);
});

socket.on('select_troc_target', (data) => {
    log('Troc - sélection cible', data);
    showTrocModal(data.available_targets);
});

socket.on('select_piston_job', (data) => {
    log('Piston - sélection métier', data);
    showPistonModal(data.available_jobs);
});

socket.on('select_vengeance', (data) => {
    log('Vengeance - sélection', data);
    showVengeanceModal(data.received_hardships, data.available_targets);
});

socket.on('select_chance_card', (data) => {
    log('Chance - sélection carte', data);
    showChanceModal(data.cards);
});

socket.on('arc_en_ciel_mode', (data) => {
    log('Arc-en-ciel - mode activé', data);
    showArcEnCielMode();
});

socket.on('select_casino_bet', (data) => {
    log('Casino - sélection mise par l\'ouvreur', data);
    
    const myPlayer = currentGame.players[myPlayerId];
    const availableSalaries = myPlayer.hand.filter(c => c.type === 'salary');
    
    if (availableSalaries.length === 0) {
        // Pas de salaires, passer directement au joueur suivant
        socket.emit('skip_casino_bet', {});
        return;
    }
    
    const salariesHTML = availableSalaries.map(salary => `
        <button onclick="placeOpenerCasinoBet('${salary.id}');pickCard('deck')" 
                class="w-full p-4 bg-yellow-400 hover:bg-yellow-500 text-black font-bold rounded-lg transform hover:scale-105 transition-all shadow-lg mb-2">
            🎰 Salaire ${salary.subtype}
        </button>
    `).join('');
    
    const modalHTML = `
        <div id="casino-opener-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onclick="if(event.target.id==='casino-opener-modal') closeCasinoOpenerModal()">
            <div class="bg-gradient-to-b from-yellow-50 to-yellow-100 rounded-xl shadow-2xl p-8 max-w-md w-full border-4 border-yellow-400">
                <h2 class="text-3xl font-bold text-center mb-6 text-yellow-800">
                    🎰 Vous ouvrez le casino !
                </h2>
                <p class="text-center mb-6 text-gray-700">
                    Voulez-vous miser maintenant ? (Optionnel - le casino restera ouvert même si vous refusez)
                </p>
                <div class="space-y-2 mb-4">
                    ${salariesHTML}
                </div>
                <button onclick="skipOpenerCasinoBet()" 
                        class="w-full bg-orange-500 hover:bg-orange-600 text-white py-3 px-6 rounded-lg transition-all font-semibold mb-2">
                    ⛔ Refuser de miser maintenant
                </button>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
});

function placeOpenerCasinoBet(salaryId) {
    log('Ouvreur place un pari', {salaryId});
    socket.emit('place_casino_bet', { 
        salary_id: salaryId,
        is_opener: true
    });
    closeCasinoOpenerModal();
}

function skipOpenerCasinoBet() {
    log('Ouvreur refuse de miser');
    socket.emit('skip_casino_bet', {});
    closeCasinoOpenerModal();
}

function closeCasinoOpenerModal() {
    const modal = document.getElementById('casino-opener-modal');
    if (modal) modal.remove();
}

