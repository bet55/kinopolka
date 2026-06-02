import {Request} from "../../utils/request.js";
import {getRandomItem} from "../../utils/get_random_item.js";
import {formatTime} from "../../utils/format_time.js";
import {addToCart} from "../../based_layout/movies_cart.js";

// Количество постеров в ленте перед победителем — определяет драматизм прокрутки.
const STRIP_LEN = 30;
// Победитель ставится на эту позицию (с запасом от края, чтобы остановка выглядела «честной»).
const WINNER_POS = STRIP_LEN - 3;

// Длительности прокрутки трёх барабанов (сек). Последовательная остановка → драматизм.
const DURATIONS = [5.8, 6.6, 7.5];

const LEVER_SOUND_URL         = "/static/sound/lever.mp3";
const WIN_SOUND_URL           = "/static/sound/small-win.wav";
const CASH_REGISTER_SOUND_URL = "/static/sound/cash-machine2.mp3";

class SlotMachine {
    constructor(allMovies) {
        this.allMovies = allMovies;
        this.allIds = Object.keys(allMovies);
        this.reels = document.querySelectorAll('.reel');
        this.leverBtn = document.querySelector('#lever-btn');
        this.resultEl = document.querySelector('#slot-result');
        this.resultTitle = this.resultEl.querySelector('.result-title');
        this.resultDuration = this.resultEl.querySelector('.result-duration');
        this.addBtn = this.resultEl.querySelector('.add-to-bookmark');

        this.cashRegisterSound = new Audio(CASH_REGISTER_SOUND_URL);
        this.leverSound = new Audio(LEVER_SOUND_URL);
        this.winSound = new Audio(WIN_SOUND_URL);
        this.winSound.volume = 0.8;

        this.isSpinning = false;

        // Заполняем барабаны начальной лентой, чтобы при первой загрузке было что показать.
        this.reels.forEach(reel => this.fillStrip(reel.querySelector('.reel-strip'), null));

        this.leverBtn.addEventListener('click', () => this.pull());
    }

    fillStrip(strip, winnerId) {
        let html = '';
        for (let i = 0; i < STRIP_LEN; i++) {
            const id = (winnerId !== null && i === WINNER_POS)
                ? winnerId
                : getRandomItem(this.allIds);
            const movie = this.allMovies[id];
            html += `<img src="${movie.poster_local}" alt="" data-kp-id="${id}">`;
        }
        strip.innerHTML = html;
    }

    spinReel(reel, durationSec) {
        return new Promise(resolve => {
            const strip = reel.querySelector('.reel-strip');

            // сброс позиции мгновенно
            strip.style.transition = 'none';
            strip.style.transform = 'translateY(0px)';
            // принудительный reflow, чтобы браузер не «склеил» изменения
            void strip.offsetHeight;

            // меряем фактическую высоту картинки в ленте — это то, что реально прокручиваем
            const posterH = strip.children[0]?.offsetHeight || reel.clientHeight;
            const targetY = -WINNER_POS * posterH;
            strip.style.transition = `transform ${durationSec}s cubic-bezier(0.15, 0.4, 0.1, 1)`;
            strip.style.transform = `translateY(${targetY}px)`;

            const onEnd = () => {
                strip.removeEventListener('transitionend', onEnd);
                resolve();
            };
            strip.addEventListener('transitionend', onEnd);
        });
    }

    async pull() {
        if (this.isSpinning) return;
        this.isSpinning = true;

        this.resultEl.classList.add('hidden');
        this.leverBtn.classList.add('pulled');
        this.leverBtn.disabled = true;

        // Звук кассы при нажатии — ждём его окончания
        this.cashRegisterSound.currentTime = 0;
        await new Promise(resolve => {
            this.cashRegisterSound.addEventListener('ended', resolve, {once: true});
            this.cashRegisterSound.play().catch(() => resolve());
        });

        // Только после кассы запускаем звук рычага и начинаем прокрутку
        this.leverSound.currentTime = 0;
        this.leverSound.play().catch(() => {});

        const winnerId = getRandomItem(this.allIds);
        const winner = this.allMovies[winnerId];

        const promises = [];
        this.reels.forEach((reel, i) => {
            this.fillStrip(reel.querySelector('.reel-strip'), winnerId);
            promises.push(this.spinReel(reel, DURATIONS[i]));
        });

        await Promise.all(promises);

        this.winSound.currentTime = 0;
        this.winSound.play().catch(() => {});

        this.leverBtn.classList.remove('pulled');
        this.leverBtn.disabled = false;

        this.showResult(winnerId, winner);
        this.isSpinning = false;
    }

    showResult(movieId, movie) {
        this.resultTitle.textContent = movie.name;
        this.resultDuration.textContent = formatTime(movie.duration);

        const inCart = !!localStorage.getItem(movieId);
        this.addBtn.classList.toggle('added', inCart);
        this.addBtn.textContent = inCart ? '✓ в закладках' : '+ в закладки';
        this.addBtn.disabled = inCart;

        // пересоздаём обработчик, чтобы не накапливать listener'ы между прокрутками
        const newBtn = this.addBtn.cloneNode(true);
        this.addBtn.replaceWith(newBtn);
        this.addBtn = newBtn;
        this.addBtn.addEventListener('click', () => {
            if (this.addBtn.classList.contains('added')) return;
            addToCart(movieId, movie);
            this.addBtn.classList.add('added');
            this.addBtn.textContent = '✓ в закладках';
            this.addBtn.disabled = true;
        });

        this.resultEl.classList.remove('hidden');
    }
}

const allMovies = await Request.get({url: '/movies/?format=json', showToast: false});

if (allMovies) {
    new SlotMachine(allMovies);
}
