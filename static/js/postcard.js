import {cartHandler} from "./postcard/movies_cart.js";
import {createToast} from "./utils/create_toast.js";
import {modernShot} from "./utils/screenshot.js";




const savePostcard = async () => {
    const saveButton = document.querySelector('#postcard-save-button');
    const postcard = document.querySelector('#postcard-container');
    const title = document.querySelector('#invitation-title');


    saveButton.addEventListener('click', async e => {

        if (title.innerText.replace(/\D/g, '').length < 1) {
            createToast('Введите дату церемонии', 'error')
        } else {
            title.contentEditable = false;
            await modernShot(postcard, 'client');
        }
    })


}

savePostcard();
cartHandler();