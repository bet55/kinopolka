import {removeFromCart} from "../../based_layout/movies_cart.js";
import {Request} from "../../utils/request.js";

export const removeMovie = async (allMovies, movieId, target, posterContainer) => {

    const url = '/movies/remove/';
    const sendData = {kp_id: movieId};

    const response = await Request.send('delete', url, sendData);
    if (response === null) {
        return null;
    }
    document.querySelector('.tooltip').remove() // удаляем подсказку
    removeFromCart(movieId); // чистим корзину в шапке
    posterContainer.remove(); // удаляем постер

}