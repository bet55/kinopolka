import {createToast} from "./utils/create_toast.js";
import {Request} from "./utils/request.js";


const addButton = document.querySelector("#add-btn");
const spinner = addButton.querySelector('.spinner-border');
const input = document.querySelector("#movie-link");
const form = document.querySelector('form');

async function sendData() {

    if (input.value.replace(/\D/g, '').length < 1) {
        createToast('В строке отсутствует id', 'info');
        return null;
    }

    // Отображаем выполнение запроса
    addButton.disabled = true;
    spinner.style.display = 'inline-block';

    // Запрос на добавление фильма
    await Request.send({method: 'post', url: '', body: {kp_id: input.value}});

    // Возвращаем страницу в изначальное состояние
    addButton.disabled = false;
    input.value = '';
    spinner.style.display = 'none';
}

form.addEventListener('submit', e => {
    e.preventDefault();
})



// Take over form submission
addButton.addEventListener("click", async (event) => {
    await sendData();
});

