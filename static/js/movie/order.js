import {createToast} from "../utils/create_toast.js";
import {getCookie} from "../utils/cookie.js";

// Отображение списка с сортировками по нажатии на иконку
function showOrder() {
    const order = document.querySelector('#order img');
    const orderOptions = document.querySelector('#order ul');

    // Нажатие на опцию не должно закрывать список
    orderOptions.addEventListener('click', (e) => {
        e.stopPropagation();
    })

    // Видимость списка по нажатию
    orderOptions.style.visibility = 'hidden' // Бредик полнейший (без этого хака нет свойства у объекта до нажатия)
    order.addEventListener('click', (event) => {

        const visibility = (orderOptions.style.visibility === 'hidden') ? 'visible' : 'hidden';
        orderOptions.style.visibility = visibility;
    })
}

// Словарь с функциями сортировки
function makeOrdersFunctions(movies) {
    const name = (a, b) => a.name.localeCompare(b.name);
    const rating_user = (a, b) => parseFloat(b.rating_user) - parseFloat(a.rating_user);
    const rating_kp = (a, b) => parseFloat(b.rating_kp) - parseFloat(a.rating_kp);
    const rating_imdb = (a, b) => parseFloat(b.rating_imdb) - parseFloat(a.rating_imdb);
    const premiere = (a, b) => new Date(a.premiere.split('/').reverse().join('-')) - new Date(b.premiere.split('/').reverse().join('-'));
    const duration = (a, b) => a.duration - b.duration;


    return {
        name: () => movies.toSorted(name),
        rating_user: () => movies.toSorted(rating_user),
        rating_kp: () => movies.toSorted(rating_kp),
        rating_imdb: () => movies.toSorted(rating_imdb),
        premiere: () => movies.toSorted(premiere),
        duration: () => movies.toSorted(duration)
    }
}

function makeMoviesArray(movies) {
    const currentUser = getCookie('user');

    // Если не выбран пользователь или мы не в архиве - убираем метод сортировки по оценкам
    if(!window.location.href.includes('archive') || !currentUser) {
        document.querySelector('li[data-order="rating-user"]').remove();
        return Object.values(movies);
    }

    // Добавим информацию об оценках пользователя
    const rateNotesContainers = document.querySelectorAll('.note-container');
    rateNotesContainers.forEach(notesContainer => {
        const movieId = notesContainer.dataset.kpId;
        const ratingElement = notesContainer.querySelector(`.note[data-user-id="${currentUser}"] h2`);
        const userRating =  ratingElement?.textContent ?? 0;
        movies[movieId]['rating_user'] = parseInt(userRating);
    })

    return Object.values(movies);
}

// Сортируем постеры
function orderMovies(allMovies) {
    const movies = makeMoviesArray(allMovies);
    const ordersFunctions = makeOrdersFunctions(movies);

    const postersElements = document.querySelectorAll('.poster-container');
    const ordersOptions = document.querySelectorAll('#order-list li');

    console.log(ordersFunctions['rating_user']())

    ordersOptions.forEach(option => {

        option.addEventListener('click', e => {

            const orderName = option.dataset.order.replace('-', '_');
            if (!(orderName in ordersFunctions)) {
                return null;
            }

            const sortedMovies = ordersFunctions[orderName]();
            const sortedMoviesMap = sortedMovies.reduce((acc, movie, index) => {
                acc[movie.kp_id] = index + 1; // +1 если нужна нумерация с 1 вместо 0
                return acc;
            }, {});

            postersElements.forEach(poster => {
                const posterOrder = sortedMoviesMap[poster.dataset.kpId];
                poster.style.order = posterOrder;
            })


        })
    })

}

export {showOrder, orderMovies}