import {getCookie} from "../utils/cookie.js";

// Отображение списка с сортировками по нажатии на иконку
function toggleSortList() {
    const sorting = document.querySelector('#sorting img');
    const sortingOptions = document.querySelector('#sorting-list');

    // Нажатие на опцию не должно закрывать список
    sortingOptions.addEventListener('click', (e) => {
        e.stopPropagation();
    })

    // Видимость списка по нажатию
    sortingOptions.style.visibility = 'hidden' // Бредик полнейший (без этого хака нет свойства у объекта до нажатия)
    sorting.addEventListener('click', (event) => {

        const visibility = (sortingOptions.style.visibility === 'hidden') ? 'visible' : 'hidden';
        sortingOptions.style.visibility = visibility;
    })

}

// Изменение иконки сортировки по убыванию/возрастанию
function toggleAscending() {
    const arrowsImages = document.querySelectorAll('#sorting-list img');

    arrowsImages.forEach(arrow => {
        arrow.addEventListener('click', e => {

            e.stopPropagation();

            const changedClasses = arrow.classList.contains('asc') ? ['asc', 'desc'] : ['desc', 'asc'];
            arrow.classList.replace(changedClasses[0], changedClasses[1]);

        })


    })
}


// Словарь с функциями сортировки
function makeSortFunctions(movies) {
    const name = (a, b) => a.name.localeCompare(b.name);
    const rating_user = (a, b) => parseFloat(b.rating_user) - parseFloat(a.rating_user);
    const rating_kp = (a, b) => parseFloat(b.rating_kp) - parseFloat(a.rating_kp);
    const rating_imdb = (a, b) => parseFloat(b.rating_imdb) - parseFloat(a.rating_imdb);
    const premiere = (a, b) => new Date(b.premiere.split('/').reverse().join('-')) - new Date(a.premiere.split('/').reverse().join('-'));
    const duration = (a, b) => b.duration - a.duration;


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
    if (!window.location.href.includes('archive') || !currentUser) {
        document.querySelector('li[data-sorting="rating-user"]').remove();
        return Object.values(movies);
    }

    // Добавим информацию об оценках пользователя
    const rateNotesContainers = document.querySelectorAll('.note-container');
    rateNotesContainers.forEach(notesContainer => {
        const movieId = notesContainer.dataset.kpId;
        const ratingElement = notesContainer.querySelector(`.note[data-user-id="${currentUser}"] h2`);
        const userRating = ratingElement?.textContent ?? 0;
        movies[movieId]['rating_user'] = parseInt(userRating);
    })

    return Object.values(movies);
}

// Сортируем постеры
function handeSortChoice(allMovies) {
    const movies = makeMoviesArray(allMovies);
    const sortFunctions = makeSortFunctions(movies);

    const postersElements = document.querySelectorAll('.poster-container');
    const sortingTypes = document.querySelectorAll('#sorting-list li');

    sortingTypes.forEach(sorting => {

        sorting.addEventListener('click', e => {

            // Вычисляем текущий тип сортировки
            const orderName = sorting.dataset.sorting.replace('-', '_');
            const isAscending = sorting.querySelector('img').classList.contains('asc');
            if (!(orderName in sortFunctions)) {
                return null;
            }

            // Отображаем сортировку как активную
            sortingTypes.forEach(s => s.classList.remove('active'))
            sorting.classList.add('active');

            // Сортируем фильмы
            let sortedMovies = sortFunctions[orderName]();
            sortedMovies = isAscending ? sortedMovies.reverse() : sortedMovies;

            const sortedMoviesMap = sortedMovies.reduce((acc, movie, index) => {
                acc[movie.kp_id] = index + 1;
                return acc;
            }, {});

            // Указываем порядок постера
            postersElements.forEach(poster => poster.style.order = sortedMoviesMap[poster.dataset.kpId]);


        })
    })

}

function sortMovies(allMovies) {
    toggleSortList(); // показываем список сортировок
    toggleAscending(); // меняем направление сортировки
    handeSortChoice(allMovies); // применяем выбранную сортировку
}

export {sortMovies}