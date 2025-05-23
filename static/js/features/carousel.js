import {addToCart} from "../based_layout/movies_cart.js";
import {formatTime} from "../utils/format_time.js";
import {Request} from "../utils/request.js";

const carousel = document.querySelector('#carousel');
let posters = document.querySelectorAll('.poster');
const start = document.querySelector('#start button');
const result = document.querySelector('#result');
const resultDuration = document.querySelector('#duration b');
const arrow = document.querySelector('.arrow');

const posterWidth = posters[0].clientWidth;
const borderWidth = Number(getComputedStyle(posters[0]).borderTopWidth.slice(0, -2)) * 2; // слева + справа
const containerWidth = posterWidth + borderWidth;


let offset = posters.length * containerWidth;
let frames = 2; // сколько прокруток до сокрытия постера
let delta = -containerWidth / frames; // на сколько пикселей смещаем постеры

let counter = 0; // сколько было сдвигов на delta
let shiftedIndex = 0; // какой постер стал самым правым
let resultIndex = 0; // какой индекс у выпавшего фильма

// Звуковое сопровождение
const endSound = new Audio("https://freesound.org/data/previews/511/511484_6890478-lq.mp3");
const tickSound = new Audio("https://freesound.org/data/previews/269/269026_5094889-lq.mp3");
tickSound.playbackRate = 4;

// Задержка между крутками
let sleepTime = 500;

// Получаем все фильмы
const allMovies = await Request.get({url:`/movies/?format=json`, showToast: false});

// Вычисляем случайное количество круток
function randomTicksCount(postersCount) {
    const min = postersCount * 0.8;
    const max = postersCount * 2.2;

    const randomInt = Math.floor(Math.random() * (max - min) + min);

    return randomInt;
}

// Блокируем выполнение кода
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
}

// Добавляем выпавший постер в контейнер с результатами
function addWinPoster(movieId, src) {
    const resultPoster = document.createElement('img');
    resultPoster.dataset.kpId = movieId;
    resultPoster.src = src;
    resultPoster.classList.add('win-poster');
    result.appendChild(resultPoster);

    // Обновляем общую длительность всех выпавших фильмов
    const prevDuration = resultDuration.textContent
    if (!prevDuration) {
        resultDuration.textContent = formatTime(allMovies[movieId]['duration']);
    } else {
        let [hours, , mins] = prevDuration.split(' ');
        mins = parseInt(hours) * 60 + parseInt(mins) + allMovies[movieId]['duration'];
        resultDuration.textContent = formatTime(mins);
    }


    // Добавление в корзину
    resultPoster.addEventListener('click', e => {

        // Проверяем, что фильма нет в корзине
        if (!document.querySelector(`#cart li[data-kp-id="${movieId}"]`)) {

            addToCart(movieId, allMovies[movieId]);
        }
    })
}

// Делаем кнопки активными/неактивными
function changeButtonsStatus() {
    let isActive = true;

    function inner() {
        if (isActive) {
            start.disabled = true; // отключаем кнопку
            start.classList.add('disabled');
            arrow.classList.add('shake'); // трясем стрелку

            isActive = false;
        } else {
            arrow.classList.remove('shake');
            start.classList.remove('disabled');
            start.disabled = false;

            isActive = true;
        }
    }

    return inner;
}

const toggleButtons = changeButtonsStatus();


const roll = async () => {

    // Сколько круток будет
    const ticksCount = randomTicksCount(posters.length);


    // Отключаем кнопку старта
    toggleButtons();

    // Прокручиваем фильмы
    for (let i = 0; i < ticksCount; i++) {

        // Динамически изменяем скорость прокрутки
        if (i > ticksCount * 0.8) {
            sleepTime += 30;
        } else {
            sleepTime = (sleepTime < 120) ? sleepTime : sleepTime - (i * 10);
        }

        await sleep(sleepTime);

        // Сдвигаем все постеры
        counter++;
        posters.forEach(p => {
            offset = p.style.transform.replace(/[^\d-]/g, '');
            offset = Number(offset) + delta;
            p.style.transform = `translatex(${offset}px)`
        });

        tickSound.play();


        // Передвигаем крайний правый постер в конец
        if (counter === frames) {
            counter = 0;

            shiftedIndex = (shiftedIndex >= posters.length) ? 0 : shiftedIndex;

            offset = containerWidth * (posters.length - 1) - (containerWidth * shiftedIndex);

            posters[shiftedIndex].style.transform = `translatex(${offset}px)`;

            shiftedIndex++;
        }
    }

    // Вычисляем выпавший постер по положению стрелки
    resultIndex = shiftedIndex - 1 + 4; // физическое расположение стрелки на 4 элементе (можно через тики)
    resultIndex = (resultIndex < posters.length) ? resultIndex : resultIndex - posters.length;
    const winPoster = posters[resultIndex];

    // Добавляем постер в результаты
    addWinPoster(winPoster.dataset.kpId, winPoster.querySelector('img').src);

    // Звук остановки
    endSound.play();

    // Удаляем выпавший фильм из карусели
    winPoster.classList.add('fadeout');
    await sleep(900);
    winPoster.remove();

    // Пересчитываем постеры
    posters = document.querySelectorAll('.poster');

    // Возвращаем постеры в изначальное положение
    posters.forEach(p => p.style.transform = `translatex(0px)`);

    // Обнуляем счетчики
    counter = 0;
    shiftedIndex = 0;
    resultIndex = 0;

    // Возвращаем кнопки в исходное положение
    toggleButtons();

}

// Запускаем рулетку по кнопке
start.addEventListener('click', async e => {
    await roll();
})

