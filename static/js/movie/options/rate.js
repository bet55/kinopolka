import {getCookie} from "../../utils/cookie.js";
import {showUserRequiredModal} from "../../utils/show_modal.js";
import {showRatingModal} from "../rating_modal.js";

// Показываем модальное окно для оценки или просьбу выбрать пользователя
export const rateMovie = (allMovies, movieId, target, posterContainer) => {

    target.addEventListener('click', () => {
        const user = getCookie('user');

        if (!user) {
            showUserRequiredModal();
        } else {
            showRatingModal(movieId, allMovies);
        }
    })

}