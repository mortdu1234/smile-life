const socket = io();

socket.on('connect', () => {
    console.log('✅ Connecté, SID:', socket.id);
    socket.emit('join', {
        game_id: window.GAME_ID,
        pseudo:  window.PSEUDO   // ← à t'assurer que window.PSEUDO est défini dans board.html
    });
});

// Dans board-stream.js, remplace temporairement updateBoard(state) par :
socket.on('game_update', (state) => {
    console.log('players[0]:', JSON.stringify(state.players[0], null, 2));
    if (typeof window.updateBoard === 'function') {
        updateBoard(state);
    } else {
        console.error('updateBoard non défini');
    }
});

socket.on('disconnect', () => {
    console.warn('❌ Déconnecté');
});