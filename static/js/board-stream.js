// ═══════════════════════════════════════════════════════════
//  board-stream.js — Connexion WebSocket (Socket.IO)
//  Dépendances : board.js (window.updateBoard, window.GAME_ID, window.PSEUDO)
// ═══════════════════════════════════════════════════════════

const socket = io();

socket.on('connect', () => {
    console.log('✅ Connecté, SID:', socket.id);
    socket.emit('join', {
        game_id: window.GAME_ID,
        pseudo:  window.PSEUDO,
    });
});

socket.on('game_update', (state) => {
    console.log('📦 game_update reçu — joueur courant :', state.current_player);
    if (typeof window.updateBoard === 'function') {
        window.updateBoard(state);
    } else {
        console.error('updateBoard non défini');
    }
});

socket.on('disconnect', () => {
    console.warn('❌ Déconnecté');
});
console.log('=== DEBUG WS ===');
console.log('GAME_ID:', window.GAME_ID);
console.log('PSEUDO:', window.PSEUDO);
