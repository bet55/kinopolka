import {bookedToggle} from "./booked_toggler.js";

// Меняем иконку на активную у фильмов в закладках
export function paintBookedMovies() {

    let lsKeys = Object.keys(localStorage);

    for (let key of lsKeys) {
        if (isNaN(key)) {
            continue;
        }
        bookedToggle(key);

    }

}
