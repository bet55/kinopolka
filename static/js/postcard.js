import {cartHandler} from "./postcard/movies_cart.js";
import {createToast} from "./utils/create_toast.js";
import {screenshot} from "./utils/screenshot.js";


function sendPostcard() {
    const sendButton = document.querySelector('#postcard-send-button');

    if (!sendButton) {
        return false
    }

    sendButton.addEventListener('click', () => {
        console.log('send email')
    })
}

function createPostcard() {
    const createButton = document.querySelector('#postcard-create-button');

    if (!createButton) {
        return false
    }

    createButton.addEventListener('click', () => {
        const url = document.baseURI.split('/', 3).join('/');

        const requestOptions = {
            method: "PUT",
            redirect: "follow"
        };

        console.log('Создаём открытку ...')


        fetch(url, requestOptions)
            .then((response) => response.text())
            .then((result) => {
                console.log(result)

                // Перезагружаем страницу
                window.location.reload();
            })
            .catch((error) => console.error(error));

    })


}


const savePostcard = async () => {
    const saveButton = document.querySelector('#postcard-save-button');
    const postcard = document.querySelector('#postcard-container');
    const title = document.querySelector('#invitation-title');

    if (!saveButton) {
        return false
    }


    saveButton.addEventListener('click', async e => {

        if (title.innerText.replace(/\D/g, '').length < 1) {
            createToast('Введите дату церемонии', 'error')
        } else {
            const posters = document.querySelectorAll('.poster');
            title.contentEditable = false;
            const posters_ids = Array.from(posters).map(p => p.dataset.kpId);
            await screenshot(postcard, posters_ids, title.innerText);


        }
    })


}

savePostcard();
createPostcard();
sendPostcard();
cartHandler();