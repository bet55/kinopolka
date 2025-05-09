import {fillMovieCard} from "./movie/card_filling.js";
import {selectOptionHandler} from "./movie/select_options.js";
import {showRatingNotesHandler} from "./movie/rating_toggler.js";
import {paintBookedMovies} from "./movie/paintBookedMovies.js";
import {Request} from "./utils/request";


// Получаем все фильмы
const baseUrl = document.baseURI.split('/', 3).join('/') + '/movies/';
const url = (document.baseURI.includes('archive')) ? `${baseUrl}archive/` : `${baseUrl}`;
const getMoviesUrl = `${url}?format=json`.replace('#', '');

const allMovies = await Request.send('get', getMoviesUrl);

paintBookedMovies() // меняем иконку у всех фильмов в закладках
showRatingNotesHandler() // отображение оценок
fillMovieCard(allMovies); // отрисовки большого постера
selectOptionHandler(allMovies) // применение опции к фильму

