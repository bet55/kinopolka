import {createToast} from "../utils/create_toast.js";
import {Request} from "../utils/request.js";
import {confirmModalAction} from "../utils/confirm_modal_action.js";

// Глобальные переменные для состояния формы
let selectedIngredients = [];
let currentCocktailId = null;

export function createCocktail() {
    setupFormToggle();
    setupImageUpload();
    setupIngredientHandlers();
    setupFormSubmission();
}

export function updateCocktail() {
    document.querySelectorAll('.cocktail .update').forEach(button => {
        button.addEventListener('click', function () {
            const cocktailNode = this.closest('.cocktail');
            loadCocktailDataIntoForm(cocktailNode);
        });
    });
}

export function removeCocktail() {
    // Обработчик для удаления одного коктейля (если передан элемент)
    const removeSingleCocktail = async (cocktailNode) => {
        const cocktailId = cocktailNode.dataset.cocktailId;
        const response = await Request.delete({url: `/bar/cocktails/${cocktailId}/`});

        if (response) {
            cocktailNode.remove();
            createToast('Коктейль удален', 'success');
        }
    };

    // Настройка подтверждения удаления
    const setupConfirmation = (cocktailNode) => {
        const removeButton = cocktailNode.querySelector('.remove');
        const confirmationTooltip = cocktailNode.querySelector('.confirmation');

        if (!removeButton || !confirmationTooltip) return;

        const confirmModalOptions = {
            triggerNode: removeButton,
            modalNode: confirmationTooltip,
            confirmAction: async () => {
                confirmationTooltip.classList.remove('show');
                await removeSingleCocktail(cocktailNode);
            },
            declineAction: () => confirmationTooltip.classList.remove('show')
        };

        confirmModalAction(confirmModalOptions);
    };

    // Инициализация для всех коктейлей на странице
    document.querySelectorAll('.cocktail').forEach(cocktailNode => {
        setupConfirmation(cocktailNode);
    });

    // Возвращаем функцию для ручного удаления (если нужно)
    return {
        remove: removeSingleCocktail
    };
}

// ============== Вспомогательные функции ==============

function setupFormToggle() {
    const addButton = document.querySelector('#cocktails .add');
    const formContainer = document.querySelector('#new-cocktail-form');
    const cancelButton = formContainer.querySelector('.close-btn');

    addButton.addEventListener('click', () => {
        resetForm();
        formContainer.classList.toggle('hide');
    });

    cancelButton.addEventListener('click', resetForm);
}

function setupImageUpload() {
    const imageInput = document.querySelector('#cocktail-image');
    const imagePreview = document.querySelector('#cocktail-image-preview');
    const uploadLabel = document.querySelector('#new-cocktail-form .image-upload-label span');

    imageInput.addEventListener('change', function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                imagePreview.src = e.target.result;
                imagePreview.classList.remove('hide');
                uploadLabel.style.display = 'none';
            };
            reader.readAsDataURL(file);
        }
    });
}

function setupIngredientHandlers() {
    const ingredientSelect = document.querySelector('#ingredient-select');
    const amountInput = document.querySelector('#ingredient-amount');
    const unitSelect = document.querySelector('#ingredient-unit');
    const addIngredientBtn = document.querySelector('.add-ingredient-btn');
    const selectedIngredientsList = document.querySelector('#selected-ingredients-list');

    addIngredientBtn.addEventListener('click', function () {
        const ingredientId = ingredientSelect.value;
        const ingredientName = ingredientSelect.options[ingredientSelect.selectedIndex].text;
        const amount = amountInput.value;
        const unit = unitSelect.value;

        if (!amount || isNaN(amount)) {
            createToast('Укажите количество', 'error');
            return;
        }

        // Обновляем или добавляем ингредиент
        const existingIndex = selectedIngredients.findIndex(ing => ing.ingredient_id === ingredientId);
        if (existingIndex >= 0) {
            selectedIngredients[existingIndex] = {ingredient_id: ingredientId, name: ingredientName, amount, unit};
        } else {
            selectedIngredients.push({ingredient_id: ingredientId, name: ingredientName, amount, unit});
        }

        updateSelectedIngredientsList();
        amountInput.value = '';
    });

    selectedIngredientsList.addEventListener('click', function (e) {
        if (e.target.classList.contains('remove-ingredient')) {
            const ingredientId = e.target.dataset.id;
            selectedIngredients = selectedIngredients.filter(ing => ing.ingredient_id !== ingredientId);
            updateSelectedIngredientsList();
        }
    });
}

function setupFormSubmission() {
    const form = document.querySelector('#cocktail-form');
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        await submitCocktailForm();
    });
}

async function submitCocktailForm() {
    const form = document.querySelector('#cocktail-form');
    const formData = new FormData(form);
    const isEditMode = !!currentCocktailId;

    // Добавляем ингредиенты в FormData
    const ingredientsData = selectedIngredients.map(ing => ({
        ingredient: parseInt(ing.ingredient_id),
        amount: parseInt(ing.amount),
        unit: ing.unit
    }));
    console.log(ingredientsData)
    formData.append('ingredients', JSON.stringify(ingredientsData));

    try {
        const response = await Request.send({
            method: isEditMode ? 'PUT' : 'POST',
            url: isEditMode ? `/bar/cocktails/${currentCocktailId}/` : '/bar/cocktails/',
            body: formData
        });

        if (response) {
            if (isEditMode) {
                updateCocktailNode(response);
            } else {
                createCocktailNode(response);
            }
            resetForm();
            createToast(isEditMode ? 'Коктейль обновлен' : 'Коктейль добавлен', 'success');
        }
    } catch (error) {
        createToast('Ошибка при сохранении', 'error');
        console.error(error);
    }
}

function loadCocktailDataIntoForm(cocktailNode) {
    const formContainer = document.querySelector('#new-cocktail-form');
    const addButton = document.querySelector('#cocktails .add');

    // Получаем данные из DOM
    currentCocktailId = cocktailNode.dataset.cocktailId;
    const cocktailName = cocktailNode.querySelector('h3').textContent.replace('×', '').trim();
    const cocktailInstructions = cocktailNode.querySelector('.instruction').textContent.trim();
    const cocktailImage = cocktailNode.querySelector('img').src;

    // Заполняем форму
    document.querySelector('#cocktail-name').value = cocktailName;
    document.querySelector('#cocktail-instructions').value = cocktailInstructions;

    const imagePreview = document.querySelector('#cocktail-image-preview');
    imagePreview.src = cocktailImage;
    imagePreview.classList.remove('hide');
    formContainer.querySelector('.image-upload-label span').style.display = 'none';

    const unitMap = {'мл': 'ml', 'гр': 'gr', 'pcs': 'штк'};

    // Заполняем ингредиенты
    selectedIngredients = Array.from(cocktailNode.querySelectorAll('.cocktail-ingredients li')).map(ing => ({
        ingredient_id: ing.dataset.ingredientId,
        name: ing.querySelector('span:nth-child(1)').textContent.trim(),
        amount: ing.querySelector('span:nth-child(2) b').textContent.trim(),
        unit: unitMap[ing.querySelector('span:nth-child(3)').textContent.trim()]
    }));

    console.log(selectedIngredients)

    updateSelectedIngredientsList();

    // Настраиваем UI для редактирования
    addButton.textContent = 'Сохранить';
    formContainer.classList.remove('hide');
    formContainer.scrollIntoView({behavior: 'smooth'});
}

function updateSelectedIngredientsList() {
    const selectedIngredientsList = document.querySelector('#selected-ingredients-list');
    selectedIngredientsList.innerHTML = selectedIngredients.map(ing => `
        <li data-id="${ing.ingredient_id}">
            ${ing.name} - ${ing.amount} ${ing.unit}
            <button type="button" class="remove-ingredient" data-id="${ing.ingredient_id}">×</button>
        </li>
    `).join('');
}

function resetForm() {
    const form = document.querySelector('#cocktail-form');
    const formContainer = document.querySelector('#new-cocktail-form');
    const imagePreview = document.querySelector('#cocktail-image-preview');

    form.reset();
    currentCocktailId = null;
    selectedIngredients = [];
    imagePreview.src = '';
    imagePreview.classList.add('hide');
    formContainer.querySelector('.image-upload-label span').style.display = 'block';
    document.querySelector('#selected-ingredients-list').innerHTML = '';
    document.querySelector('#cocktails .add').textContent = '+ добавить';
    formContainer.classList.add('hide');
}

function createCocktailNode(cocktailData) {
    const cocktailsList = document.querySelector('#cocktails-list');
    const li = document.createElement('li');
    li.className = 'cocktail';
    li.dataset.available = cocktailData.is_available ? 'True' : 'False';
    li.dataset.cocktailId = cocktailData.id;

    li.innerHTML = `
        <img src="${cocktailData.image || '/static/img/bar/cocktail.png'}" alt="${cocktailData.name}">
        <div class="description">
            <h3>
                <img src="/static/img/bar/pencil.png" class="update">
                ${cocktailData.name}
                <span class="remove">×</span>
            </h3>
            <ul class="cocktail-ingredients">
                ${cocktailData.ingredients.map(ing => `
                    <li data-ingredient-id="${ing.ingredient.id}">
                        <span>${ing.ingredient.name}</span>
                        <span><b>${ing.amount}</b></span>
                        <span>${ing.unit}</span>
                    </li>
                `).join('')}
            </ul>
        </div>
        <p class="instruction">${cocktailData.instructions}</p>
    `;

    cocktailsList.appendChild(li);
    removeCocktail(li);
}

function updateCocktailNode(cocktailData) {
    const cocktailNode = document.querySelector(`.cocktail[data-cocktail-id="${cocktailData.id}"]`);
    if (!cocktailNode) return;

    cocktailNode.querySelector('h3').innerHTML = `
        <img src="/static/img/bar/pencil.png" class="update">
        ${cocktailData.name}
        <span class="remove">×</span>
    `;

    cocktailNode.querySelector('.instruction').textContent = cocktailData.instructions;

    if (cocktailData.image) {
        cocktailNode.querySelector('img').src = cocktailData.image;
    }

    const ingredientsUl = cocktailNode.querySelector('.cocktail-ingredients');
    ingredientsUl.innerHTML = cocktailData.ingredients.map(ing => `
        <li data-ingredient-id="${ing.ingredient.id}">
            <span>${ing.ingredient.name}</span>
            <span><b>${ing.amount}</b></span>
            <span>${ing.unit}</span>
        </li>
    `).join('');

    removeCocktail(cocktailNode);
}