import {createToast} from "../utils/create_toast.js";
import {Request} from "../utils/request.js";
import {confirmModalAction} from "../utils/confirm_modal_action.js";


function createNode(capitalizeName, imagSrc, isAvailable, id) {
    // Руками создаем элементы для созданного ингредиента

    const ingredientsList = document.querySelector('#ingredients-list');

    // Добавляем в ингредиент на страницу, чтобы не делать перезагрузку
    const li = document.createElement('li');
    const img = document.createElement('img');
    const h6 = document.createElement('h6');
    const btnUpdate = document.createElement('button');
    const btnIcon = document.createElement('img');
    const btnRemove = document.createElement('button');

    h6.innerText = capitalizeName;
    img.src = imagSrc ? imagSrc : '/static/img/bar/ingredient.png';
    btnIcon.src = '/static/img/bar/box.png';
    btnRemove.innerText = '×';
    btnUpdate.classList.add('update');
    btnRemove.classList.add('remove');
    li.classList.add('ingredient');
    li.dataset.available = isAvailable ? 'True' : 'False';
    li.dataset.ingredientId = id;


    // Окно подтверждения
    const div = document.createElement('li');
    const h4 = document.createElement('h4');
    const btnConf = document.createElement('button');
    const btnDecline = document.createElement('button');

    h4.innerText = 'Удалить ингредиент?';
    btnConf.innerText = 'Да';
    btnDecline.innerText = 'Нет';
    btnConf.classList.add('confirm-yes');
    btnDecline.classList.add('confirm-no');
    div.className = 'confirmation container-fluid left';

    div.appendChild(h4);
    div.appendChild(btnConf);
    div.appendChild(btnDecline);


    btnUpdate.appendChild(btnIcon);
    li.appendChild(img);
    li.appendChild(h6);
    li.appendChild(btnUpdate);
    li.appendChild(btnRemove);
    li.appendChild(div);
    ingredientsList.appendChild(li);

    // Слушатели добавленных кнопок
    updateIngredient(li);
    removeIngredient(li);
}

function createIngredient() {

    const addButton = document.querySelector('#ingredients .add');

    // Элементы формы
    const formContainer = document.querySelector('#new-ingredient-form');
    const form = formContainer.querySelector('#ingredient-form');
    const cancelButton = formContainer.querySelector('.close-btn');
    const imageInput = formContainer.querySelector('#ingredient-image');
    const imagePreview = formContainer.querySelector('#image-preview');
    const nameInput = formContainer.querySelector('#ingredient-name');
    const availabilityInput = formContainer.querySelector('#ingredient-available');

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
        imagePreview.src = '';
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
        const capitalizeName = ingredientName[0].toUpperCase() + ingredientName.slice(1);
        const formData = new FormData();
        formData.append('name', capitalizeName);
        formData.append('is_available', availabilityInput.checked);

        if (imageInput.files[0]) {
            formData.append('image', imageInput.files[0]);
        }

        const response = await Request.post({url: '/bar/ingredients/', body: formData});
        if (response === null || !response.id) {
            return null;
        }

        // Создаём элемент, вместо перезагрузки страницы
        createNode(capitalizeName, imagePreview.src, availabilityInput.checked, response.id);


        // Сбрасываем форму
        formContainer.classList.toggle('hide');
        form.reset();
        imagePreview.src = '';
        imagePreview.classList.add('hide');
        formContainer.querySelector('.image-upload-label span').style.display = 'block';
    });

}


function updateIngredient(ingredient) {
    const ingredients = ingredient ? [ingredient] : document.querySelectorAll('.ingredient');

    ingredients.forEach(ing => {
        ing.querySelector('.update').addEventListener('click', async (e) => {
            const ingredientId = ing.dataset.ingredientId;
            const isAvailable = ing.dataset.available === 'True';
            let response = await Request.put({
                url: `/bar/ingredients/${ingredientId}/`,
                body: {is_available: !isAvailable}
            });

            if (response === null) {
                return null
            }

            // Изменим статус ингредиента на странице
            ing.dataset.available = isAvailable ? 'False' : 'True';

            // Запросим заново информацию о коктейлях, чтобы отобразить корректный статус
            const cocktails = await Request.get({url: '/bar/cocktails/'});
            if (cocktails === null) {
                return null
            }

            const availabilityMap = cocktails.reduce((acc, cocktail) => {
                acc[cocktail.id] = cocktail.is_available;
                return acc;
            }, {});


            const cocktailsElements = document.querySelectorAll('.cocktail');
            cocktailsElements.forEach(cock => {
              cock.dataset.available = availabilityMap[cock.dataset.cocktailId] ? 'True': 'False';
            })


        })
    });
}


function removeIngredient(ingredient) {
    const ingredients = ingredient ? [ingredient] : document.querySelectorAll('.ingredient');

    const remove = async (ingredientId, ingredientName, ingredientNode) => {
        const existedIngredients = Array.from(document.querySelectorAll('.cocktail-ingredients span')).map(h => h.innerText.toLowerCase());
        if (existedIngredients.includes(ingredientName)) {
            createToast('Ингредиент используется в коктейлях!', 'error');
            return null;
        }

        const response = await Request.delete({url: `/bar/ingredients/${ingredientId}/`});

        if (response) {
            ingredientNode.remove();
        }
    }

    ingredients.forEach(ing => {
        const button = ing.querySelector('.remove');
        const confirmContainer = ing.querySelector('.confirmation');
        const ingredientName = ing.querySelector('h6').innerText.toLowerCase();

        // Отображаем окно подтверждения удаления
        const confirmModalOptions = {
            triggerNode: button,
            modalNode: confirmContainer,
            confirmAction: async () => await remove(ing.dataset.ingredientId, ingredientName, ing)
        }
        confirmModalAction(confirmModalOptions);


    });

}


export {createIngredient, updateIngredient, removeIngredient}
