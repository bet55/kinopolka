import {createToast} from "../utils/create_toast.js";
import {Request} from "../utils/request.js";
import {confirmModalAction} from "../utils/confirm_modal_action.js";
import {capitalise} from "../utils/capitalise.js";


// Глобальные переменные для состояния
let currentIngredientId = null;

export function createIngredient() {
    setupFormToggle();
    setupImageUpload();
    setupFormSubmission();
}

export function updateIngredient() {
    document.querySelectorAll('.ingredient .update').forEach(button => {
        button.addEventListener('click', async function () {
            const ingredientNode = this.closest('.ingredient');
            const ingredientId = ingredientNode.dataset.ingredientId;
            const isAvailable = ingredientNode.dataset.available === 'True';

            try {
                const response = await Request.put({
                    url: `/bar/ingredients/${ingredientId}/`,
                    body: {is_available: !isAvailable}
                });

                if (response) {
                    // Обновляем состояние на клиенте
                    ingredientNode.dataset.available = !isAvailable ? 'True' : 'False';

                    // Обновляем доступность связанных коктейлей
                    await updateCocktailsAvailability();
                }
            } catch (error) {
                createToast('Ошибка при обновлении', 'error');
                console.error(error);
            }
        });
    });
}

export function removeIngredient() {
    document.querySelectorAll('.ingredient').forEach(ingredientNode => {
        const button = ingredientNode.querySelector('.remove');
        const confirmContainer = ingredientNode.querySelector('.confirmation');
        const ingredientName = ingredientNode.querySelector('h6').innerText.toLowerCase();

        const confirmModalOptions = {
            triggerNode: button,
            modalNode: confirmContainer,
            confirmAction: async () => {
                try {
                    // Проверяем, используется ли ингредиент
                    const usedInCocktails = await checkIngredientUsage(ingredientName);
                    if (usedInCocktails) {
                        createToast('Ингредиент используется в коктейлях!', 'error');
                        return;
                    }

                    const response = await Request.delete({url: `/bar/ingredients/${ingredientNode.dataset.ingredientId}/`});
                    if (response) {
                        ingredientNode.remove();
                        createToast('Ингредиент удален', 'success');
                        await refreshIngredientSelect();
                    }
                } catch (error) {
                    createToast('Ошибка при удалении', 'error');
                    console.error(error);
                }
            }
        };

        confirmModalAction(confirmModalOptions);
    });
}

// ============== Вспомогательные функции ==============

function setupFormToggle() {
    const addButton = document.querySelector('#ingredients .add');
    const formContainer = document.querySelector('#new-ingredient-form');
    const cancelButton = formContainer.querySelector('.close-btn');

    addButton.addEventListener('click', () => {
        // resetForm();
        formContainer.classList.toggle('hide');
    });

    cancelButton.addEventListener('click', resetForm);
}

function setupImageUpload() {
    const imageInput = document.querySelector('#ingredient-image');
    const imagePreview = document.querySelector('#image-preview');
    const uploadLabel = document.querySelector('#new-ingredient-form .image-upload-label span');

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

function setupFormSubmission() {
    const form = document.querySelector('#ingredient-form');
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        await submitIngredientForm();
    });
}

async function submitIngredientForm() {
    const form = document.querySelector('#ingredient-form');
    const formData = new FormData(form);
    const nameInput = document.querySelector('#ingredient-name');
    const ingredientName = capitalise(nameInput.value);
    nameInput.value = ingredientName;

    // Проверка на существующий ингредиент
    const existingIngredients = Array.from(document.querySelectorAll('#ingredients-list h6'))
        .map(el => capitalise(el.innerText));

    if (existingIngredients.includes(ingredientName)) {
        createToast('Ингредиент уже существует!', 'error');
        return;
    }

    try {
        const response = await Request.post({
            url: '/bar/ingredients/',
            body: formData
        });

        if (response) {
            createIngredientNode(response);
            resetForm();
            createToast('Ингредиент добавлен', 'success');
            await refreshIngredientSelect(); // Обновляем список в форме коктейлей
        }
    } catch (error) {
        createToast('Ошибка при сохранении', 'error');
        console.error(error);
    }
}

function createIngredientNode(ingredientData) {
    const ingredientsList = document.querySelector('#ingredients-list');
    const li = document.createElement('li');
    li.className = 'ingredient';
    li.dataset.available = ingredientData.is_available ? 'True' : 'False';
    li.dataset.ingredientId = ingredientData.id;

    li.innerHTML = `
        <img src="${ingredientData.image || '/static/img/bar/ingredient.png'}" alt="${ingredientData.name}">
        <h6>${capitalise(ingredientData.name)}</h6>
        <button class="update"><img src="/static/img/bar/box.png" alt=""></button>
        <button class="remove">×</button>
        <li class="confirmation container-fluid left">
            <h4>Удалить ингредиент?</h4>
            <button class="confirm-yes">Да</button>
            <button class="confirm-no">Нет</button>
        </li>
    `;

    ingredientsList.appendChild(li);
    updateIngredient();
    removeIngredient();
}

async function refreshIngredientSelect() {
    try {
        const ingredients = await Request.get({url: '/bar/ingredients/'});
        if (!ingredients) return;

        // 1. Обновляем оригинальный select
        const select = document.querySelector('#ingredient-select');
        select.innerHTML = ingredients.map(ing =>
            `<option value="${ing.id}">${capitalise(ing.name)}</option>`
        ).join('');

        // 2. Обновляем кастомный интерфейс
        const customSelect = document.querySelector('#custom-ingredient-select');
        const customOptions = document.querySelector('#custom-ingredient-options');

        if (customSelect && customOptions) {
            // Сохраняем текущее выбранное значение
            const currentValue = select.value;
            const currentText = select.options[select.selectedIndex]?.text || 'Выберите ингредиент';

            // Обновляем основной текст
            customSelect.textContent = currentText;

            // Обновляем список опций
            customOptions.innerHTML = ingredients.map(ing => `
                <div class="custom-select-option" data-value="${ing.id}">
                    ${capitalise(ing.name)}
                </div>
            `).join('');

            // 3. Полностью переинициализируем обработчики
            setupCustomSelectHandlers();
        }

    } catch (error) {
        console.error('Ошибка при обновлении списка ингредиентов:', error);
        createToast('Не удалось обновить список ингредиентов', 'error');
    }
}

function setupCustomSelectHandlers() {
    const customSelect = document.querySelector('#custom-ingredient-select');
    const customOptions = document.querySelector('#custom-ingredient-options');
    const originalSelect = document.querySelector('#ingredient-select');

    if (!customSelect || !customOptions) return;

    // Удаляем старые обработчики
    customSelect.replaceWith(customSelect.cloneNode(true));
    customOptions.replaceWith(customOptions.cloneNode(true));

    // Получаем новые элементы после клонирования
    const newCustomSelect = document.querySelector('#custom-ingredient-select');
    const newCustomOptions = document.querySelector('#custom-ingredient-options');
    const options = newCustomOptions.querySelectorAll('.custom-select-option');

    // Обработчик клика по кастомному селекту
    newCustomSelect.addEventListener('click', function (e) {
        e.stopPropagation();
        newCustomOptions.style.display = newCustomOptions.style.display === 'block' ? 'none' : 'block';
    });

    // Обработчики для опций
    options.forEach(option => {
        option.addEventListener('click', function () {
            const value = this.getAttribute('data-value');
            const text = this.textContent;

            originalSelect.value = value;
            newCustomSelect.textContent = text;
            newCustomOptions.style.display = 'none';
        });
    });

    // Закрытие при клике вне списка
    document.addEventListener('click', function () {
        newCustomOptions.style.display = 'none';
    });
}

async function checkIngredientUsage(ingredientName) {
    try {
        const cocktails = await Request.get({url: '/bar/cocktails/'});
        return cocktails.some(cocktail =>
            cocktail.ingredients.some(ing =>
                ing.ingredient.name.toLowerCase() === ingredientName.toLowerCase()
            )
        );
    } catch (error) {
        console.error('Ошибка при проверке использования ингредиента:', error);
        return true; // В случае ошибки предполагаем, что ингредиент используется
    }
}

async function updateCocktailsAvailability() {
    try {
        const cocktails = await Request.get({url: '/bar/cocktails/'});
        if (cocktails) {
            document.querySelectorAll('.cocktail').forEach(cocktailNode => {
                const cocktail = cocktails.find(c => c.id == cocktailNode.dataset.cocktailId);
                if (cocktail) {
                    cocktailNode.dataset.available = cocktail.is_available ? 'True' : 'False';
                }
            });
        }
    } catch (error) {
        console.error('Ошибка при обновлении коктейлей:', error);
    }
}

function resetForm() {
    const form = document.querySelector('#ingredient-form');
    const formContainer = document.querySelector('#new-ingredient-form');
    const imagePreview = document.querySelector('#image-preview');

    form.reset();
    currentIngredientId = null;
    imagePreview.src = '';
    imagePreview.classList.add('hide');
    formContainer.querySelector('.image-upload-label span').style.display = 'block';
    formContainer.classList.add('hide');
}