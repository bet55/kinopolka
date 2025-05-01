import {createToast} from "./utils/create_toast.js";


const addButton = document.querySelector("#add-btn");
const spinner = addButton.querySelector('.spinner-border');
const input = document.querySelector("#movie-link");
const form = document.querySelector('form');

async function sendData() {

    const sendData = {kp_id: input.value};
    const addUrl = '';

    if (input.value.replace(/\D/g, '').length < 1) {
        createToast('В строке отсутствует id', 'error');
        return '';
    }
    addButton.disabled = true;
    spinner.style.display = 'inline-block';

    try {
        const response = await fetch(addUrl, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(sendData),
        });
        const responseJson = await response.json();

        if (responseJson['success'] === false) {
            createToast('Ошибка добавления', 'error');
        } else {
            createToast('Фильм добавлен', 'success');
        }
    } catch (e) {
        createToast('Ошибка добавления', 'error');
        console.error(e);
    }

    addButton.disabled = false;
    input.value = '';
    spinner.style.display = 'none';
}

form.addEventListener('submit', e => {
    e.preventDefault();
})


// Take over form submission
addButton.addEventListener("click", async (event) => {
    // event.preventDefault();


    await sendData();
});

