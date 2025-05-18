import {rateMovie} from "./options/rate.js";
import {removeMovie} from "./options/remove.js";
import {addMovieToBookmark} from "./options/book.js";
import {changeMovieArchiveStatus} from "./options/archive.js";


// Словарь - название опции: функция навешивания слушателя
const optionsListenerMap = {
    'opt-rate': rateMovie,
    'opt-booked': addMovieToBookmark,
    'opt-archive': changeMovieArchiveStatus,
    'opt-remove': removeMovie
}

// При нажатии на кнопку под постером фильма выбирается нужная функция
export function selectOptionHandler(allMovies) {

    const moviesOptions = document.querySelectorAll('.opt');

    moviesOptions.forEach(opt => {

        const posterContainer = opt.parentElement.parentElement;
        const movieId = posterContainer.dataset.kpId;

        const optionName = opt.classList[1];
        const optionFunction = optionsListenerMap[optionName];

        optionFunction(allMovies, movieId, opt, posterContainer);

    })

}

