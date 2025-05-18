import {removeFromCart} from "../../based_layout/movies_cart.js";
import {Request} from "../../utils/request.js";
import {confirmModalAction} from "../../utils/confirm_modal_action.js";


async function remove(posterContainer, movieId) {

    const url = '/movies/remove/';
    const sendData = {kp_id: movieId};

    const response = await Request.delete({url: url, body: sendData});

    if (response === null) {
        return null;
    }

    // удаляем подсказку
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove()
    }

    removeFromCart(movieId); // чистим корзину в шапке
    posterContainer.remove(); // удаляем постер
}

export const removeMovie = async (allMovies, movieId, target, posterContainer) => {
    const confirmWindow = document.querySelector(`.poster-container[data-kp-id="${movieId}"] .confirmation`);

    // Отображаем окно подтверждения удаления
    const confirmModalOptions = {
        triggerNode: target,
        modalNode: confirmWindow,
        confirmAction: async () => await remove(posterContainer, movieId)
    }
    confirmModalAction(confirmModalOptions);

}