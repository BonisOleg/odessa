/* ==========================================================================
   Main JavaScript - CRM Nice
   ========================================================================== */

(function () {
    'use strict';

    // ==========================================================================
    // bfcache (Back/Forward Cache) Support
    // ==========================================================================

    window.addEventListener('pageshow', function (event) {
        if (event.persisted) {
            // Сторінка відновлена з bfcache
            // Примусово знімаємо лоадери або активуємо кнопки
            document.body.classList.remove('is-loading');
            // Перезапускаємо ініціалізацію компонентів
            updateTopbarActiveState();
        }
    });

    // ==========================================================================
    // HTMX CSRF Configuration
    // ==========================================================================

    document.body.addEventListener('htmx:configRequest', function (event) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            event.detail.headers['X-CSRFToken'] = csrfToken.value;
        } else {
            // Альтернативний спосіб - з cookie
            const cookieValue = document.cookie
                .split('; ')
                .find(function (row) { return row.startsWith('csrftoken='); });
            if (cookieValue) {
                event.detail.headers['X-CSRFToken'] = cookieValue.split('=')[1];
            }
        }
    });

    // ==========================================================================
    // Topbar Active State Management
    // ==========================================================================

    function updateTopbarActiveState() {
        const currentPath = window.location.pathname;

        // Видалити активний стан з усіх посилань
        document.querySelectorAll('.topbar__nav-link').forEach(function (link) {
            link.classList.remove('topbar__nav-link--active', 'active');
        });

        // Додати активний стан до поточного посилання
        document.querySelectorAll('.topbar__nav-link').forEach(function (link) {
            const linkPath = new URL(link.href).pathname;
            if (currentPath.startsWith(linkPath) && linkPath !== '/') {
                link.classList.add('topbar__nav-link--active', 'active');
            } else if (currentPath === linkPath) {
                link.classList.add('topbar__nav-link--active', 'active');
            }
        });
    }

    // Оновлення активного стану topbar меню після HTMX навігації
    document.body.addEventListener('htmx:afterSwap', updateTopbarActiveState);

    // ==========================================================================
    // Date and Time Update
    // ==========================================================================

    function updateDateTime() {
        const datetimeElement = document.getElementById('current-datetime');
        if (!datetimeElement) return;

        const now = new Date();
        const options = {
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        const formatted = now.toLocaleDateString('ru-RU', options);
        datetimeElement.textContent = formatted;
    }

    // Ініціалізація дати/часу
    updateDateTime();
    setInterval(updateDateTime, 60000); // Оновлювати кожну хвилину

    // ==========================================================================
    // Dropdown Menu
    // ==========================================================================

    document.addEventListener('click', function (event) {
        const trigger = event.target.closest('.dropdown__trigger');
        if (trigger) {
            event.preventDefault();
            event.stopPropagation();

            const dropdown = trigger.closest('.dropdown');
            if (!dropdown) return;

            const isOpen = dropdown.classList.contains('is-open');

            // Закрити всі інші dropdown
            document.querySelectorAll('.dropdown.is-open').forEach(function (openDropdown) {
                if (openDropdown !== dropdown) {
                    openDropdown.classList.remove('is-open');
                }
            });

            // Перемкнути поточний dropdown
            if (isOpen) {
                dropdown.classList.remove('is-open');
            } else {
                dropdown.classList.add('is-open');
            }
        } else {
            // Закрити всі dropdown при кліку поза ними
            if (!event.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown.is-open').forEach(function (dropdown) {
                    dropdown.classList.remove('is-open');
                });
            }
        }
    }, true);

    // ==========================================================================
    // Photo Slider
    // ==========================================================================

    function initPhotoSlider() {
        const sliders = document.querySelectorAll('.photo-slider');
        sliders.forEach(function (slider) {
            const images = slider.querySelectorAll('img');
            const prevBtn = slider.querySelector('.slider-btn--prev');
            const nextBtn = slider.querySelector('.slider-btn--next');
            let currentIndex = 0;

            if (images.length === 0) return;

            function showImage(index) {
                images.forEach(function (img, i) {
                    img.style.display = i === index ? 'block' : 'none';
                });
            }

            if (prevBtn) {
                prevBtn.addEventListener('click', function () {
                    currentIndex = (currentIndex - 1 + images.length) % images.length;
                    showImage(currentIndex);
                });
            }

            if (nextBtn) {
                nextBtn.addEventListener('click', function () {
                    currentIndex = (currentIndex + 1) % images.length;
                    showImage(currentIndex);
                });
            }

            showImage(0);
        });
    }

    // Ініціалізація слайдера при завантаженні та після HTMX
    initPhotoSlider();
    document.body.addEventListener('htmx:afterSwap', initPhotoSlider);

    // ==========================================================================
    // Favorite Companies (localStorage)
    // ==========================================================================

    function initFavorites() {
        const favoriteButtons = document.querySelectorAll('.favorite-btn');

        favoriteButtons.forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const companyId = this.getAttribute('data-id');
                const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
                const index = favorites.indexOf(companyId);

                if (index > -1) {
                    favorites.splice(index, 1);
                    this.classList.remove('icon-btn--active');
                } else {
                    favorites.push(companyId);
                    this.classList.add('icon-btn--active');
                }

                localStorage.setItem('favorites', JSON.stringify(favorites));
                // Пересортувати таблицю
                sortTableByFavorites();
            });
        });

        // Установити активні стани для закріплених
        const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
        favorites.forEach(function (id) {
            const btn = document.querySelector('.favorite-btn[data-id="' + id + '"]');
            if (btn) {
                btn.classList.add('icon-btn--active');
            }
        });
    }

    function sortTableByFavorites() {
        const table = document.querySelector('table');
        if (!table) return;

        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');

        rows.sort(function (a, b) {
            const aId = a.querySelector('.favorite-btn')?.getAttribute('data-id');
            const bId = b.querySelector('.favorite-btn')?.getAttribute('data-id');
            const aFav = favorites.includes(aId) ? 0 : 1;
            const bFav = favorites.includes(bId) ? 0 : 1;
            return aFav - bFav;
        });

        rows.forEach(function (row) {
            tbody.appendChild(row);
        });
    }

    initFavorites();
    document.body.addEventListener('htmx:afterSwap', initFavorites);

    // ==========================================================================
    // Pagination
    // ==========================================================================

    function initPagination() {
        const prevBtn = document.querySelector('.pagination__btn--prev');
        const nextBtn = document.querySelector('.pagination__btn--next');

        if (prevBtn) {
            prevBtn.addEventListener('click', function () {
                if (!this.disabled) {
                    const currentPage = parseInt(document.querySelector('.pagination__info').textContent.match(/\d+/)[0]);
                    if (currentPage > 1) {
                        const newPage = currentPage - 1;
                        updatePagination(newPage);
                    }
                }
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', function () {
                if (!this.disabled) {
                    const currentPage = parseInt(document.querySelector('.pagination__info').textContent.match(/\d+/)[0]);
                    const totalPages = parseInt(document.querySelector('.pagination__info').textContent.match(/\d+/g)[1]);
                    if (currentPage < totalPages) {
                        const newPage = currentPage + 1;
                        updatePagination(newPage);
                    }
                }
            });
        }
    }

    function updatePagination(page) {
        const totalPages = 2;
        const info = document.querySelector('.pagination__info');
        const prevBtn = document.querySelector('.pagination__btn--prev');
        const nextBtn = document.querySelector('.pagination__btn--next');

        if (info) {
            info.textContent = `Страница ${page} из ${totalPages}`;
        }

        if (prevBtn) {
            prevBtn.disabled = page === 1;
        }

        if (nextBtn) {
            nextBtn.disabled = page === totalPages;
        }
    }

    initPagination();
    document.body.addEventListener('htmx:afterSwap', initPagination);

    // ==========================================================================
    // Telegram Notification
    // ==========================================================================

    document.addEventListener('click', function (e) {
        const telegramBtn = e.target.closest('.telegram-btn');
        if (telegramBtn) {
            e.preventDefault();
            const username = telegramBtn.getAttribute('data-telegram');
            alert('💬 Відкрити чат з ' + username + '\n\nПосилання: https://t.me/' + username.replace('@', ''));
        }
    });

    // ==========================================================================
    // Textarea Auto-Resize
    // ==========================================================================

    function autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 300) + 'px';
    }

    document.querySelectorAll('.textarea-auto-resize').forEach(function (textarea) {
        textarea.addEventListener('input', function () {
            autoResizeTextarea(this);
        });
        autoResizeTextarea(textarea);
    });

    // ==========================================================================
    // Form Helpers
    // ==========================================================================

    // Додавання телефонного поля
    document.addEventListener('click', function (event) {
        if (event.target.matches('[data-action="add-phone"]')) {
            event.preventDefault();
            const phoneInputs = event.target.closest('.phone-inputs');
            if (phoneInputs) {
                const newInput = document.createElement('input');
                newInput.type = 'tel';
                newInput.className = 'form-control';
                newInput.name = 'phones[]';
                newInput.placeholder = '+380991234567';
                phoneInputs.insertBefore(newInput, event.target);
            }
        }
    });

    // Видалення тега
    document.addEventListener('click', function (event) {
        if (event.target.matches('[data-action="remove-tag"]')) {
            event.preventDefault();
            const tag = event.target.closest('.tag');
            if (tag) {
                tag.remove();
            }
        }
    });

    // ==========================================================================
    // Modal Windows
    // ==========================================================================

    // Закриття модального вікна
    function closeModal(modal) {
        if (modal) {
            modal.classList.remove('is-open');
            document.body.style.overflow = '';
        }
    }

    // Відкриття модального вікна
    function openModal(modal) {
        if (modal) {
            modal.classList.add('is-open');
            document.body.style.overflow = 'hidden';
        }
    }

    // Обробка кліку для закриття модального вікна
    document.addEventListener('click', function (event) {
        if (event.target.matches('[data-action="close-modal"]')) {
            event.preventDefault();
            const modal = event.target.closest('.modal');
            closeModal(modal);
        }
    });

    // Закриття по ESC
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            const openModal = document.querySelector('.modal.is-open');
            if (openModal) {
                closeModal(openModal);
            }
        }
    });

    // Відкриття модального вікна після HTMX завантаження
    document.body.addEventListener('htmx:afterSwap', function (event) {
        const modal = event.detail.target.querySelector('.modal');
        if (modal) {
            openModal(modal);
        }
    });

    // Відкриття модального вікна при додаванні в body
    const observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            mutation.addedNodes.forEach(function (node) {
                if (node.nodeType === 1 && node.classList && node.classList.contains('modal')) {
                    openModal(node);
                }
            });
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    // ==========================================================================
    // Comment Deletion
    // ==========================================================================

    document.addEventListener('click', function (e) {
        if (e.target.closest('.btn-delete-comment')) {
            e.preventDefault();
            const comment = e.target.closest('.comment');
            if (confirm('Видалити коментарій?')) {
                comment.remove();
            }
        }
    });

    // ==========================================================================
    // Call Date Editing
    // ==========================================================================

    function initCallDateEditor() {
        const editBtns = document.querySelectorAll('.btn-edit-date');
        editBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                const display = this.closest('.call-date-display');
                const input = this.closest('.call-date-card').querySelector('.call-date-input');

                if (!input) return;

                display.style.display = 'none';
                input.classList.add('is-visible');
                input.focus();

                function saveDate() {
                    const date = new Date(input.value);
                    const formatted = ('0' + date.getDate()).slice(-2) + '.' +
                        ('0' + (date.getMonth() + 1)).slice(-2) + '.' +
                        date.getFullYear();

                    const valueSpan = display.querySelector('.call-date-value');
                    valueSpan.textContent = formatted;
                    display.style.display = 'flex';
                    input.classList.remove('is-visible');
                }

                input.addEventListener('change', saveDate);
                input.addEventListener('blur', saveDate);
            });
        });
    }

    initCallDateEditor();
    document.body.addEventListener('htmx:afterSwap', initCallDateEditor);

    // ==========================================================================
    // Company Detail Page - Expand Comments
    // ==========================================================================

    function initExpandComments() {
        const expandBtn = document.querySelector('.btn-expand-comments');
        if (expandBtn) {
            const hiddenComments = document.querySelectorAll('.comment--hidden');
            if (hiddenComments.length === 0) {
                expandBtn.classList.add('is-hidden');
            }

            expandBtn.addEventListener('click', function () {
                hiddenComments.forEach(function (c) {
                    c.classList.remove('comment--hidden');
                });
                this.classList.add('is-hidden');
            });
        }
    }

    initExpandComments();
    document.body.addEventListener('htmx:afterSwap', initExpandComments);

})();
