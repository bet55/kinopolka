import {createToast} from "./create_toast.js";

// Общий метод отправки запросов

class Request {


    static async send({method, url, body = null, headers = {}, showToast = true}) {

        const EMO = ['ﮩ٨ـﮩﮩ٨ـ🫀ﮩ٨ـﮩﮩ٨ـ', '🦋ꦿ', '🍆🍑🍆💦🥛CUM', '🥛𓂺', '𝖓𝖎𝖌𝖌𝖆 ♱', '𓃵', '୧⍤⃝💐', '🦊', '🐲', 'ඞ'];
        const successEmo = '🌟';
        const errorEmo = '☠';

        const requestOptions = {
            method: method.toUpperCase(),
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

            // Ошибка HTTP (4xx, 5xx)
            if (!response.ok) {
                const errorText = await response.text();
                createToast(`Ошибка сервера: ${response.status} ${response.statusText}`, 'error');
                console.error(`${method} ${url} failed: ${response.status}\n${errorText}`);
                return null;
            }

            // Пытаемся распарсить JSON, даже если ответ 204 No Content
            let responseData;
            try {
                responseData = await response.json();
            } catch (e) {
                // Пустой ответ - это не обязательно ошибка
                return {};
            }


            // Ошибка логики приложения (success: false)
            if (responseData && responseData.success === false) {
                const errorMsg = responseData.error || 'Неизвестная ошибка';
                createToast(`Ошибка: ${errorMsg}`, 'error');
                console.error(`API error: ${errorMsg}`);
                return null;
            }

            if (showToast) {
                createToast(`Успешно!`, 'success');
            }

            return responseData?.data ?? responseData;

        } catch (e) {
            // Ошибка сети или другая непредвиденная ошибка
            createToast('Не удалось выполнить запрос', 'error');
            console.error(`Request failed: ${e}`);
            return null;
        }

    }
}

export {Request}