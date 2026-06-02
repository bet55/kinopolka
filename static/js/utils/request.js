import {createToast} from "./create_toast.js";
import {getCookie} from "./cookie.js";

// Общий метод отправки запросов

class Request {

    static async get({url, body = null, headers = {}, showToast = true}) {
        return await Request.send({method: 'get', url: url, body: body, headers: headers, showToast: showToast})
    }

    static async post({url, body = null, headers = {}, showToast = true}) {
        return await Request.send({method: 'post', url: url, body: body, headers: headers, showToast: showToast})
    }

    static async delete({url, body = null, headers = {}, showToast = true}) {
        return await Request.send({method: 'delete', url: url, body: body, headers: headers, showToast: showToast})
    }

    static async put({url, body = null, headers = {}, showToast = true}) {
        return await Request.send({method: 'put', url: url, body: body, headers: headers, showToast: showToast})
    }

    static async patch({url, body = null, headers = {}, showToast = true}) {
        return await Request.send({method: 'patch', url: url, body: body, headers: headers, showToast: showToast})
    }

    static _permissionsIsAllowed(method) {
        if(method === 'GET') {
            return true;
        }
        const user = getCookie('user');
        console.log(user);
        return !!user;
    }

    static _prepareRequest(method, headers, body) {
        const requestOptions = {
            method: method,
            headers: {
                'Accept': 'application/json',
                ...headers
            },
            body: body,
            redirect: "follow"
        };

        // Добавляем тело только для методов, которые его поддерживают
        if (body && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(requestOptions.method)) {

            if (body instanceof FormData) {
                requestOptions.body = body;
            } else {
                requestOptions.body = JSON.stringify(body);
                requestOptions.headers['Content-Type'] = 'application/json';
            }

        }
        return requestOptions;
    }

    static async send({method, url, body = null, headers = {}, showToast = true}) {

        const EMO = ['ﮩ٨ـﮩﮩ٨ـ🫀ﮩ٨ـﮩﮩ٨ـ', '🦋ꦿ', '🍆🍑🍆💦🥛CUM', '🥛𓂺', '𝖓𝖎𝖌𝖌𝖆 ♱', '𓃵', '୧⍤⃝💐', '🦊', '🐲', 'ඞ'];
        const successEmo = '🌟';
        const errorEmo = '☠';

        method = method.toUpperCase();

        if(!Request._permissionsIsAllowed(method)) {
            createToast('Только пользователи могут это сделать', 'error');
            return null;
        }

        const requestOptions = Request._prepareRequest(method, headers, body);

        try {
            const response = await fetch(url, requestOptions);

            // Читаем тело один раз, потом пробуем распарсить как JSON
            const rawText = await response.text();
            let responseData = {};
            let responseEmpty = true;
            try {
                responseData = JSON.parse(rawText);
                responseEmpty = false;
            } catch (e) {
                console.warn('Не распарсился ответ: ', e);
            }

            // Ошибка HTTP (4xx, 5xx)
            if (!response.ok) {
                const status = response.status;
                let errorText;
                let toastText = '';
                let logText = '';

                if (responseEmpty) {
                    errorText = rawText || 'беда!';
                    toastText = `Ошибка сервера: ${status} ${errorText}`;
                    logText = `server ${method} ${url} failed: ${status}\n${errorText}`;
                } else {
                    errorText = responseData.error ?? 'Неизвестная ошибка';
                    toastText = `Ошибка запроса: ${errorText}`;
                    logText = `api ${method} ${url} failed: ${status}\n${errorText}`;
                }

                createToast(toastText, 'error');
                console.error(logText);
                return null;
            }

            // Уведомление об успехе
            if (showToast) {
                createToast(`Успешно!`, 'success');
            }

            return responseData?.data ?? responseData;

        } catch (e) {
            // Ошибка сети или другая непредвиденная ошибка
            createToast('Не удалось выполнить запрос', 'error');
            console.error(`Request failed`);
            console.error(e);
            return null;
        }

    }
}

export {Request}