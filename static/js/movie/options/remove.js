import {createToast} from "../../utils/create_toast.js";
import {removeFromCart} from "../../based_layout/movies_cart.js";

export const removeMovie = (allMovies, movieId, target, posterContainer) => {

    const removeUrl = '/movies/remove/';
    const sendData = {kp_id: movieId};

    fetch(removeUrl, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(sendData)
    }).then(rs => rs.json()).then((data) => {
        if (data['success'] === false) {
            createToast(data['error'], 'error');
            console.log(data);
        } else {
            document.querySelector('.tooltip').remove() // удаляем подсказку
            removeFromCart(movieId); // чистим корзину в шапке
            posterContainer.remove(); // удаляем постер
        }

    }).catch(rs => {
        createToast('Ошибка удаления', 'error');
        console.error(rs)
    });

}