import {cartHandler} from "./postcard/movies_cart.js";
import {savePostcard} from "./postcard/save_postcard.js";
import {createPostcard} from "./postcard/create_postcard.js";
import {confirmAndSend} from "./postcard/send_postcard_invitation.js";



cartHandler(); // обработка работы с корзиной
await savePostcard(); // сохранение открытки
await createPostcard(); // создание новой открытки
await confirmAndSend(); // отправка открытки пользователям
