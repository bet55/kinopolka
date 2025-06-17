import {createToast} from "./create_toast.js";

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

    static async send({method, url, body = null, headers = {}, showToast = true}) {

        const EMO = ['ﮩ٨ـﮩﮩ٨ـ🫀ﮩ٨ـﮩﮩ٨ـ', '🦋ꦿ', '🍆🍑🍆💦🥛CUM', '🥛𓂺', '𝖓𝖎𝖌𝖌𝖆 ♱', '𓃵', '୧⍤⃝💐', '🦊', '🐲', 'ඞ'];
        const successEmo = '🌟';
        const errorEmo = '☠';

        method = method.toUpperCase()

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

        try {
            const response = await fetch(url, requestOptions);
            let responseData = {};
            // Пытаемся распарсить JSON
            if (response.status !== 204) {
                try {
                    responseData = await response.json();
                } catch (e) {
                    responseData = {};
                    createToast('Ошибка чтения ответа', 'error');
                    console.error(`parse json: ${e}`)
                    showToast = false;
                }
            }


            // Ошибка HTTP (4xx, 5xx)
            if (!response.ok) {
                const networkErrorText = await response.text();
                const serverErrorText = responseData?.error;
                const errorText = serverErrorText ? serverErrorText : networkErrorText;
                createToast(`Ошибка сервера: ${response.status} ${errorText}`, 'error');
                console.error(`${method} ${url} failed: ${response.status}\n${errorText}`);
                return null;
            }


            // Ошибка логики приложения (success: false)
            if (responseData && responseData.success === false) {
                const errorMsg = responseData.error || 'Неизвестная ошибка';
                createToast(`Ошибка: ${errorMsg}`, 'error');
                console.error(`API error: ${errorMsg}`);
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