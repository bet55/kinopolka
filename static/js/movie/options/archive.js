import {createToast} from "../../utils/create_toast.js";
import {Request} from "../../utils/request.js";

export const changeMovieArchiveStatus = async (allMovies, movieId, target, posterContainer) => {
    const isArchive = document.URL.includes('archive');

    const url = '/movies/change_archive/';
    const sendData = {kp_id: movieId, is_archive: !isArchive};

    const response = await Request.send({method:'patch', url: url, body: sendData})
    if(response === null) {
        return null;
    }

    // Удаляем фильм со страницы
    posterContainer.remove();
}
