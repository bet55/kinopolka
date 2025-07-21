import {createIngredient, updateIngredient, removeIngredient} from "./bar/ingredients.js";
import {createCocktail, updateCocktail, removeCocktail} from "./bar/cocktails.js";

document.addEventListener('DOMContentLoaded', () => {
    createCocktail();
    updateCocktail();
    removeCocktail();

    createIngredient();
    updateIngredient();
    removeIngredient();
});