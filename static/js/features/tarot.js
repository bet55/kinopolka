// Конфигурация
const TAROT_CONFIG = {
    cardNames: [
        'fool', 'magician', 'high-priestess', 'empress', 'emperor',
        'hierophant', 'lovers', 'chariot', 'strength', 'hermit',
        'wheel-of-fortune', 'justice', 'hanged-man', 'death', 'temperance',
        'devil', 'tower', 'star', 'moon', 'sun', 'judgement', 'world'
    ],
    minStarDistance: 5, // Минимальное расстояние между звёздами (%)
    starCount: 15,      // Количество звёзд
    maxPlacementAttempts: 100, // Макс. попыток размещения звезды
    flipDelay: 100,     // Задержка перед переворотом карты (мс)
    reversedChance: 0.5, // Вероятность перевёрнутой карты (50%)
};

// Описания карт (можно вынести в отдельный JSON-файл)
const CARD_DESCRIPTIONS = {
    'fool': {
        title: 'Шут',
        description: 'Символизирует новые начинания, спонтанность, безрассудство, свободный дух и веру в себя. Эта карта говорит о том, что пришло время для новых приключений и возможностей.'
    },
    'magician': {
        title: 'Маг',
        description: 'Представляет проявление, силу воли, мастерство и уверенность. Маг напоминает, что у вас есть все необходимые инструменты для достижения ваших целей.'
    },
    'high-priestess': {
        title: 'Верховная Жрица',
        description: 'Символизирует интуицию, тайные знания, внутреннюю мудрость и духовное просветление. Призывает прислушаться к своему внутреннему голосу.'
    },
    'empress': {
        title: 'Императрица',
        description: 'Олицетворяет изобилие, творчество, плодородие и материнскую заботу. Говорит о периоде роста и процветания.'
    },
    'emperor': {
        title: 'Император',
        description: 'Символ власти, авторитета, структуры и стабильности. Представляет мужское начало, лидерство и порядок.'
    },
    'hierophant': {
        title: 'Иерофант',
        description: 'Представляет традиции, духовное руководство, образование и конформизм. Указывает на необходимость следовать проверенным путём.'
    },
    'lovers': {
        title: 'Влюблённые',
        description: 'Символизируют любовь, гармонию, отношения и выбор. Карта говорит о важных решениях в жизни и необходимости следовать зову сердца.'
    },
    'chariot': {
        title: 'Колесница',
        description: 'Означает движение вперёд, победу, силу воли и решительность. Говорит о необходимости взять контроль над ситуацией.'
    },
    'strength': {
        title: 'Сила',
        description: 'Символизирует внутреннюю силу, мужество, терпение и мягкую власть. Напоминает о важности самоконтроля и настойчивости.'
    },
    'hermit': {
        title: 'Отшельник',
        description: 'Представляет самоанализ, внутренний поиск, мудрость и одиночество. Призывает к размышлениям и поиску истины.'
    },
    'wheel-of-fortune': {
        title: 'Колесо Фортуны',
        description: 'Символизирует судьбу, циклы жизни, удачу и перемены. Напоминает о постоянном движении жизни и неизбежности перемен.'
    },
    'justice': {
        title: 'Справедливость',
        description: 'Означает равновесие, честность, истину и последствия. Говорит о важности объективности и принятия ответственных решений.'
    },
    'hanged-man': {
        title: 'Повешенный',
        description: 'Символизирует жертвенность, новый взгляд на вещи и принятие. Призывает посмотреть на ситуацию с другой стороны.'
    },
    'death': {
        title: 'Смерть',
        description: 'Представляет трансформацию, окончание чего-либо и новые начинания. Говорит о необходимых переменах и обновлении.'
    },
    'temperance': {
        title: 'Умеренность',
        description: 'Символизирует баланс, гармонию, терпение и умеренность. Призывает найти золотую середину во всём.'
    },
    'devil': {
        title: 'Дьявол',
        description: 'Означает материализм, зависимость, искушение и ограничения. Предупреждает о необходимости осознать свои страхи и освободиться от них.'
    },
    'tower': {
        title: 'Башня',
        description: 'Символизирует внезапные изменения, разрушение старого и освобождение. Говорит о неизбежных переменах и необходимости принять их.'
    },
    'star': {
        title: 'Звезда',
        description: 'Представляет надежду, вдохновение, духовное руководство и обновление. Несёт послание надежды и веры в будущее.'
    },
    'moon': {
        title: 'Луна',
        description: 'Символизирует интуицию, иллюзии, страхи и подсознательное. Призывает доверять своим инстинктам и не бояться неизвестного.'
    },
    'sun': {
        title: 'Солнце',
        description: 'Означает радость, успех, позитив и жизненную энергию. Несёт свет и тепло в жизнь, обещает счастливые времена.'
    },
    'judgement': {
        title: 'Суд',
        description: 'Представляет возрождение, внутренний зов, искупление и пробуждение. Говорит о важных жизненных переменах и новом этапе.'
    },
    'world': {
        title: 'Мир',
        description: 'Символизирует завершение, достижение целей, путешествия и гармонию. Означает успешное завершение важного жизненного этапа.'
    }
};

// ==================== ЗВЁЗДЫ ====================
function initStars() {
    const stars = [];
    const body = document.body;

    // Проверка, можно ли разместить звезду без наложений
    const isPositionValid = (x, y, stars, minDist) => {
        return stars.every(star => {
            const distance = Math.sqrt((x - star.x) ** 2 + (y - star.y) ** 2);
            return distance >= minDist;
        });
    };

    // Создание звёзд
    for (let i = 0; i < TAROT_CONFIG.starCount; i++) {
        let x, y, attempts = 0;

        do {
            x = Math.random() * 95 + 2.5; // 2.5-97.5% (чтобы не прилипали к краям)
            y = Math.random() * 95 + 2.5;
            attempts++;
            if (attempts >= TAROT_CONFIG.maxPlacementAttempts) break;
        } while (!isPositionValid(x, y, stars, TAROT_CONFIG.minStarDistance));

        if (attempts < TAROT_CONFIG.maxPlacementAttempts) {
            const star = document.createElement('div');
            star.className = 'star';
            star.style.cssText = `
                left: ${x}vw;
                top: ${y}vh;
                width: ${Math.random() * 2 + 1}px;
                height: ${Math.random() * 2 + 1}px;
                animation-delay: ${Math.random() * 2}s;
            `;
            body.appendChild(star);
            stars.push({ x, y });
        }
    }
}

// Функция для перемешивания массива (Fisher-Yates shuffle)
function shuffleArray(array) {
    const newArray = [...array];
    for (let i = newArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
    }
    return newArray;
}

// ==================== КАРТЫ ====================
class TarotDeck {
    constructor() {
        this.shuffledDeck = shuffleArray(TAROT_CONFIG.cardNames);
        this.currentCardIndex = 0;
        this.deckElement = document.querySelector('.deck-card');
        this.readingArea = document.getElementById('readingArea');
        this.openCardsList = document.querySelector('#open-cards-list');
        this.modal = new ModalController();
        this.initDeck();
    }

    initDeck() {
        this.deckElement.addEventListener('click', () => this.drawCard());
    }

    drawCard() {
        if (this.currentCardIndex >= this.shuffledDeck.length) {
            alert('Все карты уже вытянуты!');
            return;
        }

        const cardName = this.shuffledDeck[this.currentCardIndex];
        const isReversed = Math.random() <= TAROT_CONFIG.reversedChance;
        this.createCardElement(cardName, isReversed);
        this.addCardToList(cardName, isReversed);
        this.currentCardIndex++;
    }

    createCardElement(cardName, isReversed) {
        const cardElement = document.createElement('div');
        cardElement.className = 'tarot-card';

        const frontClass = isReversed ? 'card-front-spin' : 'card-front';

        cardElement.innerHTML = `
            <div class="card-face card-back"></div>
            <div class="card-face ${frontClass}" 
                 style="background-image: url('/static/img/tarots/${cardName}.png')"></div>
        `;

        cardElement.querySelector(`.${frontClass}`).addEventListener('click', () => {
            this.modal.show(cardName, isReversed);
        });

        this.readingArea.appendChild(cardElement);

        setTimeout(() => {
            if (cardName === 'world') this.playSound("/static/sound/za_warudo.mp3");
            cardElement.classList.add('flipped');
        }, TAROT_CONFIG.flipDelay);
    }

    addCardToList(cardName, isReversed) {
        const cardItem = document.createElement('li');
        const cardSpan = document.createElement('span');
        cardSpan.textContent = CARD_DESCRIPTIONS[cardName].title;
        cardSpan.classList.add('card-name');
        cardItem.appendChild(cardSpan);

        if (isReversed) {
            const reversedSpan = document.createElement('span');
            reversedSpan.textContent = ' (перевёрнута)';
            reversedSpan.classList.add('card-reversed');
            cardItem.appendChild(reversedSpan);
        }

        this.openCardsList.appendChild(cardItem);
    }

    playSound(url) {
        new Audio(url).play().catch(e => console.error("Ошибка воспроизведения звука:", e));
    }
}

// ==================== МОДАЛЬНОЕ ОКНО ====================
class ModalController {
    constructor() {
        this.modal = document.getElementById('cardModal');
        this.modalImage = document.getElementById('modalCardImage');
        this.modalTitle = document.getElementById('modalCardTitle');
        this.modalDescription = document.getElementById('modalCardDescription');
        this.initModal();
    }

    initModal() {
        document.querySelector('.close-button').onclick = () => this.hide();
        window.addEventListener('click', (e) => e.target === this.modal && this.hide());
    }

    show(cardName, isReversed) {
        const card = CARD_DESCRIPTIONS[cardName];
        this.modalImage.src = `/static/img/tarots/${cardName}.png`;
        this.modalTitle.textContent = isReversed ? `${card.title} (перевёрнута)` : card.title;
        this.modalDescription.textContent = card.description;
        this.modal.style.display = 'block';
    }

    hide() {
        this.modal.style.display = 'none';
    }
}

// ==================== ПРЕДЗАГРУЗКА ИЗОБРАЖЕНИЙ ====================
function preloadImages(deck) {
    deck.forEach(card => {
        const img = new Image();
        img.src = `/static/img/tarots/${card}.png`;
    });
}

// ==================== ЗАПУСК ПРИЛОЖЕНИЯ ====================
document.addEventListener('DOMContentLoaded', () => {
    const deck = new TarotDeck();
    preloadImages(deck.shuffledDeck);
    initStars();
});