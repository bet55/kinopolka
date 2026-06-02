import {Request} from "../../utils/request.js";
import {getRandomItem} from "../../utils/get_random_item.js";
import {formatTime} from "../../utils/format_time.js";
import {addToCart} from "../../based_layout/movies_cart.js";

const SHAKE_SOUND_URL = "https://freesound.org/data/previews/237/237610_4284968-lq.mp3";
const SHAKE_DURATION_MS = 1400;
const FLIP_DURATION_MS = 800;

class MagicBall {
    constructor(allMovies) {
        this.allMovies = allMovies;
        this.allIds = Object.keys(allMovies);
        this.ballEl = document.querySelector('#ball');
        this.innerEl = this.ballEl.querySelector('.ball-inner');
        this.posterEl = document.querySelector('#ball-poster');
        this.placeholderEl = this.ballEl.querySelector('.ball-placeholder');
        this.shakeBtn = document.querySelector('#shake-btn');
        this.resultEl = document.querySelector('#ball-result');
        this.resultTitle = this.resultEl.querySelector('.result-title');
        this.resultDuration = this.resultEl.querySelector('.result-duration');
        this.addBtn = this.resultEl.querySelector('.add-to-bookmark');

        this.shakeSound = new Audio(SHAKE_SOUND_URL);
        this.isShaking = false;

        this.shakeBtn.addEventListener('click', () => this.shake());
        this.ballEl.addEventListener('click', () => this.shake());
    }

    async shake() {
        if (this.isShaking) return;
        this.isShaking = true;

        this.resultEl.classList.add('hidden');
        this.shakeBtn.disabled = true;

        // если шар уже перевёрнут на «ответ» — сначала возвращаем его к «8»
        if (this.innerEl.classList.contains('flipped')) {
            this.innerEl.classList.remove('flipped');
            this.posterEl.classList.remove('visible');
            await wait(FLIP_DURATION_MS);
        }

        // выбираем фильм заранее
        const winnerId = getRandomItem(this.allIds);
        const winner = this.allMovies[winnerId];

        // трясём шар с «8»
        this.innerEl.classList.add('shaking');
        this.shakeSound.currentTime = 0;
        this.shakeSound.play().catch(() => {});
        await wait(SHAKE_DURATION_MS);
        this.innerEl.classList.remove('shaking');

        // ставим постер на обратную сторону, переворачиваем шар
        this.posterEl.src = winner.poster_local;
        this.posterEl.alt = winner.name;
        this.placeholderEl.classList.add('hidden');
        // постер показываем чуть позже, когда шар повернётся хотя бы наполовину
        setTimeout(() => this.posterEl.classList.add('visible'), FLIP_DURATION_MS / 2);

        this.innerEl.classList.add('flipped');
        await wait(FLIP_DURATION_MS);

        this.showResult(winnerId, winner);

        this.shakeBtn.disabled = false;
        this.shakeBtn.textContent = 'Встряхнуть ещё раз';
        this.isShaking = false;
    }

    showResult(movieId, movie) {
        this.resultTitle.textContent = movie.name;
        this.resultDuration.textContent = formatTime(movie.duration);

        const inCart = !!localStorage.getItem(movieId);
        this.addBtn.classList.toggle('added', inCart);
        this.addBtn.textContent = inCart ? '✓ в закладках' : '+ в закладки';
        this.addBtn.disabled = inCart;

        // пересоздаём кнопку, чтобы не накапливать listener'ы
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

function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const allMovies = await Request.get({url: '/movies/?format=json', showToast: false});

if (allMovies) {
    new MagicBall(allMovies);
}
