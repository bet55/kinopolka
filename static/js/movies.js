import {fillMovieCard} from "./movie/card_filling.js";
import {selectOptionHandler} from "./movie/select_options.js";
import {showRatingNotesHandler} from "./movie/rating_toggler.js";
import {paintBookedMovies} from "./movie/paintBookedMovies.js";
import {Request} from "./utils/request.js";


// Получаем все фильмы
const url = window.location.pathname;
const getMoviesUrl = `${url}?format=json`;

const allMovies = await Request.send({method: 'get', url: getMoviesUrl, showToast: false});

paintBookedMovies() // меняем иконку у всех фильмов в закладках
showRatingNotesHandler() // отображение оценок
fillMovieCard(allMovies); // отрисовки большого постера
selectOptionHandler(allMovies) // применение опции к фильму

