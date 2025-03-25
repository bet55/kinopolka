import {cartHandler} from "./postcard/movies_cart.js";
import {createToast} from "./utils/create_toast.js";
import {screenshot} from "./utils/screenshot.js";


const savePostcard = async () => {
    const saveButton = document.querySelector('#postcard-save-button');
    const postcard = document.querySelector('#postcard-container');
    const title = document.querySelector('#invitation-title');


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
cartHandler();