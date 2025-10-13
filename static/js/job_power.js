// === CHEF DES VENTES ===
function showChefVentesModal(salaries) {
    const modal = document.createElement('div');
    modal.id = 'chef-achats-modal';
    modal.className = 'modal fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
    
    const html = `
        <div class="bg-white rounded-xl shadow-2xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h2 class="text-2xl font-bold text-center mb-4 text-gray-800">
                🛍️ Chef des Ventes
            </h2>
            <p class="text-center mb-6 text-gray-600">Choisissez une acquisition de la défausse à acheter (ou ne rien prendre)</p>
            <div id="chef-achats-acquisitions" class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6"></div>
            <div class="flex gap-3">
                <button onclick="cancelChefVenteModal()" class="flex-1 bg-gray-500 text-white py-3 px-6 rounded-lg hover:bg-gray-600 font-semibold">
                    ❌ Annuler
                </button>
            </div>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
    
    const container = document.getElementById('chef-achats-acquisitions');
    container.innerHTML = salaries.map(sal => `
        <div onclick="selectChefVenteSalary('${sal.id}')" 
             class="cursor-pointer p-4 bg-green-100 border-2 border-green-300 rounded-lg hover:bg-green-200 hover:scale-105 transition-all text-center">
            <div class="text-3xl mb-2">💰</div>
            <div class="font-bold text-lg">salaire ${sal.subtype}</div>
        </div>
    `).join('');
}

function selectChefVenteSalary(salary_id) {
    socket.emit('chef_ventes_salary_selected', { salary_id: salary_id });
    closeChefAchatsModal();
}

function cancelChefVenteModal() {
    socket.emit('cancel_chef_ventes_salary_selection');
    closeChefAchatsModal();
}

// === CHEF DES ACHATS ===
function showChefAchatsModal(acquisitions) {
    const modal = document.createElement('div');
    modal.id = 'chef-achats-modal';
    modal.className = 'modal fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
    
    const html = `
        <div class="bg-white rounded-xl shadow-2xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h2 class="text-2xl font-bold text-center mb-4 text-gray-800">
                🛍️ Chef des Achats
            </h2>
            <p class="text-center mb-6 text-gray-600">Choisissez une acquisition de la défausse à acheter (ou ne rien prendre)</p>
            <div id="chef-achats-acquisitions" class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6"></div>
            <div class="flex gap-3">
                <button onclick="confirmChefAchatsWithoutPurchase()" class="flex-1 bg-blue-500 text-white py-3 px-6 rounded-lg hover:bg-blue-600 font-semibold">
                    ✅ Ne rien prendre
                </button>
                <button onclick="cancelChefAchatsModal()" class="flex-1 bg-gray-500 text-white py-3 px-6 rounded-lg hover:bg-gray-600 font-semibold">
                    ❌ Annuler
                </button>
            </div>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
    
    const container = document.getElementById('chef-achats-acquisitions');
    container.innerHTML = acquisitions.map(acq => `
        <div onclick="selectChefAchatsAcquisition('${acq.id}')" 
             class="cursor-pointer p-4 bg-green-100 border-2 border-green-300 rounded-lg hover:bg-green-200 hover:scale-105 transition-all text-center">
            <div class="text-3xl mb-2">${acq.type === 'house' ? '🏠' : '✈️'}</div>
            <div class="font-bold text-lg">${acq.subtype}</div>
            ${acq.cost ? `<div class="text-sm text-gray-600">Coût: ${acq.cost}</div>` : ''}
        </div>
    `).join('');
}

socket.on('select_salaries_for_acquisition_chef_achat', (data) => {
    log('Sélectionner salaires pour acquisition', data);
    showSalarySelectionModal(data.card, data.required_cost, data.available_salaries, data.heritage_available || 0);
});

function cancelChefAchatsModal() {
    socket.emit('cancel_chef_achats_job', {});
    closeChefAchatsModal();
}

function confirmChefAchatsWithoutPurchase() {
    socket.emit('confirm_chef_achats_without_purchase');
    closeChefAchatsModal();
}

function selectChefAchatsAcquisition(acquisitionId) {
    socket.emit('chef_achats_acquisition_selected', { acquisition_id: acquisitionId });
    closeChefAchatsModal();
}

function closeChefAchatsModal() {
    const modal = document.getElementById('chef-achats-modal');
    if (modal) modal.remove();
}

// === CHERCHEUR ===
function showChercheursModal(message) {
    const modal = document.createElement('div');
    modal.id = 'chercheur-modal';
    modal.className = 'modal fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
    
    const html = `
        <div class="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full">
            <h2 class="text-2xl font-bold text-center mb-4 text-gray-800">
                🔬 Chercheur
            </h2>
            <div class="bg-green-50 border-2 border-green-300 rounded-lg p-6 mb-6 text-center">
                <p class="text-lg text-gray-700">${message}</p>
            </div>
            <button onclick="confirmChercheur()" class="w-full bg-green-500 text-white py-3 px-6 rounded-lg hover:bg-green-600 font-semibold">
                ✅ Continuer
            </button>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
}

function confirmChercheur() {
    socket.emit('chercheur_confirm', {});
    const modal = document.getElementById('chercheur-modal');
    if (modal) modal.remove();
}

// === JOURNALISTE ===
function showJournalisteModal(handsInfo) {
    const modal = document.createElement('div');
    modal.id = 'journaliste-modal';
    modal.className = 'modal fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
    
    let handsHTML = '';
    for (const [playerName, cards] of Object.entries(handsInfo)) {
        handsHTML += `
            <div class="mb-6 p-4 bg-blue-50 rounded-lg border-2 border-blue-300">
                <h3 class="font-bold mb-3 text-lg text-blue-800">${playerName}</h3>
                <div class="grid grid-cols-3 gap-2">
                    ${cards.map(card => `
                        <div class="p-2 bg-white rounded border border-blue-200 text-center text-xs">
                            <div>${card.type === 'special' ? '⭐' : card.type === 'job' ? '💼' : '📋'}</div>
                            <div class="font-semibold">${getCardLabel(card)}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    const html = `
        <div class="bg-white rounded-xl shadow-2xl p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <h2 class="text-2xl font-bold text-center mb-6 text-gray-800">
                📰 Journaliste - Mains de tous les joueurs
            </h2>
            <div id="journaliste-hands">${handsHTML}</div>
            <button onclick="confirmJournaliste()" class="w-full bg-green-500 text-white py-3 px-6 rounded-lg hover:bg-green-600 font-semibold">
                ✅ Continuer
            </button>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
}

function confirmJournaliste() {
    socket.emit('journaliste_confirm', {});
    const modal = document.getElementById('journaliste-modal');
    if (modal) modal.remove();
}

// === MÉDIUM ===
function showMediumModal(cards, total) {
    const modal = document.createElement('div');
    modal.id = 'medium-modal';
    modal.className = 'modal fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
    
    const cardsHTML = cards.map((card, index) => `
        <div class="p-3 bg-purple-100 border-2 border-purple-300 rounded text-center">
            <div class="text-sm font-bold mb-1">Position ${index + 1}</div>
            <div class="text-2xl mb-1">${card.type === 'hardship' ? '⚠️' : card.type === 'special' ? '⭐' : '📋'}</div>
            <div class="text-xs font-semibold">${getCardLabel(card)}</div>
        </div>
    `).join('');
    
    const html = `
        <div class="bg-white rounded-xl shadow-2xl p-8 max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <h2 class="text-2xl font-bold text-center mb-2 text-gray-800">
                🔮 Médium - Les 13 prochaines cartes
            </h2>
            <p class="text-center text-gray-600 mb-6">Total de cartes en pioche: ${total}</p>
            <div class="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-13 gap-2 mb-6">
                ${cardsHTML}
            </div>
            <button onclick="confirmMedium()" class="w-full bg-purple-500 text-white py-3 px-6 rounded-lg hover:bg-purple-600 font-semibold">
                ✅ Continuer
            </button>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
}

function confirmMedium() {
    socket.emit('medium_confirm', {});
    const modal = document.getElementById('medium-modal');
    if (modal) modal.remove();
}

// === ÉCOUTEURS SOCKET ===
socket.on('select_chef_ventes_salary', (data) => {
    log('Chef des ventes - sélection salaire', data);
    showChefVentesModal(data.salaries);
});

socket.on('select_chef_achats_acquisition', (data) => {
    log('Chef des achats - sélection acquisition', data);
    showChefAchatsModal(data.acquisitions);
});

// Chercheur - choix d'une carte dans la défausse
socket.on('chercheur_activated', (data) => {
    log('Chercheur activé', data);
    showChercheursModal(data.message);
});

// Journaliste - affichage des mains de tous les joueurs
socket.on('show_all_hands', (data) => {
    log('Journaliste - affichage des mains', data);
    showJournalisteModal(data.hands);
});

// Médium - affichage des 13 prochaines cartes
socket.on('show_next_cards', (data) => {
    log('Médium - affichage des 13 prochaines cartes', data);
    showMediumModal(data.cards, data.total);
});

// === ASTRONAUTE ===
function showAstronauteModal(cards) {
    const modal = document.createElement('div');
    modal.id = 'astronaute-modal';
    modal.className = 'modal fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4';
    
    const html = `
        <div class="bg-white rounded-xl shadow-2xl p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <h2 class="text-2xl font-bold text-center mb-4 text-gray-800">
                🚀 Astronaute
            </h2>
            <p class="text-center mb-6 text-gray-600">Choisissez une carte de la défausse à jouer (sauf coups durs)</p>
            <div id="astronaute-cards" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3 mb-6"></div>
            <button onclick="closeAstronauteModal()" class="w-full bg-gray-500 text-white py-3 px-6 rounded-lg hover:bg-gray-600">
                Annuler
            </button>
        </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
    
    const container = document.getElementById('astronaute-cards');
    container.innerHTML = cards.map(card => `
        <div onclick="selectAstronauteCard('${card.id}')" 
             class="cursor-pointer transform hover:scale-105 transition-all">
            ${createCardHTML(card, false)}
        </div>
    `).join('');
}

function selectAstronauteCard(cardId) {
    socket.emit('astronaute_card_selected', { card_id: cardId });
    closeAstronauteModal();
}

function closeAstronauteModal() {
    const modal = document.getElementById('astronaute-modal');
    if (modal) modal.remove();
}

socket.on('select_astronaute_card', (data) => {
    log('Astronaute - sélection carte', data);
    showAstronauteModal(data.cards);
});