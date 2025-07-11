import {createToast} from "./utils/create_toast.js";
import {Request} from "./utils/request.js";

const addButton = document.querySelector('#ingredients .add');
const ingredientsList = document.querySelector('#ingredients-list');

// Элементы формы
const formContainer = document.querySelector('#new-ingredient-form');
const cancelButton = formContainer.querySelector('.close-btn');
const imageInput = document.querySelector('#ingredient-image');
const imagePreview = document.querySelector('#image-preview');
const nameInput = document.querySelector('#ingredient-name');
const availabilityInput = document.querySelector('#ingredient-available');

// Показываем форму при нажатии на кнопку "+добавить"
addButton.addEventListener('click', function () {
    formContainer.classList.toggle('hide');
});

// Скрываем форму при нажатии на "Отменить"
cancelButton.addEventListener('click', function () {
    formContainer.classList.add('hide');
    // Сбрасываем форму
    document.querySelector('#ingredient-form').reset();
    imagePreview.classList.add('hide');
    formContainer.querySelector('.image-upload-label span').style.display = 'block';
});

// Обработка загрузки изображения
imageInput.addEventListener('change', function () {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            imagePreview.src = e.target.result;
            imagePreview.classList.remove('hide');
            formContainer.querySelector('.image-upload-label span').style.display = 'none';
        }
        reader.readAsDataURL(file);
    }
});


// Обработка отправки формы
const form = document.getElementById('ingredient-form');
form.addEventListener('submit', async function (e) {
    e.preventDefault();

    // Делаем проверку данных
    const existedIngredients = Array.from(document.querySelectorAll('#ingredients-list h6')).map(h => h.innerText.toLowerCase());
    const ingredientName = nameInput.value.toLowerCase();
    if (existedIngredients.includes(ingredientName)) {
        createToast('Ингредиент уже существует!', 'error');
        return null;
    }

    // Обновляем список ингредиентов
    const formData = new FormData();
    formData.append('name', ingredientName[0] + ingredientName.slice(1));
    formData.append('is_available', availabilityInput.checked);

    if (imageInput.files[0]) {
        formData.append('image', imageInput.files[0]);
    }

    const response = await Request.post({url: '/bar/ingredients/', body: formData});
    if (response) {
        console.log(response);

        const li = document.createElement('li');
        const img = document.createElement('img');
        const h6 = document.createElement('h6');

        h6.innerText = capitalizeName;
        img.src = imagePreview.src;
        li.classList.add('ingredient');
        li.dataset.availabe = availabilityInput.checked;

        li.appendChild(img);
        li.appendChild(h6);
        ingredientsList.appendChild(li);
    }

    // Сбрасываем форму
    formContainer.classList.toggle('hide');
    form.reset();
    imagePreview.src = '';
    imagePreview.classList.add('hide');
    formContainer.querySelector('.image-upload-label span').style.display = 'block';
});


// Обработка удаления
document.querySelectorAll('.ingredient .remove').forEach(ing => {
    ing.addEventListener('click', async (e) => {
        const ingredientId = e.target.parentElement.dataset.ingredientId;
        const response = await Request.delete({url: `/bar/ingredients/${ingredientId}/`});

        if(response) {
            e.target.parentElement.remove();
        }
    })
});