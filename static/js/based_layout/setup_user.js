import {setCookie, getCookie, deleteCookie} from "../utils/cookie.js";

const usersPanel = document.querySelector('#users-panel');
const usersSetButton = usersPanel.querySelector('.dropdown-toggle');
const usersSelector = document.querySelector('#users-selector');

// Только для архивного списка!
const rateToggler = document.querySelector('#rate-toggle');

const changeUserView = () => {

    const currentUser = getCookie('user');

    if (!currentUser) {
        return null;
    }
    console.log(currentUser)
    const userName = usersPanel.querySelector(`button[data-user-id="${currentUser}"]`).textContent;

    // Кривая кука, удалим её
    if (!userName) {
        deleteCookie('user');
        return null;
    }

    usersSetButton.textContent = userName;

    // Красим кнопку отображения оценок в цвет пользователя
    if(rateToggler) {
        rateToggler.src = rateToggler.src.replace(/note\d*\.png/, `note${currentUser}.png`);
    }
}

export function settingUserHandler() {
    changeUserView();

    const usersElements = usersSelector.querySelectorAll('.dropdown-item');

    usersElements.forEach(e => {
        e.addEventListener('click', e => {
            const user = e.target.dataset.userId;
            setCookie('user', user);
            changeUserView();
        })
    })


}