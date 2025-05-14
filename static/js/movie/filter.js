import {createToast} from "../utils/create_toast.js";


// Отображаем список с жанрами фильмов
function showFilter() {

    const filter = document.querySelector('#filter img');
    const filterOptions = document.querySelector('#filter ul');

    // Нажатие на опцию не должно закрывать список
    filterOptions.addEventListener('click', (e) => {
        e.stopPropagation();
    })

    // Видимость списка по нажатию
    filterOptions.style.visibility = 'hidden' // Бредик полнейший (без этого хака нет свойства у объекта до нажатия)
    filter.addEventListener('click', (event) => {

        const visibility = (filterOptions.style.visibility === 'hidden') ? 'visible' : 'hidden';

        if (!Boolean(filterOptions.querySelector('li'))) {
            createToast('Фильтр пуст!', 'info');
        }

        filterOptions.style.visibility = visibility;
    })

}

// Делаем словарик - жанр:[список фильмов]
function mapGenresToMovies(movies) {
    let genresMap = {};
    for (const movieId in movies) {

        for (let gener of movies[movieId]['genres']) {

            (gener in genresMap) ? genresMap[gener].push(movieId) : genresMap[gener] = [movieId];
        }
    }
    return genresMap;
}

// Показываем только постеры по выбранным фильтрам
function filterPoster(genresMap, activeGenres, shownMovies) {
    const postersList = document.querySelectorAll('.poster-container');

    // Выбираем id фильмов, соответствующие выбранным жанрам
    for (let option of activeGenres) {
        shownMovies = shownMovies.filter(mid => genresMap[option].includes(mid));
    }

    // Отображаем постеры из отфильтрованного списка
    postersList.forEach(p => {
        (shownMovies.includes(p.dataset.kpId)) ? p.classList.remove('hidden') : p.classList.add('hidden');
    })
}

// Оставляем фильмы соответствующие выбранному жанру в фильтре
function filterMovies(movies) {

    const genresList = document.querySelectorAll('#filter li'); // элементы списка
    const allMoviesIds = Object.keys(movies); // список id всех фильмов
    let genresMap = mapGenresToMovies(movies); // соотносим жанр: фильмы
    let genres = []; // выбранные фильтры/жанры

    genresList.forEach(li => {

        li.addEventListener('click', () => {
            const genre = li.innerText;
            let shownMovies = allMoviesIds;

            genres = li.classList.contains('active') ? genres.filter(g => g !== genre) : genres.concat([genre])
            filterPoster(genresMap, genres, shownMovies);
            li.classList.toggle('active');
        })
    })

}

export {showFilter, filterMovies}