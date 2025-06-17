import {fillMovieCard} from "./movie/card_filling.js";
import {selectOptionHandler} from "./movie/select_options.js";
import {showRatingNotesHandler} from "./movie/rating_toggler.js";
import {paintBookedMovies} from "./movie/paint_booked_movies.js";
import {showFilter, filterMovies} from "./movie/filter.js";
import {showOrder, orderMovies} from "./movie/order.js";
import {posterLoadingPlaceholder} from "./movie/poster_placeholder.js";
import {Request} from "./utils/request.js";

posterLoadingPlaceholder(); // заглушка на постеры до загрузки

// Получаем все фильмы
const url = window.location.pathname + '?format=json';
const allMovies = await Request.get({url: url, showToast: false});

paintBookedMovies(); // меняем иконку у всех фильмов в закладках
showRatingNotesHandler(); // отображение оценок
fillMovieCard(allMovies); // отрисовки большого постера
selectOptionHandler(allMovies); // применение опции к фильму

showOrder(); // отображение сортировки
orderMovies(allMovies); // упорядочиваем отображаемые постеры

showFilter(); // отображение фильтра по жанрам
filterMovies(allMovies); // фильтруем отображаемые постеры
