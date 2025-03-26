import {cartHandler} from "./postcard/movies_cart.js";
import {createToast} from "./utils/create_toast.js";
import {screenshot} from "./utils/screenshot.js";
import {getNextSaturday} from "./utils/next_saturday.js";


function sendPostcard() {
    const sendButton = document.querySelector('#postcard-send-button');

    if (!sendButton) {
        return null;
    }

    sendButton.addEventListener('click', () => {
        sendButton.classList.add('active_option')

        createToast('Отправка email пока не работает', 'info');

        setTimeout(() => sendButton.classList.remove('active_option'), 1000)


    })
}

function createPostcard() {
    const createButton = document.querySelector('#postcard-create-button');

    if (!createButton) {
        return null;
    }

    createButton.addEventListener('click', () => {
        createButton.classList.add('active_option')

        const url = document.baseURI.split('/', 3).join('/');

        const requestOptions = {
            method: "PUT",
            redirect: "follow"
        };


        fetch(url, requestOptions)
            .then((response) => {
                if (!response.ok) {
                    throw Error(`${response.status}: ${response.text()}`);
                }
                return response.text()
            })
            .then((result) => {

                createToast('Открытка заархивирована', 'success');
                createButton.classList.remove('active_option')

                // Перезагружаем страницу
                setTimeout(() => window.location.reload(), 1000)

            })
            .catch((error) => {

                console.error(error);
                createToast('Открытка не заархивирована', 'error');
                createButton.classList.remove('active_option')
            });


    })


}


const savePostcard = async () => {
    const saveButton = document.querySelector('#postcard-save-button');
    const postcard = document.querySelector('#postcard-container');
    const title = document.querySelector('#invitation-title');

    if (!saveButton) {
        return null;
    }

    // Времянка, пока не доделаем модели
    title.innerText = getNextSaturday('text');
    title.contentEditable = false;

    saveButton.addEventListener('click', async e => {

        const postcardFilled = (title.innerText.replace(/\D/g, '')) && document.querySelector('.poster');

        if (!postcardFilled) {
            createToast('Заполните открытку', 'error')
            return null;
        }

        saveButton.classList.add('active_option')

        title.contentEditable = false;
        const posters = document.querySelectorAll('.poster');
        const posters_ids = Array.from(posters).map(p => p.dataset.kpId);
        await screenshot(postcard, posters_ids, getNextSaturday('iso'));

        saveButton.classList.remove('active_option')


    })


}

savePostcard();
createPostcard();
sendPostcard();
cartHandler();