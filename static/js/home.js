let deckConfigContext = 'create';
const presetDecks = {
    "standard": {
        name: "Jeu Standard",
        description: "Configuration par défaut du jeu",
        config: null  // null = utiliser les valeurs par défaut de cardCategories
    },
    "test": {
        name: "Version de test",
        description: "aucune carte",
        config: {

        }
    }
};

const cardCategories = {
    "Jeu Standards": [
        // --- PROFESSIONS ---
        { id: "architecte", name: "Architecte", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/architecte.png" },
        { id: "astronaute", name: "Astronaute", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/astronaute.png" },
        { id: "avocat", name: "Avocat", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/avocat.png" },
        { id: "bandit", name: "Bandit", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/bandit.png" },
        { id: "barman", name: "Barman", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/barman.png" },
        { id: "chef_des_ventes", name: "Chef des ventes", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/chef_des_ventes.png" },
        { id: "chef_des_achats", name: "Chef des achats", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/chef_des_achats.png" },
        { id: "chercheur", name: "Chercheur", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/chercheur.png" },
        { id: "chirurgien", name: "Chirurgien", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/chirurgien.png" },
        { id: "designer", name: "Designer", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/designer.png" },
        { id: "ecrivain", name: "Écrivain", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/ecrivain.png" },
        { id: "garagiste", name: "Garagiste", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/garagiste.png" },
        { id: "gourou", name: "Gourou", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/gourou.png" },
        { id: "jardinier", name: "Jardinier", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/jardinier.png" },
        { id: "journaliste", name: "Journaliste", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/journaliste.png" },
        { id: "medecin", name: "Médecin", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/medecin.png" },
        { id: "medium", name: "Médium", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/medium.png" },
        { id: "militaire", name: "Militaire", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/militaire.png" },
        { id: "pharmacien", name: "Pharmacien", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/pharmacien.png" },
        { id: "pilote_de_ligne", name: "Pilote de ligne", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/pilote_de_ligne.png" },
        { id: "pizzaiolo", name: "Pizzaiolo", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/pizzaiolo.png" },
        { id: "plombier", name: "Plombier", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/plombier.png" },
        { id: "policier", name: "Policier", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/policier.png" },
        { id: "prof_anglais", name: "Prof d’anglais", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/prof_anglais.png" },
        { id: "prof_francais", name: "Prof de français", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/prof_francais.png" },
        { id: "prof_histoire", name: "Prof d’histoire", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/prof_histoire.png" },
        { id: "prof_maths", name: "Prof de maths", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/prof_maths.png" },
        { id: "serveur", name: "Serveur", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/serveur.png" },
        { id: "stripteaser", name: "Strip-teaseur", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/stripteaser.png" },
        { id: "grand_prof", name: "Grand Prof", defaultCount: 1, image: "personnal_life/professionnal_life/JobCards/grand_prof.png" },

        // --- ÉTUDES ---
        { id: "study_simple", name: "Études simples", defaultCount: 22, image: "personnal_life/professionnal_life/StudyCards/study1.png" },
        { id: "study_double", name: "Études doubles", defaultCount: 3, image: "personnal_life/professionnal_life/StudyCards/study2.png" },

        // --- SALAIRES ---
        { id: "salary_1", name: "Salaire 1", defaultCount: 1, image: "personnal_life/professionnal_life/SalaryCards/salary1.png" },
        { id: "salary_2", name: "Salaire 2", defaultCount: 1, image: "personnal_life/professionnal_life/SalaryCards/salary2.png" },
        { id: "salary_3", name: "Salaire 3", defaultCount: 1, image: "personnal_life/professionnal_life/SalaryCards/salary3.png" },
        { id: "salary_4", name: "Salaire 4", defaultCount: 1, image: "personnal_life/professionnal_life/SalaryCards/salary4.png" },

        // --- FLIRTS ---
        { id: "flirt_bar", name: "Flirt au bar", defaultCount: 2, image: "personnal_life/flirts/bar.png" },
        { id: "flirt_boite_de_nuit", name: "Flirt en boîte de nuit", defaultCount: 2, image: "personnal_life/flirts/boite_de_nuit.png" },
        { id: "flirt_cinema", name: "Flirt au cinéma", defaultCount: 2, image: "personnal_life/flirts/cinema.png" },
        { id: "flirt_internet", name: "Flirt sur internet", defaultCount: 2, image: "personnal_life/flirts/internet.png" },
        { id: "flirt_parc", name: "Flirt au parc", defaultCount: 2, image: "personnal_life/flirts/parc.png" },
        { id: "flirt_restaurant", name: "Flirt au restaurant", defaultCount: 2, image: "personnal_life/flirts/restaurant.png" },
        { id: "flirt_theatre", name: "Flirt au théâtre", defaultCount: 2, image: "personnal_life/flirts/theatre.png" },
        { id: "flirt_zoo", name: "Flirt au zoo", defaultCount: 2, image: "personnal_life/flirts/zoo.png" },

        // --- FLIRTS AVEC ENFANT ---
        { id: "flirt_child_camping", name: "Flirt au camping (avec enfant)", defaultCount: 2, image: "personnal_life/flirts/camping.png" },
        { id: "flirt_child_hotel", name: "Flirt à l’hôtel (avec enfant)", defaultCount: 2, image: "personnal_life/flirts/hotel.png" },

        // --- MARIAGES ---
        { id: "mariage_corps_nuds", name: "Mariage à Corps-Nuds", defaultCount: 1, image: "personnal_life/mariages/mariage_corps_nuds.png" },
        { id: "mariage_montcuq", name: "Mariage à Montcuq", defaultCount: 1, image: "personnal_life/mariages/mariage_montcuq.png" },
        { id: "mariage_monteton", name: "Mariage à Monteton", defaultCount: 1, image: "personnal_life/mariages/mariage_monteton.png" },
        { id: "mariage_sainte_vierge", name: "Mariage à Sainte-Vierge", defaultCount: 1, image: "personnal_life/mariages/mariage_sainte_vierge.png" },
        { id: "mariage_fourqueux", name: "Mariage à Fourqueux", defaultCount: 1, image: "personnal_life/mariages/mariage_fourqueux.png" },
        { id: "adultere", name: "Adultère", defaultCount: 1, image: "personnal_life/mariages/adultere.png" },

        // --- ENFANTS ---
        { id: "child_diana", name: "Diana", defaultCount: 1, image: "personnal_life/children/diana.png" },
        { id: "child_harry", name: "Harry", defaultCount: 1, image: "personnal_life/children/harry.png" },
        { id: "child_hermione", name: "Hermione", defaultCount: 1, image: "personnal_life/children/hermione.png" },
        { id: "child_lara", name: "Lara", defaultCount: 1, image: "personnal_life/children/lara.png" },
        { id: "child_leia", name: "Leia", defaultCount: 1, image: "personnal_life/children/leia.png" },
        { id: "child_luigi", name: "Luigi", defaultCount: 1, image: "personnal_life/children/luigi.png" },
        { id: "child_luke", name: "Luke", defaultCount: 1, image: "personnal_life/children/luke.png" },
        { id: "child_mario", name: "Mario", defaultCount: 1, image: "personnal_life/children/mario.png" },
        { id: "child_rocky", name: "Rocky", defaultCount: 1, image: "personnal_life/children/rocky.png" },
        { id: "child_zelda", name: "Zelda", defaultCount: 1, image: "personnal_life/children/zelda.png" },

        // --- ANIMAUX ---
        { id: "animal_chat", name: "Chat", defaultCount: 1, image: "aquisition_cards/animals/chat.png" },
        { id: "animal_chien", name: "Chien", defaultCount: 1, image: "aquisition_cards/animals/chien.png" },
        { id: "animal_lapin", name: "Lapin", defaultCount: 1, image: "aquisition_cards/animals/lapin.png" },
        { id: "animal_licorne", name: "Licorne", defaultCount: 1, image: "aquisition_cards/animals/licorne.png" },
        { id: "animal_poussin", name: "Poussin", defaultCount: 1, image: "aquisition_cards/animals/poussin.png" },

        // --- MAISONS ---
        { id: "house_petite", name: "Petite maison", defaultCount: 2, image: "aquisition_cards/houses/maison1.png" },
        { id: "house_moyenne", name: "Maison moyenne", defaultCount: 2, image: "aquisition_cards/houses/maison2.png" },
        { id: "house_grande", name: "Grande maison", defaultCount: 1, image: "aquisition_cards/houses/maison3.png" },

        // --- VOYAGES ---
        { id: "trip_le_caire", name: "Voyage au Caire", defaultCount: 1, image: "aquisition_cards/trip/le_caire.png" },
        { id: "trip_londres", name: "Voyage à Londres", defaultCount: 1, image: "aquisition_cards/trip/londres.png" },
        { id: "trip_new_york", name: "Voyage à New York", defaultCount: 1, image: "aquisition_cards/trip/new_york.png" },
        { id: "trip_rio", name: "Voyage à Rio", defaultCount: 1, image: "aquisition_cards/trip/rio.png" },
        { id: "trip_sydney", name: "Voyage à Sydney", defaultCount: 1, image: "aquisition_cards/trip/sydney.png" },

        // --- CARTES SPÉCIALES ---
        { id: "troc", name: "Troc", defaultCount: 1, image: "special_cards/troc.png" },
        { id: "tsunami", name: "Tsunami", defaultCount: 1, image: "special_cards/tsunami.png" },
        { id: "heritage", name: "Héritage", defaultCount: 1, image: "special_cards/heritage.png" },
        { id: "piston", name: "Piston", defaultCount: 1, image: "special_cards/piston.png" },
        { id: "anniversaire", name: "Anniversaire", defaultCount: 1, image: "special_cards/anniversaire.png" },
        { id: "casino", name: "Casino", defaultCount: 1, image: "special_cards/casino.png" },
        { id: "chance", name: "Chance", defaultCount: 1, image: "special_cards/chance.png" },
        { id: "etoile_filante", name: "Étoile filante", defaultCount: 1, image: "special_cards/etoile_filante.png" },
        { id: "vengeance", name: "Vengeance", defaultCount: 1, image: "special_cards/vengeance.png" },
        { id: "arc_en_ciel", name: "Arc-en-ciel", defaultCount: 1, image: "special_cards/arc_en_ciel.png" },
        
        // --- COUPS DURS ---
        { id: "accident", name: "Accident", defaultCount: 5, image: "hardship_cards/accident.png" },
        { id: "burnout", name: "Burn-out", defaultCount: 5, image: "hardship_cards/burnout.png" },
        { id: "divorce", name: "Divorce", defaultCount: 5, image: "hardship_cards/divorce.png" },
        { id: "tax", name: "Impôts", defaultCount: 5, image: "hardship_cards/tax.png" },
        { id: "licenciement", name: "Licenciement", defaultCount: 5, image: "hardship_cards/licenciement.png" },
        { id: "maladie", name: "Maladie", defaultCount: 5, image: "hardship_cards/maladie.png" },
        { id: "redoublement", name: "Redoublement", defaultCount: 5, image: "hardship_cards/redoublement.png" },
        { id: "prison", name: "Prison", defaultCount: 1, image: "hardship_cards/prison.png" },
        { id: "attentat", name: "Attentat", defaultCount: 1, image: "hardship_cards/attentat.png" },

        // --- AUTRES ---
        { id: "legion", name: "Légion d’honneur", defaultCount: 1, image: "personnal_life/professionnal_life/legion.png" },
        { id: "price", name: "Grand Prix d'Exelence", defaultCount: 2, image: "personnal_life/professionnal_life/price.png" }
    ],
    "Extentions Standards": [
        // --- MÉTIERS ---
        { id: "prof_education_sexuelle", name: "Prof d’éducation sexuelle", defaultCount: 0, image: "personnal_life/professionnal_life/JobCards/prof_education_sexuelle.png" },
        { id: "youtubeur", name: "Youtubeur", defaultCount: 0, image: "personnal_life/professionnal_life/JobCards/youtubeur.png" },
        { id: "coiffeur", name: "Coiffeur", defaultCount: 0, image: "personnal_life/professionnal_life/JobCards/coiffeur.png" },
        { id: "deejay", name: "Deejay", defaultCount: 0, image: "personnal_life/professionnal_life/JobCards/deejay.png" },
        
        // --- ÉTUDES ---
        
        // --- SALAIRES ---

        // --- FLIRTS ---
        
        // --- FLIRTS AVEC ENFANT ---
        
        // --- MARIAGES ---
        
        // --- ADULTÈRE ---
        
        // --- ENFANTS ---
        
        // --- ANIMAUX ---
        
        // --- MAISONS ---
        
        // --- VOYAGES ---
        
        // --- CARTES SPÉCIALES ---
        { id: "super_heritage", name: "Super héritage", defaultCount: 0, image: "special_cards/super_heritage.png" },
        { id: "muguet", name: "Muguet", defaultCount: 0, image: "special_cards/muguet.png" }
        
        // --- COUPS DURS ---

        // --- AUTRES ---
    
    ],
    "Extentions Apocalypse": [
        // --- MÉTIERS ---

        // --- ÉTUDES ---

        // --- SALAIRES ---

        // --- FLIRTS ---

        // --- FLIRTS AVEC ENFANT ---

        // --- MARIAGES ---

        // --- ADULTÈRE ---

        // --- ENFANTS ---

        // --- ANIMAUX ---

        // --- MAISONS ---

        // --- VOYAGES ---

        // --- CARTES SPÉCIALES ---
        
        // --- COUPS DURS ---

        // --- AUTRES ---
    
    ],
    "Extentions Luxe": [
        // --- MÉTIERS ---

        // --- ÉTUDES ---

        // --- SALAIRES ---

        // --- FLIRTS ---

        // --- FLIRTS AVEC ENFANT ---

        // --- MARIAGES ---

        // --- ADULTÈRE ---

        // --- ENFANTS ---

        // --- ANIMAUX ---

        // --- MAISONS ---

        // --- VOYAGES ---

        // --- CARTES SPÉCIALES ---
        
        // --- COUPS DURS ---

        // --- AUTRES ---
    
    ],
    "Extentions Fantastique": [
        // --- MÉTIERS ---

        // --- ÉTUDES ---

        // --- SALAIRES ---

        // --- FLIRTS ---

        // --- FLIRTS AVEC ENFANT ---

        // --- MARIAGES ---

        // --- ADULTÈRE ---

        // --- ENFANTS ---

        // --- ANIMAUX ---

        // --- MAISONS ---

        // --- VOYAGES ---

        // --- CARTES SPÉCIALES ---
        
        // --- COUPS DURS ---

        // --- AUTRES ---
    
    ],
    "Extentions Girl Power": [
        // --- MÉTIERS ---

        // --- ÉTUDES ---

        // --- SALAIRES ---

        // --- FLIRTS ---

        // --- FLIRTS AVEC ENFANT ---

        // --- MARIAGES ---

        // --- ADULTÈRE ---

        // --- ENFANTS ---

        // --- ANIMAUX ---

        // --- MAISONS ---

        // --- VOYAGES ---

        // --- CARTES SPÉCIALES ---
        { id: "girl_power", name: "Girl Power", defaultCount: 0, image: "special_cards/girl_power.png" },
        
        // --- COUPS DURS ---

        // --- AUTRES ---
    
    ],
    "Extentions Trash": [
        // --- MÉTIERS ---

        // --- ÉTUDES ---

        // --- SALAIRES ---

        // --- FLIRTS ---

        // --- FLIRTS AVEC ENFANT ---

        // --- MARIAGES ---

        // --- ADULTÈRE ---

        // --- ENFANTS ---

        // --- ANIMAUX ---

        // --- MAISONS ---

        // --- VOYAGES ---

        // --- CARTES SPÉCIALES ---
        
        // --- COUPS DURS ---

        // --- AUTRES ---
    
    ]
};




// État des quantités de cartes
let cardCounts = {};
let expandedCategories = {};

// Initialiser les quantités par défaut
function initializeCardCounts() {
  cardCounts = {};
  Object.values(cardCategories).forEach(category => {
    category.forEach(card => {
      cardCounts[card.id] = card.defaultCount;
    });
  });
}

// Valider et créer la partie avec la config
function validateDeckConfig() {
  const totalCards = getTotalCards();
  
  if (totalCards === 0) {
    alert('Veuillez sélectionner au moins une carte !');
    return;
  }
  
  log('Configuration validée', { totalCards, config: cardCounts });
  confirmDeckAndCreateGame(cardCounts);
}

// Calculer le total de cartes
function getTotalCards() {
  return Object.values(cardCounts).reduce((sum, count) => sum + count, 0);
}

// Mettre à jour l'affichage du total
function updateTotalDisplay() {
  const totalEl = document.getElementById('total-cards');
  if (totalEl) {
    totalEl.textContent = getTotalCards();
  }
}

// Toggle catégorie
function toggleCategory(categoryName) {
  expandedCategories[categoryName] = !expandedCategories[categoryName];
  renderCardSelector();
}

// Modifier la quantité d'une carte
function updateCardCount(cardId, delta) {
  cardCounts[cardId] = Math.max(0, cardCounts[cardId] + delta);
  renderCardSelector();
}

// Définir directement la quantité d'une carte via l'input
function setCardCount(cardId, value) {
  const numValue = parseInt(value) || 0;
  cardCounts[cardId] = Math.max(0, Math.min(99, numValue)); // Entre 0 et 99
  
  // Mettre à jour uniquement l'input et le total sans re-render complet
  const inputElement = document.getElementById(`input-${cardId}`);
  if (inputElement) {
    inputElement.value = cardCounts[cardId];
  }
  updateTotalDisplay();
}

// Réinitialiser aux valeurs par défaut
function resetDeckToDefault() {
  initializeCardCounts();
  renderCardSelector();
}

// Afficher le sélecteur de cartes
function renderCardSelector() {
  const container = document.getElementById('card-selector-container');
  if (!container) return;

  let html = renderPresetSelector();
  html += '<div class="space-y-4">';

  Object.entries(cardCategories).forEach(([categoryName, cards]) => {
    const isExpanded = expandedCategories[categoryName];
    const categoryTotal = cards.reduce((sum, card) => sum + cardCounts[card.id], 0);
    
    html += `
      <div class="border-2 rounded-lg overflow-hidden shadow-md">
        <button onclick="toggleCategory('${categoryName}')" 
                class="w-full bg-gradient-to-r from-purple-100 to-pink-100 p-4 flex items-center justify-between hover:from-purple-200 hover:to-pink-200 transition-colors">
          <div class="flex items-center gap-3">
            <span class="font-bold text-lg text-gray-800">${categoryName}</span>
            <span class="text-sm bg-white px-3 py-1 rounded-full text-gray-600 font-semibold">
              ${categoryTotal} cartes
            </span>
          </div>
          <span>${isExpanded ? '▲' : '▼'}</span>
        </button>
    `;

    if (isExpanded) {
      html += '<div class="p-4 bg-gray-50"><div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">';
      
      cards.forEach(card => {
        html += `
        <div class="bg-white rounded-lg shadow-lg overflow-hidden transform hover:scale-105 transition-transform">
            <div class="aspect-[2/3] bg-gradient-to-br from-blue-100 to-purple-100 relative overflow-hidden cursor-pointer"
                 onclick="showCardInfoInDeckConfig('${card.id}', '${card.name.replace(/'/g, "\\'")}')">
              <img src="/ressources/${card.image}" 
                  alt="${card.name}" 
                  class="w-full h-full object-cover"
                  onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
              <div class="absolute inset-0 hidden items-center justify-center p-4">
                  <div class="text-center">
                    <div class="text-4xl mb-2">🎴</div>
                    <div class="text-sm font-bold text-gray-700">${card.name}</div>
                  </div>
              </div>
              <!-- Indicateur cliquable -->
              <div class="absolute top-2 right-2 bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold shadow-lg">
                ℹ️
              </div>
            </div>
            <div class="p-3 bg-white border-t-2 border-gray-200">
              <div class="text-center mb-2">
                  <span class="font-semibold text-gray-800 text-sm">${card.name}</span>
              </div>
              <div class="flex items-center justify-center gap-2">
                  <button onclick="updateCardCount('${card.id}', -1)" 
                          class="w-8 h-8 flex items-center justify-center bg-red-500 hover:bg-red-600 text-white rounded-full transition-colors shadow-md ${cardCounts[card.id] === 0 ? 'opacity-50 cursor-not-allowed' : ''}"
                          ${cardCounts[card.id] === 0 ? 'disabled' : ''}>
                    <span class="text-xl">−</span>
                  </button>
                  <input type="number" 
                      id="input-${card.id}"
                      value="${cardCounts[card.id]}" 
                      min="0"
                      max="99"
                      onchange="setCardCount('${card.id}', this.value)"
                      onclick="this.select()"
                      class="w-12 h-8 text-center bg-gray-100 rounded-lg font-bold text-lg text-gray-800 border-2 border-gray-300 focus:border-purple-500 focus:outline-none">
                  <button onclick="updateCardCount('${card.id}', 1)" 
                          class="w-8 h-8 flex items-center justify-center bg-green-500 hover:bg-green-600 text-white rounded-full transition-colors shadow-md">
                    <span class="text-xl">+</span>
                  </button>
              </div>
            </div>
        </div>
        `;
      });
      
      html += '</div></div>';
    }

    html += '</div>';
  });

  html += '</div>';
  container.innerHTML = html;
  updateTotalDisplay();
}

// Nouvelle fonction pour afficher les infos de carte dans le config du deck
async function showCardInfoInDeckConfig(cardId, cardName) {
  try {
    const response = await fetch(`/api/card_rule/${cardId}`);
    const data = await response.json();
    
    if (data.success) {
      showCardRules(cardName, data.rule);
    } else {
      alert('Impossible de charger les informations de cette carte');
    }
  } catch (error) {
    console.error('Erreur lors du chargement des règles:', error);
    alert('Erreur de connexion au serveur');
  }
}




function backToCreate() {
    document.getElementById('card-selector-screen').classList.add('hidden');
    document.getElementById('create-screen').classList.remove('hidden');
}

function createGame() {
  const playerName = document.getElementById('host-name').value || 'Joueur 1';
  const numPlayers = parseInt(document.getElementById('num-players').value);
  
  log('Création de partie avec deck par défaut', {playerName, numPlayers});
  
  // ✨ Créer directement avec le deck par défaut (null = deck par défaut côté serveur)
  socket.emit('create_game', {
    player_name: playerName,
    num_players: numPlayers,
    deck_config: null  // null = utiliser le deck par défaut
  });
  
  isHost = true;
}

function showDeckConfigFromLobby() {
  deckConfigContext = 'lobby';
  document.getElementById('lobby-screen').classList.add('hidden');
  document.getElementById('card-selector-screen').classList.remove('hidden');
  
  // Initialiser avec la configuration actuelle du jeu
  initializeCardCounts();
  renderCardSelector();
}

function backFromDeckConfig() {
  if (deckConfigContext === 'lobby') {
    // Retour au lobby
    document.getElementById('card-selector-screen').classList.add('hidden');
    document.getElementById('lobby-screen').classList.remove('hidden');
  } else {
    // Retour à la création
    backToCreate();
  }
}

function validateDeckConfigFromLobby() {
  const totalCards = getTotalCards();
  
  if (totalCards === 0) {
    alert('Veuillez sélectionner au moins une carte !');
    return;
  }
  
  if (deckConfigContext === 'lobby') {
    // Envoyer la nouvelle configuration au serveur
    log('Mise à jour du deck depuis le lobby', { totalCards, config: cardCounts });
    
    socket.emit('update_deck_config', {
      game_id: gameId,
      deck_config: cardCounts
    });
    
    // Retour au lobby
    document.getElementById('card-selector-screen').classList.add('hidden');
    document.getElementById('lobby-screen').classList.remove('hidden');
    
    alert(`Deck mis à jour ! ${totalCards} cartes au total.`);
  } else {
    // Création initiale (non utilisé maintenant)
    confirmDeckAndCreateGame(cardCounts);
  }
}


// Charger un deck prédéfini
function loadPresetDeck(presetKey) {
    const preset = presetDecks[presetKey];
    if (!preset) return;
    
    if (preset.config === null) {
        // Utiliser les valeurs par défaut
        initializeCardCounts();
    } else {
        // Initialiser tous les compteurs à 0
        cardCounts = {};
        Object.values(cardCategories).forEach(category => {
            category.forEach(card => {
                cardCounts[card.id] = 0;
            });
        });
        
        // Appliquer la configuration du preset
        Object.entries(preset.config).forEach(([cardId, count]) => {
            if (cardCounts.hasOwnProperty(cardId)) {
                cardCounts[cardId] = count;
            }
        });
    }
    
    renderCardSelector();
    
    // Message de confirmation
    const totalCards = getTotalCards();
    alert(`Deck "${preset.name}" chargé ! ${totalCards} cartes au total.\n\n${preset.description}`);
}

// Afficher le sélecteur de presets dans l'UI
function renderPresetSelector() {
    return `
        <div class="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border-2 border-purple-200">
            <h3 class="font-bold text-lg mb-3 text-gray-800">📦 Decks Prédéfinis</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                ${Object.entries(presetDecks).map(([key, preset]) => `
                    <button onclick="loadPresetDeck('${key}')" 
                            class="bg-white hover:bg-purple-100 border-2 border-purple-300 rounded-lg p-4 text-left transition-all transform hover:scale-105 shadow-md">
                        <div class="font-bold text-purple-700 mb-1">${preset.name}</div>
                        <div class="text-sm text-gray-600">${preset.description}</div>
                    </button>
                `).join('')}
            </div>
        </div>
    `;
}


function confirmDeckAndCreateGame(deckConfig) {
    const playerName = sessionStorage.getItem('playerName') || 'Joueur 1';
    const numPlayers = parseInt(sessionStorage.getItem('numPlayers'));

    
    log('Création de partie', {playerName, numPlayers, deckConfig});
    backToCreate()
    
    socket.emit('create_game', {
        player_name: playerName,
        num_players: numPlayers,
        deck_config: deckConfig
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

function showCreateGame() {
    document.getElementById('menu-screen').classList.add('hidden');
    document.getElementById('create-screen').classList.remove('hidden');
}

function showGame() {
    document.getElementById('lobby-screen').classList.add('hidden');
    document.getElementById('game-screen').classList.remove('hidden');
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
    
      if (isHost) {
    document.getElementById('deck-config-button-container').classList.remove('hidden');
    document.getElementById('start-button-container').classList.remove('hidden');
    
    if (connectedCount >= 2) {
      document.querySelector('#start-button-container button').disabled = false;
    }
  }
};

socket.on('deck_updated', (data) => {
    log('Deck mis à jour', data);
    updateMessage(data.message);
    
    // Si on est dans le lobby, rafraîchir
    if (!document.getElementById('lobby-screen').classList.contains('hidden')) {
        updateLobby();
    }
});