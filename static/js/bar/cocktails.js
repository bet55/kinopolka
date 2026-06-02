import {createToast} from "../utils/create_toast.js";
import {Request} from "../utils/request.js";
import {confirmModalAction} from "../utils/confirm_modal_action.js";
import {capitalise} from "../utils/capitalise.js";
import {getCookie} from "../utils/cookie.js";
import {getRandomItem} from "../utils/get_random_item.js";

// Глобальные переменные для состояния формы
let selectedIngredients = [];
let currentCocktailId = null;
let imageCorrect = true;
const UNIT_MAP = {'мл': 'ml', 'гр': 'g', 'pcs': 'штк'};

export function createCocktail() {
    setupFormToggle();
    setupImageUpload();
    setupIngredientHandlers();
    setupFormSubmission();
    setupCustomSelect();
}

export function updateCocktail(cocktail) {
    const cocktailsList = cocktail ? [cocktail] : document.querySelectorAll('.cocktail');

    cocktailsList.forEach(cock => {
        const button = cock.querySelector('.update');
        button.addEventListener('click', function () {
            const cocktailNode = this.closest('.cocktail');
            loadCocktailDataIntoForm(cocktailNode);
        });
    });
}

export function telegramRequest(cocktail) {
    const cocktailsList = cocktail ? [cocktail] : document.querySelectorAll('.cocktail');

    const createMessage = (userName, cockName, ingredients) => {
        const STARS = ['💫', '⭐', '🌟', '🌠', '✨', '✴'];
        const CHARS = ['👺', '🤯', '😎', '🤡', '👽', '🤖', '🧟', '🧞'];
        const COCKS = ['🍸', '🍹', '💩', '🍺']

        const star = getRandomItem(STARS);
        const char = getRandomItem(CHARS);
        const cock = getRandomItem(COCKS);

        let text = `${star} Хэллоу ${star}
                            \n До меня дошли слухи, что <b>${userName}</b> ${char} хочет <b>${cockName}</b> ${cock}
                            \nДобудьте мне:`;
        text += '\n — ' + ingredients.join('\n — ');
        return text;
    }

    cocktailsList.forEach(cock => {
        const button = cock.querySelector('.telegram');
        button.addEventListener('click', async (e) => {


            const cockName = cock.querySelector('h3').innerText.replace('×', '').trim();
            const currentUser = getCookie('user');
            let userName = 'некто';

            if (cock.dataset.available === 'True') {
                createToast(`Для коктейля «${cockName}» уже всё есть`, 'info');
                return;
            }

            if (currentUser) {
                userName = document.querySelector(`#users-selector button[data-user-id="${currentUser}"]`).innerText;
            }

            const cockIngredients = Array.from(cock.querySelectorAll('.cocktail-ingredients li')).map(ing => {
                return ing.dataset.ingredientId;
            });

            const unavailableIngredient = [];

            cockIngredients.forEach(ingId => {
                const ingr = document.querySelector(`#ingredients-list li[data-ingredient-id="${ingId}"]`);

                if (ingr && ingr.dataset.available === 'False') {
                    const ingrName = ingr.querySelector('h6').innerText;
                    unavailableIngredient.push(ingrName);
                }
            });


            const text = createMessage(userName, cockName, unavailableIngredient);
            const response = await Request.post({url: `/bar/ingredients/telegram/`, body: {text: text}});

            if (response) {
                createToast('Отправили', 'info');
            }
        })
    })
}

export function removeCocktail(cocktail) {
    const cocktailsList = cocktail ? [cocktail] : document.querySelectorAll('.cocktail');

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
    cocktailsList.forEach(cocktailNode => {
        setupConfirmation(cocktailNode);
    });

    // Возвращаем функцию для ручного удаления (если нужно)
    return {
        remove: removeSingleCocktail
    };
}

// ============== Вспомогательные функции ==============

function setupCustomSelect() {
    const originalSelect = document.querySelector('#ingredient-select');
    const customSelect = document.querySelector('#custom-ingredient-select');
    const customOptions = document.querySelector('#custom-ingredient-options');
    const options = customOptions.querySelectorAll('.custom-select-option');

    // Открытие/закрытие списка
    customSelect.addEventListener('click', function (e) {
        e.stopPropagation();
        customOptions.style.display = customOptions.style.display === 'block' ? 'none' : 'block';
    });

    // Выбор варианта
    options.forEach(option => {
        option.addEventListener('click', function () {
            const value = this.getAttribute('data-value');
            const text = this.textContent;

            // Устанавливаем значение в оригинальный select
            originalSelect.value = value;

            // Обновляем текст в кастомном селекте
            customSelect.textContent = text;

            // Закрываем список
            customOptions.style.display = 'none';

            // Обновляем выделение
            updateSelectedOptions();
        });
    });

    // Закрытие при клике вне списка
    document.addEventListener('click', function () {
        customOptions.style.display = 'none';
    });

    // Функция для обновления выделения выбранных ингредиентов
    function updateSelectedOptions() {
        options.forEach(option => {
            option.classList.remove('selected');
            const ingredientId = option.getAttribute('data-value');
            if (selectedIngredients.some(ing => ing.ingredient_id === ingredientId)) {
                option.classList.add('selected');
            }
        });
    }

    // Обновляем выделение при изменении списка ингредиентов
    const observer = new MutationObserver(updateSelectedOptions);
    observer.observe(document.querySelector('#selected-ingredients-list'), {
        childList: true,
        subtree: true
    });
}

function setupFormToggle() {
    const addButton = document.querySelector('#cocktails .add');
    const formContainer = document.querySelector('#new-cocktail-form');
    const cancelButton = formContainer.querySelector('.close-btn');

    addButton.addEventListener('click', () => {
        // resetForm();
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
        if (!file) {
            return;
        }

        if (file.name === 'default.png') {
            createToast('Недопустимое название файла: default.png', 'error');
            imageCorrect = false;
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            imagePreview.src = e.target.result;
            imagePreview.classList.remove('hide');
            uploadLabel.style.display = 'none';
        };
        reader.readAsDataURL(file);

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
        const unitDisplay = unitSelect.options[unitSelect.selectedIndex].text;

        if (!amount || isNaN(amount)) {
            createToast('Укажите количество', 'error');
            return;
        }

        // Обновляем или добавляем ингредиент
        const existingIndex = selectedIngredients.findIndex(ing => ing.ingredient_id === ingredientId);
        if (existingIndex >= 0) {
            selectedIngredients[existingIndex] = {
                ingredient_id: ingredientId,
                name: ingredientName,
                amount,
                unit,
                unitDisplay
            };
        } else {
            selectedIngredients.push({ingredient_id: ingredientId, name: ingredientName, amount, unit, unitDisplay});
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
    // Заполняем форму и отправляем

    const form = document.querySelector('#cocktail-form');
    const nameInput = document.querySelector('#cocktail-name');
    const isEditMode = !!currentCocktailId;

    const cocktailName = capitalise(nameInput.value);
    nameInput.value = cocktailName;
    const formData = new FormData(form);


    // Проверяем наличие ингредиентов
    if (selectedIngredients.length < 3) {
        createToast('Коктейль - это хотя бы 3 ингредиента!', 'error');
        return;
    }


    // Проверяем, что такого названия коктейля больше нет`
    const existingCocktails = Array.from(document.querySelectorAll('.cocktail'))
        .filter(c => c.dataset.cocktailId !== currentCocktailId)
    const sameNameCocktails = existingCocktails.filter(c => {
        const rawName = c.querySelector('h3').innerText.replace('×', '').trim();
        return capitalise(rawName) === cocktailName;
    });

    if (sameNameCocktails.length > 0) {
        createToast('Коктейль уже существует!', 'error');
        return;
    }

    // Добавляем ингредиенты в FormData
    const ingredientsData = selectedIngredients.map(ing => ({
        ingredient: parseInt(ing.ingredient_id),
        amount: parseInt(ing.amount),
        unit: ing.unit
    }));
    formData.append('ingredients', JSON.stringify(ingredientsData));


    // Передаём картинку отдельно, при обновлении коктейля
    const previewImg = document.querySelector('#cocktail-image-preview').src;
    const cocktailImg = document.querySelector('#cocktail-image').value;
    if (!cocktailImg && previewImg.split('/').at(-1).includes('.')) {
        const response = await fetch(previewImg);
        const blob = await response.blob();
        let filename = previewImg.split('/').pop();

        if (filename === 'default.png') {
            filename = 'preview_default.png';
        }

        // Создаем файл и добавляем в FormData
        const file = new File([blob], filename, {type: blob.type});
        formData.set('image', file);

    }

    try {
        const response = await Request.send({
            method: isEditMode ? 'PUT' : 'POST',
            url: isEditMode ? `/bar/cocktails/${currentCocktailId}/` : '/bar/cocktails/',
            body: formData
        });


        if (response) {
            refreshCocktailNode(response);
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


    // Заполняем ингредиенты
    selectedIngredients = Array.from(cocktailNode.querySelectorAll('.cocktail-ingredients li')).map(ing => ({
        ingredient_id: ing.dataset.ingredientId,
        name: ing.querySelector('span:nth-child(1)').textContent.trim(),
        amount: ing.querySelector('span:nth-child(2) b').textContent.trim(),
        unitDisplay: ing.querySelector('span:nth-child(3)').textContent.trim(),
        unit: UNIT_MAP[ing.querySelector('span:nth-child(3)').textContent.trim()]
    }));

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
            ${ing.name} - ${ing.amount} ${ing.unitDisplay}
            <button type="button" class="remove-ingredient" data-id="${ing.ingredient_id}">×</button>
        </li>
    `).join('');

    // Обновляем выделение в кастомном селекте
    const options = document.querySelectorAll('.custom-select-option');
    options.forEach(option => {
        option.classList.remove('selected');
        const ingredientId = option.getAttribute('data-value');
        if (selectedIngredients.some(ing => ing.ingredient_id === ingredientId)) {
            option.classList.add('selected');
        }
    });
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
    // document.querySelector('#cocktails .add').textContent = '+ добавить';
    formContainer.classList.add('hide');
}

function refreshCocktailNode(cocktailData) {

    let cocktailNode = document.querySelector(`.cocktail[data-cocktail-id="${cocktailData.id}"]`);
    const isCreating = !cocktailNode;


    if (isCreating) {
        cocktailNode = document.createElement('li');
        cocktailNode.className = 'cocktail';
        cocktailNode.dataset.cocktailId = cocktailData.id;
    }

    cocktailNode.dataset.available = cocktailData.is_available ? 'True' : 'False';

    cocktailNode.innerHTML = `
        <img src="${cocktailData.image || '/static/img/bar/cocktail.png'}" alt="${cocktailData.name}">
        <div class="description">
        <div class="confirmation container-fluid center">
            <h4>Удалить коктейль?</h4>
            <button class="confirm-yes">Да</button>
            <button class="confirm-no">Нет</button>
        </div>
            <h3>
                <img src="/static/img/bar/pencil.png" class="update">
                <img src="/static/img/bar/telegram.png" class="telegram">
                ${capitalise(cocktailData.name)}
                <span class="remove">×</span>
            </h3>
            <ul class="cocktail-ingredients">
                ${cocktailData.ingredients.map(ing => `
                    <li data-ingredient-id="${ing.ingredient.id}">
                        <span>${ing.ingredient.name}</span>
                        <span><b>${ing.amount}</b></span>
                        <span>${ing.unit_display}</span>
                    </li>
                `).join('')}
            </ul>
        </div>
        <p class="instruction">${cocktailData.instructions}</p>
    `;

    if (isCreating) {
        const cocktailsList = document.querySelector('#cocktails-list');
        cocktailsList.prepend(cocktailNode);
    }

    telegramRequest(cocktailNode);
    updateCocktail(cocktailNode);
    removeCocktail(cocktailNode);
}
