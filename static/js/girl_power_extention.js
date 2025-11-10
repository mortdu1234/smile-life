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