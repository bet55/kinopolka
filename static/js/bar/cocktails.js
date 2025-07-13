import {createToast} from "../utils/create_toast.js";
import {Request} from "../utils/request.js";
import {confirmModalAction} from "../utils/confirm_modal_action.js";

function createCocktailNode(cocktailData) {
    // Создаем элемент коктейля для добавления в список
    const cocktailsList = document.querySelector('#cocktails-list');

    const li = document.createElement('li');
    li.className = 'cocktail';
    li.dataset.available = cocktailData.is_available ? 'True' : 'False';

    const img = document.createElement('img');
    img.src = cocktailData.image || '/static/img/bar/cocktail.png';
    img.alt = cocktailData.name;

    const descriptionDiv = document.createElement('div');
    descriptionDiv.className = 'description';

    const h3 = document.createElement('h3');
    h3.textContent = cocktailData.name;

    const ingredientsUl = document.createElement('ul');
    ingredientsUl.className = 'cocktail-ingredients';

    cocktailData.ingredients.forEach(ing => {
        const ingLi = document.createElement('li');
        ingLi.innerHTML = `
            <span>${ing.ingredient.name}</span>
            <span><b>${ing.amount}</b></span>
            <span>${ing.unit}</span>
        `;
        ingredientsUl.appendChild(ingLi);
    });

    const instructionP = document.createElement('p');
    instructionP.className = 'instruction';
    instructionP.textContent = cocktailData.instructions;

    // Окно подтверждения
    const div = document.createElement('li');
    const h4 = document.createElement('h4');
    const btnConf = document.createElement('button');
    const btnDecline = document.createElement('button');

    h4.innerText = 'Удалить коктейль?';
    btnConf.innerText = 'Да';
    btnDecline.innerText = 'Нет';
    btnConf.classList.add('confirm-yes');
    btnDecline.classList.add('confirm-no');
    div.className = 'confirmation container-fluid center';

    div.appendChild(h4);
    div.appendChild(btnConf);
    div.appendChild(btnDecline);


    descriptionDiv.appendChild(div);
    descriptionDiv.appendChild(h3);
    descriptionDiv.appendChild(ingredientsUl);

    li.appendChild(img);
    li.appendChild(descriptionDiv);
    li.appendChild(instructionP);

    cocktailsList.appendChild(li);
}

function createCocktail() {
    const addButton = document.querySelector('#cocktails .add');
    const formContainer = document.querySelector('#new-cocktail-form');
    const form = document.querySelector('#cocktail-form');
    const cancelButton = formContainer.querySelector('.close-btn');
    const imageInput = document.querySelector('#cocktail-image');
    const imagePreview = document.querySelector('#cocktail-image-preview');
    const nameInput = document.querySelector('#cocktail-name');
    const instructionsInput = document.querySelector('#cocktail-instructions');
    const ingredientSelect = document.querySelector('#ingredient-select');
    const amountInput = document.querySelector('#ingredient-amount');
    const unitSelect = document.querySelector('#ingredient-unit');
    const addIngredientBtn = document.querySelector('.add-ingredient-btn');
    const selectedIngredientsList = document.querySelector('#selected-ingredients-list');

    let selectedIngredients = [];

    // Показываем/скрываем форму
    addButton.addEventListener('click', () => formContainer.classList.toggle('hide'));
    cancelButton.addEventListener('click', resetForm);

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

    // Добавление ингредиента в список
    addIngredientBtn.addEventListener('click', function () {
        const ingredientId = ingredientSelect.value;
        const ingredientName = ingredientSelect.options[ingredientSelect.selectedIndex].text;
        const amount = amountInput.value;
        const unit = unitSelect.value;

        if (!amount || isNaN(amount)) {
            createToast('Укажите количество', 'error');
            return;
        }

        // Проверяем, не добавлен ли уже этот ингредиент
        if (selectedIngredients.some(ing => ing.ingredient_id === ingredientId)) {
            createToast('Этот ингредиент уже добавлен', 'error');
            return;
        }

        // Добавляем в массив выбранных ингредиентов
        selectedIngredients.push({
            ingredient_id: ingredientId,
            name: ingredientName,
            amount: amount,
            unit: unit
        });

        // Обновляем список на экране
        updateSelectedIngredientsList();

        // Сбрасываем поля ввода
        amountInput.value = '';
    });

    // Удаление ингредиента из списка
    selectedIngredientsList.addEventListener('click', function (e) {
        if (e.target.classList.contains('remove-ingredient')) {
            const ingredientId = e.target.dataset.id;
            selectedIngredients = selectedIngredients.filter(ing => ing.ingredient_id !== ingredientId);
            updateSelectedIngredientsList();
        }
    });

    // Отправка формы
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        if (selectedIngredients.length === 0) {
            createToast('Добавьте хотя бы один ингредиент', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('name', nameInput.value);
        formData.append('instructions', instructionsInput.value);

        const ingredients = selectedIngredients.map(ing => ({
            ingredient: parseInt(ing.ingredient_id), // Убедимся, что ID — число
            amount: parseInt(ing.amount), // Убедимся, что количество — число
            unit: ing.unit
        }));

    // Добавляем ingredients как JSON-строку
        formData.append('ingredients', JSON.stringify(ingredients));

        if (imageInput.files[0]) {
            formData.append('image', imageInput.files[0]);
        }


        const response = await Request.post({url: '/bar/cocktails/', body: formData});

        if (response) {
            createCocktailNode(response);
            resetForm();
        }
    });

    function updateSelectedIngredientsList() {
        selectedIngredientsList.innerHTML = '';

        selectedIngredients.forEach(ing => {
            const li = document.createElement('li');
            li.innerHTML = `
                ${ing.name} - ${ing.amount} ${ing.unit}
                <button type="button" class="remove-ingredient" data-id="${ing.ingredient_id}">×</button>
            `;
            selectedIngredientsList.appendChild(li);
        });
    }

    function resetForm() {
        form.reset();
        imagePreview.src = '';
        imagePreview.classList.add('hide');
        formContainer.querySelector('.image-upload-label span').style.display = 'block';
        selectedIngredients = [];
        selectedIngredientsList.innerHTML = '';

        formContainer.classList.toggle('hide')
    }
}

function updateCocktail() {

}

function removeCocktail(cocktail) {

    const cocktails = cocktail ? [cocktail] : document.querySelectorAll('.cocktail');

    const remove = async (cocktailId, cocktailNode) => {
        const response = await Request.delete({url: `/bar/cocktails/${cocktailId}/`});

        if (response) {
            cocktailNode.remove();
        }
    }

    cocktails.forEach(cock => {
        const button = cock.querySelector('.remove');
        const confirmContainer = cock.querySelector('.confirmation');
        const cockId = cock.dataset.cocktailId;

        // Отображаем окно подтверждения удаления
        const confirmModalOptions = {
            triggerNode: button,
            modalNode: confirmContainer,
            confirmAction: async () => await remove(cockId, cock)
        }
        confirmModalAction(confirmModalOptions);
    })

}

export {createCocktail, updateCocktail, removeCocktail};