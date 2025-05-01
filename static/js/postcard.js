import {cartHandler} from "./postcard/movies_cart.js";
import {createToast} from "./utils/create_toast.js";
import {screenshot} from "./utils/screenshot.js";
import {getNextSaturday} from "./utils/next_saturday.js";

let isPending = false;

// Отправляем приглашение с открыткой
function sendPostcard() {

    const sendButton = document.querySelector('#postcard-send-button');

    if (!sendButton) {
        return null;
    }

    sendButton.addEventListener('click', () => {
        // Всё еще исполняется предыдущее действие
        if (isPending) {
            return null;
        }


        sendButton.classList.add('active_option')

        const url = '/invitation/';

        const requestOptions = {
            method: "POST",
            redirect: "follow"
        };

        isPending = true;
        fetch(url, requestOptions)
            .then((response) => {

                if (!response.ok) {
                    throw Error(`${response.status}: ${response.text()}`);
                }
                return response.text()

            })
            .then((result) => {

                createToast('Открытка отправлена', 'success');
                sendButton.classList.remove('active_option')
                isPending = false;

            })
            .catch((error) => {

                console.error(error);
                createToast('Открытка не отправлена', 'error');
                sendButton.classList.remove('active_option')
                isPending = false;
            });


    })
}


// Архивируем предыдущую открытку и выводим пустой бланк
function createPostcard() {
    const createButton = document.querySelector('#postcard-create-button');

    if (!createButton) {
        return null;
    }

    createButton.addEventListener('click', () => {

        // Всё еще исполняется предыдущее действие
        if (isPending) {
            return null;
        }


        createButton.classList.add('active_option')

        const url = document.baseURI.split('/', 3).join('/') + '/';

        const requestOptions = {
            method: "PUT",
            redirect: "follow"
        };

        isPending = true;
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
                isPending = false;
            });


    })


}


// Сохраняем открытку в базе
const savePostcard = async () => {
    const saveButton = document.querySelector('#postcard-save-button');
    const postcard = document.querySelector('#postcard-container');
    const title = document.querySelector('#invitation-title');

    if (!saveButton) {
        return null;
    }

    // Предположение, что будет в следующую субботу
    title.innerText = getNextSaturday('text');

    saveButton.addEventListener('click', async e => {

        // Всё еще исполняется предыдущее действие
        if (isPending) {
            return null;
        }


        const postcardFilled = (title.innerText.replace(/\D/g, '')) && document.querySelector('.poster');

        if (!postcardFilled) {
            createToast('Заполните открытку', 'error')
            return null;
        }

        saveButton.classList.add('active_option')
        isPending = true;

        title.contentEditable = false;
        const posters = document.querySelectorAll('.poster');
        const posters_ids = Array.from(posters).map(p => p.dataset.kpId);
        await screenshot(postcard, posters_ids, title.innerText, getNextSaturday('iso'));

        isPending = false;
        saveButton.classList.remove('active_option')


    })


}

savePostcard();
createPostcard();
sendPostcard();
cartHandler();