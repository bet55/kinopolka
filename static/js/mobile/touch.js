// Мобильные JavaScript функции для улучшения взаимодействия

document.addEventListener('DOMContentLoaded', function() {
    
    // Определяем мобильное устройство
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        initMobileFeatures();
    }
    
    // Слушаем изменение размера окна
    window.addEventListener('resize', function() {
        const newIsMobile = window.innerWidth <= 768;
        if (newIsMobile !== isMobile) {
            location.reload(); // Перезагружаем страницу при изменении ориентации
        }
    });
});

function initMobileFeatures() {
    
    // Инициализация мобильной навигации
    initMobileNavigation();
    
    // Инициализация свайпов
    initSwipeGestures();
    
    // Улучшение модальных окон
    enhanceMobileModals();
    
    // Улучшение форм
    enhanceMobileForms();
    
    // Улучшение скролла
    enhanceMobileScroll();
    
    // Улучшение касаний
    enhanceTouchInteractions();
    
    // Показ индикатора свайпа
    showSwipeIndicator();
}

function initMobileNavigation() {
    const navTrigger = document.getElementById('mobile-nav-trigger');
    const navDropdown = document.getElementById('mobile-nav-dropdown');
    
    if (navTrigger && navDropdown) {
        // Переключение выпадающего меню
        navTrigger.addEventListener('click', function(e) {
            e.preventDefault();
            navDropdown.classList.toggle('show');
        });
        
        // Закрытие меню при клике вне его
        document.addEventListener('click', function(e) {
            if (!navTrigger.contains(e.target) && !navDropdown.contains(e.target)) {
                navDropdown.classList.remove('show');
            }
        });
        
        // Закрытие меню при переходе по ссылке
        const navLinks = navDropdown.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navDropdown.classList.remove('show');
            });
        });
    }
}

function initSwipeGestures() {
    const container = document.querySelector('.second-row');
    const rightPanel = document.querySelector('.col-md-3:last-child');
    const centerPanel = document.querySelector('.col-md-6');
    const backButton = document.getElementById('mobile-back-button');
    
    if (!container || !rightPanel || !centerPanel) return;
    
    let startX = 0;
    let startY = 0;
    let currentX = 0;
    let currentY = 0;
    let isSwiping = false;
    let rightPanelActive = false;
    
    // Обработка начала касания
    container.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
        isSwiping = false;
    });
    
    // Обработка движения
    container.addEventListener('touchmove', function(e) {
        if (!isSwiping) {
            currentX = e.touches[0].clientX;
            currentY = e.touches[0].clientY;
            
            const deltaX = Math.abs(currentX - startX);
            const deltaY = Math.abs(currentY - startY);
            
            // Определяем направление свайпа
            if (deltaX > deltaY && deltaX > 10) {
                isSwiping = true;
                e.preventDefault();
            }
        }
        
        if (isSwiping) {
            const deltaX = currentX - startX;
            
            // Ограничиваем свайп
            if (deltaX > 0 && !rightPanelActive) {
                // Свайп вправо - показываем правую панель
                const translateX = Math.min(deltaX * 0.3, 100);
                centerPanel.style.transform = `translateX(-${translateX}%)`;
                rightPanel.style.right = `-${100 - translateX}%`;
            } else if (deltaX < 0 && rightPanelActive) {
                // Свайп влево - скрываем правую панель
                const translateX = Math.min(Math.abs(deltaX) * 0.3, 100);
                centerPanel.style.transform = `translateX(-${100 - translateX}%)`;
                rightPanel.style.right = `-${translateX}%`;
            }
        }
    });
    
    // Обработка окончания касания
    container.addEventListener('touchend', function(e) {
        if (isSwiping) {
            const deltaX = currentX - startX;
            
            if (deltaX > 50 && !rightPanelActive) {
                // Активируем правую панель
                activateRightPanel();
            } else if (deltaX < -50 && rightPanelActive) {
                // Деактивируем правую панель
                deactivateRightPanel();
            } else {
                // Возвращаем в исходное состояние
                resetPanels();
            }
        }
        
        isSwiping = false;
    });
    
    // Функция активации правой панели
    function activateRightPanel() {
        container.classList.add('right-panel-active');
        rightPanelActive = true;
        if (backButton) backButton.style.display = 'block';
        hideSwipeIndicator();
    }
    
    // Функция деактивации правой панели
    function deactivateRightPanel() {
        container.classList.remove('right-panel-active');
        rightPanelActive = false;
        if (backButton) backButton.style.display = 'none';
        showSwipeIndicator();
    }
    
    // Функция сброса панелей
    function resetPanels() {
        centerPanel.style.transform = '';
        rightPanel.style.right = '';
    }
    
    // Обработка кнопки возврата
    if (backButton) {
        backButton.addEventListener('click', function() {
            deactivateRightPanel();
        });
    }
    
    // Обработка свайпа влево для закрытия правой панели
    rightPanel.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
    });
    
    rightPanel.addEventListener('touchmove', function(e) {
        if (rightPanelActive) {
            currentX = e.touches[0].clientX;
            const deltaX = currentX - startX;
            
            if (deltaX < -10) {
                e.preventDefault();
                const translateX = Math.min(Math.abs(deltaX) * 0.3, 100);
                centerPanel.style.transform = `translateX(-${100 - translateX}%)`;
                rightPanel.style.right = `-${translateX}%`;
            }
        }
    });
    
    rightPanel.addEventListener('touchend', function(e) {
        if (rightPanelActive) {
            const deltaX = currentX - startX;
            if (deltaX < -50) {
                deactivateRightPanel();
            } else {
                resetPanels();
            }
        }
    });
}

function showSwipeIndicator() {
    // Создаем индикатор свайпа, если его нет
    let indicator = document.querySelector('.swipe-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'swipe-indicator';
        indicator.textContent = '← Свайп вправо';
        document.body.appendChild(indicator);
    }
    
    // Показываем индикатор через 2 секунды после загрузки
    setTimeout(() => {
        indicator.classList.remove('hide');
    }, 2000);
    
    // Скрываем через 5 секунд
    setTimeout(() => {
        indicator.classList.add('hide');
    }, 7000);
}

function hideSwipeIndicator() {
    const indicator = document.querySelector('.swipe-indicator');
    if (indicator) {
        indicator.classList.add('hide');
    }
}

function enhanceMobileModals() {
    // Улучшаем модальные окна для мобильных
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        // Добавляем возможность закрытия по свайпу
        let startY = 0;
        let currentY = 0;
        
        modal.addEventListener('touchstart', function(e) {
            startY = e.touches[0].clientY;
        });
        
        modal.addEventListener('touchmove', function(e) {
            currentY = e.touches[0].clientY;
            const diff = startY - currentY;
            
            if (diff > 50) { // Свайп вверх
                const modalDialog = this.querySelector('.modal-dialog');
                modalDialog.style.transform = `translateY(-${diff}px)`;
            }
        });
        
        modal.addEventListener('touchend', function() {
            const modalDialog = this.querySelector('.modal-dialog');
            const diff = startY - currentY;
            
            if (diff > 100) { // Если свайп достаточно большой
                // Закрываем модальное окно
                const closeButton = this.querySelector('[data-bs-dismiss="modal"]');
                if (closeButton) {
                    closeButton.click();
                }
            }
            
            modalDialog.style.transform = '';
        });
    });
}

function enhanceMobileForms() {
    // Улучшаем формы для мобильных устройств
    const inputs = document.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        // Добавляем фокус для лучшего UX
        input.addEventListener('focus', function() {
            this.style.borderColor = 'var(--red-color)';
            this.style.boxShadow = '0 0 0 2px rgba(220, 53, 69, 0.25)';
        });
        
        input.addEventListener('blur', function() {
            this.style.borderColor = '';
            this.style.boxShadow = '';
        });
        
        // Предотвращаем зум на iOS
        if (input.type === 'text' || input.type === 'email' || input.type === 'password') {
            input.style.fontSize = '16px';
        }
    });
}

function enhanceMobileScroll() {
    // Улучшаем скролл для мобильных устройств
    const scrollableElements = document.querySelectorAll('.posters-grid, .postcards-grid, .cocktails-grid, .ingredients-grid');
    
    scrollableElements.forEach(element => {
        // Добавляем плавный скролл
        element.style.scrollBehavior = 'smooth';
        
        // Добавляем индикатор скролла
        element.addEventListener('scroll', function() {
            const scrollTop = this.scrollTop;
            const scrollHeight = this.scrollHeight;
            const clientHeight = this.clientHeight;
            
            if (scrollTop + clientHeight >= scrollHeight - 10) {
                // Пользователь достиг конца списка
                this.style.borderBottom = '2px solid var(--red-color)';
            } else {
                this.style.borderBottom = '';
            }
        });
    });
}

function enhanceTouchInteractions() {
    // Улучшаем взаимодействие с карточками
    const cards = document.querySelectorAll('.poster-container, .postcard-item, .cocktail-card, .ingredient-card');
    
    cards.forEach(card => {
        let touchStartTime = 0;
        let touchEndTime = 0;
        
        card.addEventListener('touchstart', function() {
            touchStartTime = new Date().getTime();
            this.style.transform = 'scale(0.98)';
        });
        
        card.addEventListener('touchend', function() {
            touchEndTime = new Date().getTime();
            const touchDuration = touchEndTime - touchStartTime;
            
            this.style.transform = '';
            
            // Если касание было коротким, считаем это кликом
            if (touchDuration < 200) {
                const clickableElement = this.querySelector('a, button, [onclick]');
                if (clickableElement) {
                    clickableElement.click();
                }
            }
        });
    });
}

// Функция для определения ориентации устройства
function getOrientation() {
    return window.innerWidth > window.innerHeight ? 'landscape' : 'portrait';
}

// Функция для адаптации контента под ориентацию
function adaptToOrientation() {
    const orientation = getOrientation();
    const body = document.body;
    
    if (orientation === 'landscape') {
        body.classList.add('landscape-mode');
        body.classList.remove('portrait-mode');
    } else {
        body.classList.add('portrait-mode');
        body.classList.remove('landscape-mode');
    }
}

// Слушаем изменение ориентации
window.addEventListener('orientationchange', function() {
    setTimeout(adaptToOrientation, 100);
});

// Инициализируем адаптацию при загрузке
document.addEventListener('DOMContentLoaded', adaptToOrientation); 