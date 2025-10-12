const socket = io();

let gameId = null;
let currentGame = null;
let myPlayerId = null;
let isHost = false;
let pendingHardshipCard = null;
let fromDiscard = false;

// Variables pour la sélection de salaires
let pendingAcquisitionCard = null;
let requiredCost = 0;
let selectedSalaries = [];
let heritageAvailable = 0;
let heritageUsed = 0;

// Variables pour les cartes spéciales
let selectedVengeanceHardship = null;
let availableVengeanceTargets = [];

function log(message, data) {
    console.log(`[DEBUG] ${message}`, data || '');
}