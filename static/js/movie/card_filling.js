import {formatTime} from "../utils/format_time.js";

const moviePosters = document.querySelector('.posters-grid')

const cardImg = document.querySelector('.card-img');
const cardTitle = document.querySelector('.card-title');
const cardDescription = document.querySelector('.card-description');
const cardRealiseDate = document.querySelector('.card-realise');
const cardDuration = document.querySelector('.card-duration');
const cardRating = document.querySelector('.card-rating');
const cardKpLink = document.querySelector('#kp-rating');
const cardImdbLink = document.querySelector('#imdb-rating')

// Отображение большого постера с описанием в правой части страницы
const showMoviePoster = (movieInfo) => {

    const smallPoster = document.querySelector(`.poster-img[data-kp-id="${movieInfo.kp_id}"]`);

    cardImg.src = smallPoster.src;
    cardImg.style.visibility = 'visible';
    cardTitle.textContent = movieInfo.name;
    cardDescription.textContent = movieInfo.description;
    cardRealiseDate.textContent = movieInfo.premiere;
    cardDuration.textContent = formatTime(movieInfo.duration);
    cardKpLink.href = `https://www.kinopoisk.ru/film/${movieInfo.kp_id}/`;
    cardImdbLink.href = 'https://cataas.com/cat/gif';

    cardKpLink.querySelector('span').textContent = Number(parseFloat(movieInfo.rating_kp).toFixed(1));
    cardImdbLink.querySelector('span').textContent = Number(parseFloat(movieInfo.rating_imdb).toFixed(1));


    cardRating.classList.remove('hidden');

    // случайные картинки по ссылке
    // https://cataas.com/cat/gif
    // https://www.thiswaifudoesnotexist.net/
    // https://placebear.com/800/600
    // https://place.dog/800/600
    // https://random-d.uk/api/322.jpg
    // https://loremflickr.com
    // https://picsum.photos/1280/720
    // https://loremflickr.com/800/600/cat,dog

}

export function fillMovieCard(allMovies) {

    // Возможность раскрывать/прятать текст описания
    cardDescription.addEventListener('click', e => {

        if (cardDescription.classList.contains('card-description-hidden')) {
            cardDescription.classList.remove('card-description-hidden');
        } else {
            cardDescription.classList.add('card-description-hidden');
        }

    })

    moviePosters.addEventListener('click', async (event) => {
        const target = event.target;
        const classList = target.classList;

        // Проверяем, что нажали на постер или один из перекрывающих элементов
        const isPosterClicked =
            classList.contains('poster-container') ||
            classList.contains('poster-img') ||
            classList.contains('note-container');

        if (isPosterClicked) {
            const movieId = target.dataset.kpId;
            const movieInfo = allMovies[movieId];
            showMoviePoster(movieInfo);
        }

    })

}