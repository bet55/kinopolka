import {Request} from "../../utils/request.js";
import {shuffleArray} from "../../utils/shuffle.js";
import {formatTime} from "../../utils/format_time.js";
import {addToCart} from "../../based_layout/movies_cart.js";

const DRAW_SOUND_URL = "https://freesound.org/data/previews/240/240777_2394245-lq.mp3";

class MovieDeck {
    constructor(allMovies) {
        this.allMovies = allMovies;
        this.allIds = Object.keys(allMovies);
        this.deckEl = document.querySelector('#deck');
        this.drawnEl = document.querySelector('#drawn-cards');
        this.flightLayer = document.querySelector('#flight-layer');
        this.reshuffleBtn = document.querySelector('#reshuffle-btn');
        this.hintEl = document.querySelector('#deck-hint');
        this.counterEl = this.deckEl.querySelector('.deck-counter');
        this.drawSound = new Audio(DRAW_SOUND_URL);

        this.isFlying = false;
        this.resetDeck();

        this.deckEl.addEventListener('click', () => this.drawCard());
        this.reshuffleBtn.addEventListener('click', () => this.resetDeck());
    }

    // Сброс состояния (без анимации) — для первой инициализации и кнопки «Перемешать заново».
    resetDeck() {
        this.deck = shuffleArray(this.allIds);
        this.drawnIndex = 0;
        this.drawnEl.innerHTML = '';
        this.deckEl.classList.remove('empty');
        this.reshuffleBtn.classList.add('hidden');
        this.hintEl.classList.remove('hidden');
        this.updateCounter();
    }

    updateCounter() {
        const remaining = this.deck.length - this.drawnIndex;
        this.counterEl.textContent = remaining > 0 ? `Осталось карт: ${remaining}` : '';
    }

    // Тасуем колоду визуально перед каждым вытягиванием. Сам массив не трогаем.
    playShuffleAnimation() {
        return new Promise(resolve => {
            this.deckEl.classList.add('shuffling');
            // ждём окончание анимации самой «поздней» карты (delay 0.12s + 0.45s)
            const lastCard = this.deckEl.querySelector('.card:nth-child(4)');
            lastCard.addEventListener('animationend', () => {
                this.deckEl.classList.remove('shuffling');
                resolve();
            }, {once: true});
        });
    }

    async drawCard() {
        if (this.isFlying || this.drawnIndex >= this.deck.length) {
            return;
        }
        this.isFlying = true;

        try {
            const movieId = this.deck[this.drawnIndex++];
            const movie = this.allMovies[movieId];

            // 1. Тасовка
            await this.playShuffleAnimation();

            // 2. Создаём placeholder в ряду — уже в перевёрнутом состоянии, но скрытый
            const placeholder = this.createDrawnCard(movieId, movie);
            placeholder.classList.add('invisible', 'flipped');
            this.drawnEl.appendChild(placeholder);

            // 3. Считаем «откуда → куда»
            const deckTop = this.deckEl.querySelector('.deck-top');
            const fromRect = deckTop.getBoundingClientRect();
            const toRect = placeholder.getBoundingClientRect();

            // 4. Создаём летящий клон в позиции колоды
            const flying = this.createFlyingCard(movie);
            flying.style.left = `${fromRect.left}px`;
            flying.style.top = `${fromRect.top}px`;
            flying.style.width = `${fromRect.width}px`;
            flying.style.height = `${fromRect.height}px`;
            this.flightLayer.appendChild(flying);

            // 5. Форсируем reflow: без этого браузер «склеивает» append и смену transform
            //    в один paint, transition не запускается и карта телепортируется.
            void flying.offsetHeight;

            this.drawSound.currentTime = 0;
            this.drawSound.play().catch(() => {});

            // 6. Запускаем полёт + переворот
            const dx = toRect.left - fromRect.left;
            const dy = toRect.top - fromRect.top;
            const flyingInner = flying.querySelector('.card-inner');

            flying.style.transform = `translate(${dx}px, ${dy}px)`;
            flyingInner.classList.add('flipped');

            // 7. Ждём окончание transform с защитой от пропавшего transitionend
            await new Promise(resolve => {
                let done = false;
                const finish = () => {
                    if (done) return;
                    done = true;
                    resolve();
                };
                flying.addEventListener('transitionend', function handler(e) {
                    if (e.propertyName !== 'transform' || e.target !== flying) return;
                    flying.removeEventListener('transitionend', handler);
                    finish();
                });
                // safety — на случай если transition не запустится
                setTimeout(finish, 1000);
            });

            // 8. Прибрать: убрать клон, показать placeholder
            flying.remove();
            placeholder.classList.remove('invisible');

            // 9. Обновить состояние колоды
            this.updateCounter();
            if (this.drawnIndex >= this.deck.length) {
                this.deckEl.classList.add('empty');
                this.reshuffleBtn.classList.remove('hidden');
                this.hintEl.classList.add('hidden');
            }
        } finally {
            this.isFlying = false;
        }
    }

    createDrawnCard(movieId, movie) {
        const inCart = !!localStorage.getItem(movieId);
        const card = document.createElement('li');
        card.className = 'drawn-card';
        card.dataset.kpId = movieId;
        card.innerHTML = `
            <div class="card-inner">
                <div class="card-face card-back"></div>
                <div class="card-face card-front">
                    <img class="card-poster" src="${movie.poster_local}" alt="${movie.name}">
                    <div class="card-info">
                        <span class="card-title">${movie.name}</span>
                        <span class="card-duration">${formatTime(movie.duration)}</span>
                    </div>
                    <button class="add-to-bookmark ${inCart ? 'added' : ''}" ${inCart ? 'disabled' : ''}>
                        ${inCart ? '✓ в закладках' : '+ в закладки'}
                    </button>
                </div>
            </div>
        `;
        const addBtn = card.querySelector('.add-to-bookmark');
        addBtn.addEventListener('click', () => {
            if (addBtn.classList.contains('added')) return;
            addToCart(movieId, movie);
            addBtn.classList.add('added');
            addBtn.textContent = '✓ в закладках';
            addBtn.disabled = true;
        });
        return card;
    }

    createFlyingCard(movie) {
        const card = document.createElement('div');
        card.className = 'flying-card';
        card.innerHTML = `
            <div class="card-inner">
                <div class="card-face card-back"></div>
                <div class="card-face card-front">
                    <img src="${movie.poster_local}" alt="${movie.name}">
                </div>
            </div>
        `;
        return card;
    }
}

const allMovies = await Request.get({url: '/movies/?format=json', showToast: false});

if (allMovies) {
    new MovieDeck(allMovies);
}
