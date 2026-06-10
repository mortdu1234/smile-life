// ═══════════════════════════════════════════════════════════
//  board-stream.js — Connexion WebSocket (Socket.IO)
//  Dépendances : board.js (window.updateBoard, window.GAME_ID, window.PSEUDO)
// ═══════════════════════════════════════════════════════════

const socket = io({
    path: `${window.BASE_URL}/socket.io/`
});
socket.on('connect', () => {
    console.log('✅ Connecté, SID:', socket.id);
    socket.emit('join', {
        game_id: window.GAME_ID,
        pseudo:  window.PSEUDO,
    });
});

socket.on('game_update', (state) => {
    console.log('📦 game_update reçu — joueur courant :', state);
    if (typeof window.updateBoard === 'function') {
        window.updateBoard(state);
    } else {
        console.error('updateBoard non défini');
    }
});

socket.on('disconnect', () => {
    console.warn('❌ Déconnecté');
});
