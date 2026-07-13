/* Турнир: панель ставок. Фильмы для селектов берутся из закладок —
   клиентской корзины в localStorage (см. movies_cart.js). */

import {getStorageFilmIds} from "../../based_layout/movies_cart.js";

// Заполняем селекты фильмами из закладок; пустая корзина — селект гасим
function fillMovieSelects() {
    const films = getStorageFilmIds();

    for (const select of document.querySelectorAll('.bet-movie')) {
        if (films.length === 0) {
            select.options[0].textContent = '— закладки пусты —';
            select.disabled = true;
            continue;
        }

        for (const film of films) {
            select.add(new Option(film['name'], film['kp_id']));
        }
    }
}

// Аватарка выбранного болельщика — рядом с именем бойца
function avatarsHandler() {
    for (const select of document.querySelectorAll('.bet-user')) {
        select.addEventListener('change', () => {
            const avatar = select.selectedOptions[0].dataset.avatar;
            const img = select.closest('.bet-slot').querySelector('.bet-avatar');

            img.src = avatar || '';
            img.classList.toggle('hide', !avatar);
        });
    }
}

/* Один болельщик и один фильм — только у одного бойца:
   выбранное значение блокируется в селектах остальных слотов */
function syncSelects(selector) {
    const selects = [...document.querySelectorAll(selector)];

    const update = () => {
        const taken = selects.map(s => s.value).filter(Boolean);
        for (const select of selects) {
            for (const option of select.options) {
                option.disabled = Boolean(option.value)
                    && option.value !== select.value
                    && taken.includes(option.value);
            }
        }
    };

    selects.forEach(select => select.addEventListener('change', update));
}

fillMovieSelects();
avatarsHandler();
syncSelects('.bet-user');
syncSelects('.bet-movie');
