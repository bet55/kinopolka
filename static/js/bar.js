import { Request } from "./request.js";

// Функция для добавления коктейля
async function addCocktail({ name, instructions, ingredientIds, imageFile, token = null }) {
    const formData = new FormData();
    formData.append("name", name);
    formData.append("instructions", instructions);
    formData.append("ingredients", JSON.stringify(ingredientIds)); // Отправляем массив ID как строку
    if (imageFile) {
        formData.append("image", imageFile);
    }

    const headers = {};
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await Request.post({
        url: "/bar/cocktails/",
        body: formData,
        headers,
        showToast: true
    });

    if (response) {
        console.log("Коктейль успешно добавлен:", response);
        return response;
    } else {
        console.error("Не удалось добавить коктейль");
        return null;
    }
}

// Функция для добавления ингредиента
async function addIngredient({ name, token = null }) {
    const headers = {};
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await Request.post({
        url: "/bar/ingredients/",
        body: { name },
        headers,
        showToast: true
    });

    if (response) {
        console.log("Ингредиент успешно добавлен:", response);
        return response;
    } else {
        console.error("Не удалось добавить ингредиент");
        return null;
    }
}

// Пример использования
async function example() {
    // Пример добавления ингредиента
    const ingredient = await addIngredient({
        name: "Mint",
        token: "your_token_here" // Замените на реальный токен или удалите, если авторизация не требуется
    });

    // Пример добавления коктейля
    const imageFile = document.querySelector("#cocktailImageInput")?.files[0]; // Предполагается, что файл выбран через <input type="file" id="cocktailImageInput">
    const cocktail = await addCocktail({
        name: "Mojito",
        instructions: "Mix mint, lime, and rum",
        ingredientIds: [1, 2], // ID ингредиентов
        imageFile,
        token: "your_token_here" // Замените на реальный токен или удалите
    });
}

// Выполнение примера (раскомментируйте для запуска)
// example();

export { addCocktail, addIngredient };