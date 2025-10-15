function showCreateGame() {
    document.getElementById('menu-screen').classList.add('hidden');
    document.getElementById('create-screen').classList.remove('hidden');
}

function showJoinGame() {
    document.getElementById('menu-screen').classList.add('hidden');
    document.getElementById('join-screen').classList.remove('hidden');
}

function backToMenu() {
    document.getElementById('create-screen').classList.add('hidden');
    document.getElementById('join-screen').classList.add('hidden');
    document.getElementById('menu-screen').classList.remove('hidden');
}

function showLobby() {
    document.getElementById('create-screen').classList.add('hidden');
    document.getElementById('join-screen').classList.add('hidden');
    document.getElementById('lobby-screen').classList.remove('hidden');
}

function showGame() {
    document.getElementById('lobby-screen').classList.add('hidden');
    document.getElementById('game-screen').classList.remove('hidden');
}

function showSalarySelectionModal(card, cost, availableSalaries, heritage = 0) {
    pendingAcquisitionCard = card;
    requiredCost = cost;
    selectedSalaries = [];
    heritageAvailable = heritage;
    heritageUsed = 0;
    
    const modal = document.getElementById('salary-selection-modal');
    const cardDisplay = document.getElementById('acquisition-card-display');
    const salariesList = document.getElementById('available-salaries-list');
    
    cardDisplay.innerHTML = `
        <div class="flex items-center gap-3">
            <span class="text-3xl">${card.type === 'house' ? '🏠' : '✈️'}</span>
            <div>
                <div class="font-bold text-lg">${getCardLabel(card)}</div>
                <div class="text-sm text-gray-600">Coût minimum: ${cost} 💰</div>
            </div>
        </div>
    `;
    
    document.getElementById('required-cost').textContent = cost;
    document.getElementById('selected-amount').textContent = '0';
    document.getElementById('payment-status').textContent = 'Sélectionnez vos salaires (minimum requis, vous pouvez dépenser plus)';
    
    // ✅ CONSTRUIRE LE HTML D'ABORD
    let salariesHTML = availableSalaries.map(salary => `
        <div onclick="toggleSalarySelection('${salary.id}', ${salary.subtype})" 
                id="salary-${salary.id}"
                class="salary-card-selectable p-3 bg-blue-100 border-2 border-blue-300 rounded-lg text-center">
            <div class="text-2xl">💰</div>
            <div class="font-bold">${salary.subtype}</div>
        </div>
    `).join('');
    
    // Ajouter l'héritage si disponible
    if (heritage > 0) {
        salariesHTML += `
            <div onclick="toggleHeritageSelection()" 
                    id="heritage-selector"
                    class="salary-card-selectable p-3 bg-purple-100 border-2 border-purple-300 rounded-lg text-center col-span-2">
                <div class="text-2xl">🎁</div>
                <div class="font-bold">Héritage: ${heritage}</div>
                <div class="text-xs text-gray-600">Cliquez pour utiliser</div>
            </div>
        `;
    }
    
    salariesList.innerHTML = salariesHTML;
    
    // ✅ PUIS APPELER LA MISE À JOUR
    updateSalarySelectionDisplay();
    
    modal.classList.remove('hidden');
}

function toggleSalarySelection(salaryId, salaryLevel) {
    const salaryElement = document.getElementById(`salary-${salaryId}`);
    
    const index = selectedSalaries.findIndex(s => s.id === salaryId);
    
    if (index > -1) {
        // Désélectionner
        selectedSalaries.splice(index, 1);
        salaryElement.classList.remove('salary-card-selected');
    } else {
        // Sélectionner
        selectedSalaries.push({ id: salaryId, level: salaryLevel });
        salaryElement.classList.add('salary-card-selected');
    }
    
    updateSalarySelectionDisplay();
}

function toggleHeritageSelection() {
    const heritageEl = document.getElementById('heritage-selector');
    
    if (heritageUsed > 0) {
        // Désactiver l'héritage
        heritageUsed = 0;
        heritageEl.classList.remove('salary-card-selected');
    } else {
        // Activer l'héritage
        heritageUsed = heritageAvailable;
        heritageEl.classList.add('salary-card-selected');
    }
    
    updateSalarySelectionDisplay();
}

function updateSalarySelectionDisplay() {
    const totalSalaries = selectedSalaries.reduce((sum, s) => sum + s.level, 0);
    const total = totalSalaries + heritageUsed;
    
    document.getElementById('selected-amount').textContent = `${totalSalaries}${heritageUsed > 0 ? ` + ${heritageUsed} (héritage)` : ''} = ${total}`;
    
    const statusEl = document.getElementById('payment-status');
    const confirmBtn = document.getElementById('confirm-salary-btn');
    
    // ✅ CAS SPÉCIAL : coût de 0 (GRATUIT - architecte)
    if (requiredCost === 0) {
        statusEl.textContent = '✅ Gratuit !';
        statusEl.className = 'mt-2 text-sm text-green-600 font-semibold';
        confirmBtn.disabled = false;  // ✅ ACTIVÉ IMMÉDIATEMENT

        return;  // Sortir pour ne pas continuer les autres vérifications
    }
    
    // Vérifications normales pour les acquisitions payantes
    if (total < requiredCost) {
        statusEl.textContent = `Il manque ${requiredCost - total} (minimum requis)`;
        statusEl.className = 'mt-2 text-sm text-orange-600 font-semibold';
        confirmBtn.disabled = true;
    } else if (total === requiredCost) {
        statusEl.textContent = '✅ Montant exact !';
        statusEl.className = 'mt-2 text-sm text-green-600 font-semibold';
        confirmBtn.disabled = false;
    } else {
        statusEl.textContent = `✅ Montant valide ! (+${total - requiredCost} de surplus)`;
        statusEl.className = 'mt-2 text-sm text-green-600 font-semibold';
        confirmBtn.disabled = false;
    }
}

function confirmSalarySelection() {
    if (!pendingAcquisitionCard) return;
    
    // ✅ Permettre de confirmer si c'est gratuit ET montant valide
    const totalSalaries = selectedSalaries.reduce((sum, s) => sum + s.level, 0);
    const total = totalSalaries + heritageUsed;
    
    if (requiredCost === 0 || total >= requiredCost) {
        socket.emit('select_salaries_for_purchase', {
            card_id: pendingAcquisitionCard.id,
            salary_ids: selectedSalaries.map(s => s.id),
            use_heritage: heritageUsed
        });
        
        closeSalaryModal();
    } else {
        alert('Le montant sélectionné est inférieur au minimum requis');
    }
}

function closeSalaryModal() {
    document.getElementById('salary-selection-modal').classList.add('hidden');
    pendingAcquisitionCard = null;
    selectedSalaries = [];
    requiredCost = 0;
    heritageAvailable = 0;
    heritageUsed = 0;
    socket.emit('cancel_select_salaries_for_purchase', {});
}

function showHardshipModal(card, availableTargets, isFromDiscard = false) {
    pendingHardshipCard = card;
    fromDiscard = isFromDiscard;
    
    const modal = document.getElementById('hardship-modal');
    const cardDisplay = document.getElementById('hardship-card-display');
    const targetsList = document.getElementById('target-players-list');
    
    cardDisplay.innerHTML = `
        <div class="flex items-center gap-3">
            <span class="text-3xl">⚠️</span>
            <div>
                <div class="font-bold text-lg">${getCardLabel(card)}</div>
                <div class="text-sm text-gray-600">${getHardshipDescription(card.subtype)}</div>
            </div>
        </div>
    `;
    
    targetsList.innerHTML = availableTargets.map(target => {
        const isImmune = target.immune || false;
        const buttonClass = isImmune 
            ? 'w-full p-4 bg-gray-400 text-gray-700 rounded-lg cursor-not-allowed opacity-50' 
            : 'w-full p-4 bg-gradient-to-r from-red-500 to-orange-500 text-white rounded-lg hover:from-red-600 hover:to-orange-600 transition-all transform hover:scale-105 font-semibold shadow-lg';
        const onClick = isImmune ? '' : `onclick="selectHardshipTarget(${target.id})"`;
        const immuneText = isImmune ? ` 🛡️ (Protégé)` : '';
        
        return `
            <button ${onClick} ${isImmune ? 'disabled' : ''} 
                    class="${buttonClass}">
                🎯 ${target.name}${immuneText}
            </button>
        `;
    }).join('');
    
    modal.classList.remove('hidden');
}

function closeHardshipModal() {
    document.getElementById('hardship-modal').classList.add('hidden');
    pendingHardshipCard = null;
    fromDiscard = false;
}

function selectHardshipTarget(targetId) {
    if (!pendingHardshipCard) return;
    
    log('Sélection cible malus', {cardId: pendingHardshipCard.id, targetId});
    
    socket.emit('play_card', {
        card_id: pendingHardshipCard.id,
        target_player_id: targetId
    });
    
    closeHardshipModal();
}

function getHardshipDescription(type) {
    const descriptions = {
        'accident': 'Passer 1 tour',
        'burnout': 'Passer 1 tour',
        'divorce': 'Fait perdre le mariage',
        'impot': 'Fait perdre 1 salaire',
        'licenciement': 'Fait perdre le métier',
        'maladie': 'Passer 1 tour',
        'redoublement': 'Fait perdre une étude',
        'prison': 'Passer 3 tours',
        'attentat': 'VOUS perdez tous VOS enfants !'
    };
    return descriptions[type] || 'Coup dur';
}

function createGame() {
    const playerName = document.getElementById('host-name').value || 'Joueur 1';
    const numPlayers = parseInt(document.getElementById('num-players').value);
    
    log('Création de partie', {playerName, numPlayers});
    
    socket.emit('create_game', {
        player_name: playerName,
        num_players: numPlayers
    });
    
    isHost = true;
}

function joinGame() {
    const playerName = document.getElementById('join-name').value || 'Joueur';
    const gameCode = document.getElementById('game-code').value.trim().toLowerCase();
    
    if (!gameCode) {
        alert('Veuillez entrer un code de partie');
        return;
    }
    
    log('Rejoindre partie', {playerName, gameCode});
    
    socket.emit('join_game', {
        game_id: gameCode,
        player_name: playerName
    });
}

function startGame() {
    log('Démarrage partie', {gameId});
    socket.emit('start_game', { game_id: gameId });
}

function pickCard(source) {
    log('Donne une carte depuis', {source});
    socket.emit('pick_card', { source: source });
}

function drawCard(source) {
    log('Pioche carte', {source});
    socket.emit('draw_card', { source: source });
}

function skipTurn() {
    log('Passer le tour');
    socket.emit('skip_turn', {});
}

function playCard(cardId) {
    log('Jouer carte', {cardId});
    
    if (!currentGame || !currentGame.players[myPlayerId]) return;
    
    const myPlayer = currentGame.players[myPlayerId];
    const card = myPlayer.hand.find(c => c.id === cardId);
        
    // Appel normal (le compteur sera mis à jour via game_updated)
    socket.emit('play_card', { card_id: cardId });
}

function discardCard(cardId) {
    log('Défausser carte', {cardId});
    socket.emit('discard_card', { card_id: cardId });
}

function discardPlayedCard(cardId) {
    log('Défausser carte posée', {cardId});
    
    if (confirm('Êtes-vous sûr de vouloir défausser cette carte ?')) {
        socket.emit('discard_played_card', { card_id: cardId });
    }
}

socket.on('game_created', (data) => {
    log('Partie créée', data);
    gameId = data.game_id;
    myPlayerId = data.player_id;
    currentGame = data.game;
    
    document.getElementById('lobby-game-code').textContent = gameId.toUpperCase();
    showLobby();
    updateLobby();
    
    if (isHost) {
        document.getElementById('start-button-container').classList.remove('hidden');
    }
});

socket.on('game_joined', (data) => {
    log('Partie rejointe', data);
    gameId = data.game_id;
    myPlayerId = data.player_id;
    currentGame = data.game;
    
    document.getElementById('lobby-game-code').textContent = gameId.toUpperCase();
    showLobby();
    updateLobby();
});

socket.on('player_joined', (data) => {
    log('Joueur rejoint', data);
    updateMessage(`${data.player_name} a rejoint la partie !`);
    if (!document.getElementById('lobby-screen').classList.contains('hidden')) {
        updateLobby();
    }
});

socket.on('player_disconnected', (data) => {
    log('Joueur déconnecté', data);
    updateMessage(`${data.player_name} s'est déconnecté`);
});

socket.on('game_started', (data) => {
    log('Partie démarrée', data);
    currentGame = data.game;
    showGame();
    updateGameDisplay();
});

socket.on('game_updated', (data) => {
    log('Jeu mis à jour', data);
    currentGame = data.game;
    updateGameDisplay();
    
    if (data.message) {
        updateMessage(data.message);
    }
});

socket.on('select_hardship_target', (data) => {
    log('Sélectionner cible malus', data);
    showHardshipModal(data.card, data.available_targets, data.from_discard || false);
});

socket.on('select_salaries_for_acquisition', (data) => {
    log('Sélectionner salaires pour acquisition', data);
    showSalarySelectionModal(data.card, data.required_cost, data.available_salaries, data.heritage_available || 0);
});

// Écouteurs pour les cartes spéciales
socket.on('select_from_discard', (data) => {
    log('Étoile filante - sélection défausse', data);
    showStarModal(data.discard_cards);
});

socket.on('game_over', (data) => {
    log('Partie terminée', data);
    showEndScreen(data.scores);
});

socket.on('error', (data) => {
    log('Erreur reçue', data);
    alert('Erreur: ' + data.message);
});



function updateLobby() {
    if (!currentGame) {
        log('updateLobby: pas de currentGame');
        return;
    }
    
    log('Mise à jour lobby', currentGame);
    
    const container = document.getElementById('lobby-players');
    container.innerHTML = currentGame.players.map((player, i) => {
        const status = player.connected ? '✅ Connecté' : '⏳ En attente...';
        const isYou = i === myPlayerId ? ' (Vous)' : '';
        const color = player.connected ? 'bg-green-100' : 'bg-gray-100';
        
        return `
            <div class="flex items-center justify-between p-3 ${color} rounded-lg">
                <span class="font-semibold">${player.name}${isYou}</span>
                <span class="text-sm">${status}</span>
            </div>
        `;
    }).join('');
    
    const connectedCount = currentGame.players.filter(p => p.connected).length;
    document.getElementById('players-count').textContent = 
        `${connectedCount} / ${currentGame.num_players} joueurs connectés`;
    
    if (isHost && connectedCount >= 2) {
        document.querySelector('#start-button-container button').disabled = false;
    }
}

function updateGameDisplay() {
    if (!currentGame) {
        log('updateGameDisplay: pas de currentGame');
        return;
    }
    
    log('Mise à jour affichage jeu', {
        deck: currentGame.deck_count,
        discard: currentGame.discard ? currentGame.discard.length : 0,
        phase: currentGame.phase,
        currentPlayer: currentGame.current_player,
        myId: myPlayerId
    });
    
    const myPlayer = currentGame.players[myPlayerId];
    const currentPlayer = currentGame.players[currentGame.current_player];
    const isMyTurn = currentGame.current_player === myPlayerId;
    
    document.getElementById('current-player-name').textContent = 
        isMyTurn ? 'À vous de jouer !' : `Tour de ${currentPlayer.name}`;
    document.getElementById('deck-count').textContent = currentGame.deck_count || 0;
    document.getElementById('discard-count').textContent = currentGame.discard ? currentGame.discard.length : 0;
    
    // Afficher la dernière carte défaussée
    if (currentGame.last_discard) {
        document.getElementById('last-discard-container').classList.remove('hidden');
        document.getElementById('last-discard-card').innerHTML = createCardHTML(currentGame.last_discard, false);
    } else {
        document.getElementById('last-discard-container').classList.add('hidden');
    }

    // Afficher le casino si disponible
    log('Casino status', currentGame.casino);
    updateCasinoDisplay(currentGame.casino);
    
    // Mise a jour du mode arc en ciel
    if (currentGame.pending_special && currentGame.pending_special.type === 'arc_en_ciel') {
        const actionsCount = (currentGame.pending_special.cards_played || 0) + 
                            (currentGame.pending_special.cards_discarded || 0) + 
                            (currentGame.pending_special.card_bets || 0);
        updateArcRemaining(actionsCount);
        
        // Afficher la bannière si elle est cachée
        if (document.getElementById('arc-en-ciel-banner').classList.contains('hidden')) {
            document.getElementById('arc-en-ciel-banner').classList.remove('hidden');
        }
    } else {
        // Cacher la bannière si le mode n'est plus actif
        if (!document.getElementById('arc-en-ciel-banner').classList.contains('hidden')) {
            document.getElementById('arc-en-ciel-banner').classList.add('hidden');
        }
    }

    // Afficher l'héritage si disponible
    if (myPlayer.heritage > 0) {
        const heritageDisplay = `
            <div class="bg-purple-100 border-2 border-purple-300 rounded-lg p-3 mb-4">
                <div class="flex items-center gap-2">
                    <span class="text-2xl">🎁</span>
                    <div>
                        <div class="font-bold">Héritage disponible</div>
                        <div class="text-lg text-purple-600">${myPlayer.heritage} 💰</div>
                    </div>
                </div>
            </div>
        `;
        if (!document.getElementById('heritage-display')) {
            const actionsPanel = document.getElementById('actions-panel');
            const heritageDiv = document.createElement('div');
            heritageDiv.id = 'heritage-display';
            heritageDiv.innerHTML = heritageDisplay;
            actionsPanel.parentNode.insertBefore(heritageDiv, actionsPanel.nextSibling);
        } else {
            document.getElementById('heritage-display').innerHTML = heritageDisplay;
        }
    } else {
        const heritageDiv = document.getElementById('heritage-display');
        if (heritageDiv) {
            heritageDiv.remove();
        }
    }
    
    if (isMyTurn) {
        if (myPlayer.skip_turns > 0) {
            updateMessage(`⏸️ Vous devez passer votre tour (${myPlayer.skip_turns} tour(s) restant(s)) - Cliquez sur "Passer mon tour"`);
        } else if (currentGame.phase === 'draw') {
            updateMessage('Piochez une carte de la pioche ou de la défausse (ou défaussez un métier/mariage/adultère avant, ou passez votre tour)');
        } else {
            updateMessage('Jouez ou défaussez une carte de votre main (ou passez votre tour)');
        }
    } else {
        updateMessage(`En attente de ${currentPlayer.name}...`);
    }
    
    const canDraw = isMyTurn && currentGame.phase === 'draw' && myPlayer.skip_turns === 0;
    const canPlay = isMyTurn && currentGame.phase === 'play';
    const canSkipVoluntarily = isMyTurn;
    // 🆕 canDiscardPlayed ne contrôle plus les métiers intérimaires
    // Il contrôle seulement les mariages/adultères et métiers non-intérimaires
    const canDiscardPlayed = isMyTurn && currentGame.phase === 'draw' && myPlayer.skip_turns === 0;
        
    document.getElementById('draw-deck-btn').disabled = !canDraw;
    document.getElementById('draw-discard-btn').disabled = !canDraw || (currentGame.discard && currentGame.discard.length === 0);
    document.getElementById('skip-turn-btn').disabled = !canSkipVoluntarily;
    
    const scoresContainer = document.getElementById('players-scores');
    scoresContainer.innerHTML = currentGame.players.map((player, i) => {
        const smiles = calculateSmiles(player);
        const isCurrent = i === currentGame.current_player;
        const isMe = i === myPlayerId;
        const bgColor = isCurrent ? 'bg-yellow-400 shadow-lg transform scale-105' : 
                        isMe ? 'bg-blue-100' : 'bg-white';
        
        return `
            <div class="p-3 rounded-lg ${bgColor}">
                <div class="font-bold text-sm">${player.name}${isMe ? ' (Vous)' : ''}</div>
                <div class="flex items-center gap-1 text-lg">
                    <span>😊</span>
                    <span>${smiles}</span>
                </div>
                ${player.skip_turns > 0 ? `<div class="text-xs text-orange-600">⏸️ ${player.skip_turns} tour(s)</div>` : ''}
                ${!player.connected ? '<div class="text-xs text-red-600">Déconnecté</div>' : ''}
            </div>
        `;
    }).join('');
    
    // Main du joueur
    log('Main du joueur', myPlayer.hand);
    const handContainer = document.getElementById('player-hand');
    document.getElementById('hand-count').textContent = myPlayer.hand ? myPlayer.hand.length : 0;

    // ✅ AJOUT : Vérifier si on est en mode arc-en-ciel
    const isArcMode = currentGame.pending_special && currentGame.pending_special.type === 'arc_en_ciel';

    if (myPlayer.hand && myPlayer.hand.length > 0) {
        handContainer.innerHTML = myPlayer.hand.map(card => {
            // ✅ MODIFICATION : En mode arc-en-ciel, permettre de jouer OU défausser
            const canPlayOrDiscard = isArcMode || canPlay;
            return createCardHTML(card, canPlayOrDiscard);  // ← Utiliser canPlayOrDiscard au lieu de canPlay
        }).join('');
    } else {
        handContainer.innerHTML = '<p class="text-gray-500">Aucune carte en main</p>';
    }

    // Afficher les cartes par catégories
    displayPlayerCategories(myPlayer, canDiscardPlayed);
    
    // Afficher les attaques reçues
    const hardshipsContainer = document.getElementById('hardships-received');
    if (myPlayer.received_hardships && myPlayer.received_hardships.length > 0) {
        hardshipsContainer.innerHTML = myPlayer.received_hardships.map(hardship => {
            return `
                <div class="bg-red-200 border-2 border-red-400 rounded-lg p-2 text-sm">
                    <span class="font-semibold">⚠️ ${hardship}</span>
                </div>
            `;
        }).join('');
    } else {
        hardshipsContainer.innerHTML = '<p class="text-gray-500">Aucune attaque reçue</p>';
    }
    
    const othersContainer = document.getElementById('other-players');
    othersContainer.innerHTML = currentGame.players
        .filter((_, i) => i !== myPlayerId)
        .map(player => {
            const handCount = player.hand_count || (player.hand ? player.hand.length : 0);
            return `
                <div class="bg-white rounded-lg shadow-lg p-4">
                    <h3 class="font-bold mb-3">
                        ${player.name} 
                        ${player.connected ? '' : '<span class="text-red-600 text-sm">(Déconnecté)</span>'}
                        ${player.skip_turns > 0 ? `<span class="text-orange-600 text-sm">(⏸️ ${player.skip_turns} tour(s))</span>` : ''}
                    </h3>
                    <div class="text-sm text-gray-600 mb-2">${handCount} cartes en main</div>
                    
                    ${player.received_hardships && player.received_hardships.length > 0 ? `
                        <div class="mb-2">
                            <div class="text-xs font-semibold text-red-700 mb-1">Attaques reçues:</div>
                            <div class="flex flex-wrap gap-1">
                                ${player.received_hardships.map(h => `<span class="bg-red-200 text-xs px-2 py-1 rounded">⚠️ ${h}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${displayOtherPlayerCategories(player)}
                </div>
            `;
        }).join('');
}


function displayPlayerCategories(player, canDiscard) {
    const categories = {
        'vie professionnelle': 'player-vie-pro',
        'vie personnelle': 'player-vie-perso',
        'acquisitions': 'player-acquisitions',
        'salaire dépensé': 'player-salaire-depense',
        'cartes spéciales': 'player-speciales'
    };
    
    // 🆕 Vérifier si c'est le tour du joueur
    const isMyTurn = currentGame.current_player === player.id;
    
    for (const [category, elementId] of Object.entries(categories)) {
        const container = document.getElementById(elementId);
        const cards = player.played[category] || [];
        
        if (cards.length > 0) {
            // 🆕 Logique améliorée pour chaque carte
            container.innerHTML = cards.map(card => {
                let canDiscardCard = false;
                
                if (isMyTurn) {
                    // 🆕 Métier intérimaire : défaussable à tout moment
                    if (card.type === 'job' && card.status === 'intérimaire') {
                        canDiscardCard = true;
                    }
                    // Autres cartes : seulement en phase draw
                    else if (canDiscard && (category === 'vie professionnelle' || category === 'vie personnelle')) {
                        canDiscardCard = true;
                    }
                }
                
                return createCardHTML(card, false, true, canDiscardCard);
            }).join('');
        } else {
            container.innerHTML = '<p class="text-gray-500 text-sm">Aucune carte</p>';
        }
    }
}

function displayOtherPlayerCategories(player) {
    const categoryIcons = {
        'vie professionnelle': '💼',
        'vie personnelle': '💕',
        'acquisitions': '🏠',
        'salaire dépensé': '💸',
        'cartes spéciales': '⭐'
    };
    
    let html = '';
    
    for (const [category, icon] of Object.entries(categoryIcons)) {
        const cards = player.played[category] || [];
        if (cards.length > 0) {
            html += `
                <div class="mb-2">
                    <div class="text-xs font-semibold text-gray-700 mb-1">${icon} ${category}</div>
                    <div class="flex flex-wrap gap-1">
                        ${cards.map(card => createCardHTML(card, false, false, false, true)).join('')}
                    </div>
                </div>
            `;
        }
    }
    
    return html || '<p class="text-gray-500">Aucune carte posée</p>';
}

function createCardHTML(card, canPlay, isPlayed = false, canDiscard = false, isSmall = false) {
    const colors = {
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

    const icons = {
        'job': '💼', 'study': '📚', 'salary': '💰',
        'flirt': '💕', 'marriage': '💍', 'child': '👶',
        'animal': '🐾', 'adultere': '💔', 'house': '🏠',
        'travel': '✈️', 'hardship': '⚠️', 'special': '⭐', 'other': '🎖'
    };

    const label = getCardLabel(card);
    const color = colors[card.type] || 'bg-gray-100 border-gray-300';
    const icon = icons[card.type] || '🎴';
    
    const cursor = (canPlay || canDiscard) ? 'cursor-pointer hover:scale-105' : '';
    const sizeClass = isSmall ? 'min-w-[100px]' : 'min-w-[140px]';
    
    const canDiscardPlayed = isPlayed && canDiscard && 
                            (card.type === 'job' || card.type === 'marriage' || card.type === 'adultere');
    
    let discardButtonText = '🗑️ Défausser';
    if (card.type === 'job' && card.status === 'intérimaire') {
        discardButtonText = '👋 Démissionner';
    }

    // Construire le chemin de l'image
    const imagePath = card.image ? `/ressources/${card.image}` : '';
    
    // ID unique pour gérer le fallback
    const cardElementId = `card-${card.id}`;
    
    // HTML avec image prioritaire et fallback sur texte
    const cardContentHTML = imagePath ? `
        <div id="${cardElementId}" class="card-content h-full w-full relative">
            <!-- Image (affichée par défaut) -->
            <div class="card-image-container h-full w-full flex flex-col relative">
                <img src="${imagePath}" 
                     alt="${label}" 
                     class="w-full h-full object-contain rounded"
                     onerror="handleImageError('${cardElementId}')">
                
                <!-- Boutons par-dessus l'image -->
                <div class="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/70 to-transparent">
                    ${canPlay ? `
                        <div class="flex gap-1">
                            <button onclick="playCard('${card.id}')" class="flex-1 ${card.type === 'hardship' ? 'bg-red-500 hover:bg-red-600' : card.type === 'special' ? 'bg-yellow-500 hover:bg-yellow-600' : 'bg-green-500 hover:bg-green-600'} text-white text-xs px-2 py-1 rounded font-semibold shadow-lg">
                                ${card.type === 'hardship' ? 'Attaquer' : card.type === 'special' ? '⭐ Activer' : 'Jouer'}
                            </button>
                            <button onclick="discardCard('${card.id}')" class="flex-1 bg-gray-500 text-white text-xs px-2 py-1 rounded hover:bg-gray-600 font-semibold shadow-lg">
                                Défausser
                            </button>
                        </div>
                    ` : ''}
                    ${canDiscardPlayed ? `
                        <button onclick="discardPlayedCard('${card.id}')" class="w-full bg-red-500 text-white text-xs px-2 py-1 rounded hover:bg-red-600 font-semibold shadow-lg">
                            ${discardButtonText}
                        </button>
                    ` : ''}
                </div>
            </div>
            
            <!-- Fallback texte (caché par défaut) -->
            <div class="card-text-fallback hidden h-full w-full flex flex-col justify-between p-3">
                <div>
                    <div class="flex items-center gap-2 mb-1">
                        <span class="${isSmall ? 'text-sm' : ''}">${icon}</span>
                        <span class="font-semibold ${isSmall ? 'text-xs' : 'text-sm'}">${label}</span>
                    </div>
                    ${card.smiles > 0 ? `
                        <div class="flex items-center gap-1 text-yellow-600">
                            <span class="${isSmall ? 'text-xs' : ''}">😊</span>
                            <span class="${isSmall ? 'text-xs' : 'text-sm'}">${card.smiles}</span>
                        </div>
                    ` : ''}
                </div>
                <div class="mt-2">
                    ${canPlay ? `
                        <div class="flex gap-1">
                            <button onclick="playCard('${card.id}')" class="flex-1 ${card.type === 'hardship' ? 'bg-red-500 hover:bg-red-600' : card.type === 'special' ? 'bg-yellow-500 hover:bg-yellow-600' : 'bg-green-500 hover:bg-green-600'} text-white text-xs px-2 py-1 rounded">
                                ${card.type === 'hardship' ? 'Attaquer' : card.type === 'special' ? '⭐ Activer' : 'Jouer'}
                            </button>
                            <button onclick="discardCard('${card.id}')" class="flex-1 bg-gray-500 text-white text-xs px-2 py-1 rounded hover:bg-gray-600">
                                Défausser
                            </button>
                        </div>
                    ` : ''}
                    ${canDiscardPlayed ? `
                        <button onclick="discardPlayedCard('${card.id}')" class="w-full bg-red-500 text-white text-xs px-2 py-1 rounded hover:bg-red-600">
                            ${discardButtonText}
                        </button>
                    ` : ''}
                </div>
            </div>
        </div>
    ` : `
        <!-- Pas d'image : afficher directement le texte -->
        <div class="p-3 h-full flex flex-col justify-between">
            <div>
                <div class="flex items-center gap-2 mb-1">
                    <span class="${isSmall ? 'text-sm' : ''}">${icon}</span>
                    <span class="font-semibold ${isSmall ? 'text-xs' : 'text-sm'}">${label}</span>
                </div>
                ${card.smiles > 0 ? `
                    <div class="flex items-center gap-1 text-yellow-600">
                        <span class="${isSmall ? 'text-xs' : ''}">😊</span>
                        <span class="${isSmall ? 'text-xs' : 'text-sm'}">${card.smiles}</span>
                    </div>
                ` : ''}
            </div>
            <div class="mt-2">
                ${canPlay ? `
                    <div class="flex gap-1">
                        <button onclick="playCard('${card.id}')" class="flex-1 ${card.type === 'hardship' ? 'bg-red-500 hover:bg-red-600' : card.type === 'special' ? 'bg-yellow-500 hover:bg-yellow-600' : 'bg-green-500 hover:bg-green-600'} text-white text-xs px-2 py-1 rounded">
                            ${card.type === 'hardship' ? 'Attaquer' : card.type === 'special' ? '⭐ Activer' : 'Jouer'}
                        </button>
                        <button onclick="discardCard('${card.id}')" class="flex-1 bg-gray-500 text-white text-xs px-2 py-1 rounded hover:bg-gray-600">
                            Défausser
                        </button>
                    </div>
                ` : ''}
                ${canDiscardPlayed ? `
                    <button onclick="discardPlayedCard('${card.id}')" class="w-full bg-red-500 text-white text-xs px-2 py-1 rounded hover:bg-red-600">
                        ${discardButtonText}
                    </button>
                ` : ''}
            </div>
        </div>
    `;

    return `
        <div class="card ${color} border-2 rounded-lg ${sizeClass} ${cursor} overflow-hidden" style="height: 200px;">
            ${cardContentHTML}
        </div>
    `;
}

// Nouvelle fonction pour gérer l'erreur de chargement d'image
function handleImageError(cardElementId) {
    const cardElement = document.getElementById(cardElementId);
    if (cardElement) {
        // Cacher l'image et afficher le fallback texte
        const imageContainer = cardElement.querySelector('.card-image-container');
        const textFallback = cardElement.querySelector('.card-text-fallback');
        
        if (imageContainer) imageContainer.classList.add('hidden');
        if (textFallback) textFallback.classList.remove('hidden');
    }
}

function getCardLabel(card) {
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

function calculateSmiles(player) {
    let total = 0;
    
    // Calculer depuis toutes les catégories
    for (const category in player.played) {
        const cards = player.played[category];
        total += cards.reduce((sum, card) => sum + (card.smiles || 0), 0);
    }
    
    // Vérifier le bonus licorne + arc-en-ciel + étoile
    let allCards = [];
    for (const category in player.played) {
        allCards = allCards.concat(player.played[category]);
    }
    
    const hasLicorne = allCards.some(c => c.type === 'animal' && c.subtype === 'licorne');
    const hasArc = allCards.some(c => c.type === 'special' && c.subtype === 'arc en ciel');
    const hasEtoile = allCards.some(c => c.type === 'special' && c.subtype === 'etoile filante');
    
    if (hasLicorne && hasArc && hasEtoile) {
        total += 3;
    }
    
    return total;
}

function updateMessage(msg) {
    const messageEl = document.getElementById('message');
    messageEl.textContent = msg;
    messageEl.classList.remove('hidden');
}

function showEndScreen(scores) {
    document.getElementById('game-screen').classList.add('hidden');
    document.getElementById('end-screen').classList.remove('hidden');
    
    document.getElementById('winner-name').textContent = `Gagnant : ${scores[0][0]}`;
    
    const medals = ['🥇', '🥈', '🥉'];
    const scoresHTML = scores.map((score, i) => {
        const medal = medals[i] || `#${i + 1}`;
        const bgColor = i === 0 ? 'bg-gradient-to-r from-yellow-200 to-yellow-300 border-4 border-yellow-500' :
                        i === 1 ? 'bg-gray-200 border-2 border-gray-400' :
                        i === 2 ? 'bg-orange-200 border-2 border-orange-400' :
                        'bg-white border-2 border-gray-300';
        
        return `
            <div class="p-6 rounded-lg ${bgColor}">
                <div class="flex justify-between items-center">
                    <div class="flex items-center gap-4">
                        <div class="text-3xl font-bold">${medal}</div>
                        <div>
                            <div class="text-2xl font-bold">${score[0]}</div>
                            <div class="flex items-center gap-2 text-xl">
                                <span>😊</span>
                                <span class="font-bold text-yellow-600">${score[1]} smiles</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    document.getElementById('final-scores').innerHTML = scoresHTML;
}