import {createIngredient, updateIngredient, removeIngredient} from "./bar/ingredients.js";
import {createCocktail, updateCocktail, removeCocktail, telegramRequest} from "./bar/cocktails.js";

document.addEventListener('DOMContentLoaded', () => {
    createCocktail();
    updateCocktail();
    removeCocktail();

    telegramRequest();

    createIngredient();
    updateIngredient();
    removeIngredient();
});