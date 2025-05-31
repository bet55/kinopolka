function starsAnimation() {
    document.addEventListener('DOMContentLoaded', () => {
        const body = document.body;
        const existingStars = [];
        const minDistance = 5; // Минимальное расстояние между звёздами (в %)

        // Функция проверки, не перекрывает ли новая звезда существующие
        function isPositionValid(x, y, stars, minDist) {
            for (const star of stars) {
                const distance = Math.sqrt((x - star.x) ** 2 + (y - star.y) ** 2);
                if (distance < minDist) return false;
            }
            return true;
        }

        // Создаём 15 новых звёзд
        for (let i = 0; i < 15; i++) {
            let x, y;
            let attempts = 0;
            const maxAttempts = 100; // Чтобы избежать бесконечного цикла

            // Ищем свободное место для звезды
            do {
                x = Math.random() * 95 + 2.5; // 2.5-97.5% (чтобы не прилипали к краям)
                y = Math.random() * 95 + 2.5;
                attempts++;
                if (attempts >= maxAttempts) break; // На всякий случай
            } while (!isPositionValid(x, y, existingStars, minDistance));

            // Если место нашлось — создаём звезду
            if (attempts < maxAttempts) {
                const star = document.createElement('div');
                star.className = 'star';

                // Размер (1-3px)
                const size = Math.random() * 2 + 1;

                star.style.left = `${x}vw`;
                star.style.top = `${y}vh`;
                star.style.width = `${size}px`;
                star.style.height = `${size}px`;
                star.style.animationDelay = `${Math.random() * 2}s`;

                body.appendChild(star);
                existingStars.push({x, y});
            }
        }
    });
}

const cardDescriptions = {
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

function cardsAnimation() {
    const cards = [
        'fool', 'magician', 'high-priestess', 'empress', 'emperor',
        'hierophant', 'lovers', 'chariot', 'strength', 'hermit',
        'wheel-of-fortune', 'justice', 'hanged-man', 'death', 'temperance',
        'devil', 'tower', 'star', 'moon', 'sun', 'judgement', 'world'
    ];

    const deck = document.getElementById('deck');
    const readingArea = document.getElementById('readingArea');
    const modal = document.getElementById('cardModal');
    const modalImage = document.getElementById('modalCardImage');
    const modalTitle = document.getElementById('modalCardTitle');
    const modalDescription = document.getElementById('modalCardDescription');
    const closeButton = document.querySelector('.close-button');
    let drawnCards = [];

    // Закрытие модального окна
    closeButton.onclick = () => {
        modal.style.display = 'none';
    };

    // Закрытие модального окна при клике вне его
    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };

    deck.addEventListener('click', () => {
        if (drawnCards.length >= cards.length) {
            alert('Все карты уже вытянуты!');
            return;
        }

        let randomCard;
        do {
            randomCard = cards[Math.floor(Math.random() * cards.length)];
        } while (drawnCards.includes(randomCard));

        drawnCards.push(randomCard);

        const cardElement = document.createElement('div');
        cardElement.className = 'tarot-card';

        const cardBack = document.createElement('div');
        cardBack.className = 'card-face card-back';

        const cardFront = document.createElement('div');
        cardFront.className = 'card-face card-front';
        cardFront.style.backgroundImage = `url('/static/img/tarots/${randomCard}.png')`;

        // Добавляем обработчик клика для открытия модального окна
        cardFront.addEventListener('click', () => {
            modalImage.src = `/static/img/tarots/${randomCard}.png`;
            modalTitle.textContent = cardDescriptions[randomCard].title;
            modalDescription.textContent = cardDescriptions[randomCard].description;
            modal.style.display = 'block';
        });

        cardElement.appendChild(cardBack);
        cardElement.appendChild(cardFront);
        readingArea.appendChild(cardElement);

        // Добавляем небольшую задержку перед переворотом для лучшего визуального эффекта
        setTimeout(() => {
            cardElement.classList.add('flipped');
        }, 100);
    });
}

starsAnimation();
cardsAnimation();