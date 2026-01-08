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
    // HTMX Loading States
    // ==========================================================================

    document.body.addEventListener('htmx:beforeRequest', function (event) {
        const target = event.detail.target;
        if (target) {
            target.classList.add('is-loading');
            target.style.opacity = '0.6';
            target.style.pointerEvents = 'none';
        }
    });

    document.body.addEventListener('htmx:afterRequest', function (event) {
        const target = event.detail.target;
        if (target) {
            target.classList.remove('is-loading');
            target.style.opacity = '';
            target.style.pointerEvents = '';
        }
    });

    document.body.addEventListener('htmx:responseError', function (event) {
        const target = event.detail.target;
        if (target) {
            target.classList.remove('is-loading');
            target.style.opacity = '';
            target.style.pointerEvents = '';
        }
    });

    // ==========================================================================
    // HTMX Error Handling
    // ==========================================================================

    document.body.addEventListener('htmx:responseError', function (event) {
        console.error('HTMX Error:', event.detail);
        const target = event.detail.target;
        if (target) {
            const errorMsg = document.createElement('div');
            errorMsg.className = 'message message--error';
            errorMsg.innerHTML = '<div class="message__text">Помилка завантаження. Спробуйте ще раз.</div>';
            target.insertBefore(errorMsg, target.firstChild);
        }
    });

    document.body.addEventListener('htmx:sendError', function (event) {
        console.error('HTMX Send Error:', event.detail);
        const target = event.detail.target;
        if (target) {
            const errorMsg = document.createElement('div');
            errorMsg.className = 'message message--error';
            errorMsg.innerHTML = '<div class="message__text">Помилка відправки запиту. Перевірте з\'єднання.</div>';
            target.insertBefore(errorMsg, target.firstChild);
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
    // Favorite Companies (Server-side with HTMX)
    // ==========================================================================

    function initFavorites() {
        const favoriteButtons = document.querySelectorAll('.favorite-btn');

        favoriteButtons.forEach(function (btn) {
            // Обробляємо успішне завантаження HTMX запиту
            btn.addEventListener('htmx:afterRequest', function(event) {
                if (event.detail.successful) {
                    // Перекидаємо запит для перезавантаження списку
                    setTimeout(function() {
                        htmx.ajax('GET', window.location.pathname, {target: '#main-content'});
                    }, 300);
                }
            });
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

    // ==========================================================================
    // City Search Filter
    // ==========================================================================

    function initCitySearch() {
        const searchInputs = document.querySelectorAll('.city-search-input');
        searchInputs.forEach(function(searchInput) {
            searchInput.addEventListener('input', function() {
                const query = this.value.toLowerCase();
                const optionsContainer = this.closest('.multiselect-options');
                if (!optionsContainer) return;
                
                const options = optionsContainer.querySelectorAll('.multiselect-option');
                options.forEach(function(option) {
                    const cityName = option.getAttribute('data-city-name') || option.textContent.toLowerCase();
                    const shouldShow = cityName.includes(query);
                    option.style.display = shouldShow ? '' : 'none';
                });
            });
        });
    }

    initCitySearch();
    document.body.addEventListener('htmx:afterSwap', initCitySearch);

    // Додавання адреси
    document.addEventListener('click', function (event) {
        if (event.target.matches('[data-action="add-address"]')) {
            event.preventDefault();
            const addressList = document.getElementById('address-list');
            if (addressList) {
                const index = addressList.querySelectorAll('.address-input-group').length;
                const newAddressGroup = document.createElement('div');
                newAddressGroup.className = 'address-input-group';
                newAddressGroup.style.cssText = 'display: flex; gap: var(--spacing-xs); align-items: center; margin-bottom: var(--spacing-xs);';
                newAddressGroup.innerHTML = `
                    <input type="text" class="form-control" name="addresses[]" placeholder="Введіть адресу">
                    <label class="address-favorite" style="display: flex; align-items: center; cursor: pointer;">
                        <input type="radio" name="favorite_address" value="${index}">
                        <span class="favorite-star">⭐</span>
                    </label>
                    <button type="button" class="button button--sm button--danger remove-address">−</button>
                `;
                addressList.appendChild(newAddressGroup);
            }
        }
        
        // Видалення адреси
        if (event.target.matches('.remove-address') || event.target.closest('.remove-address')) {
            event.preventDefault();
            const addressGroup = event.target.closest('.address-input-group');
            if (addressGroup) {
                const allAddresses = document.querySelectorAll('.address-input-group');
                if (allAddresses.length > 1) {
                    addressGroup.remove();
                } else {
                    alert('Має бути хоча б одна адреса');
                }
            }
        }
    });

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
        
        // Видалення телефону
        if (event.target.matches('.remove-phone') || event.target.closest('.remove-phone')) {
            event.preventDefault();
            const phoneGroup = event.target.closest('.phone-input-group');
            if (phoneGroup) {
                const allPhones = document.querySelectorAll('.phone-input-group');
                if (allPhones.length > 1) {
                    phoneGroup.remove();
                } else {
                    alert('Має бути хоча б один телефон');
                }
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

            // Видаляємо модальне з DOM після анімації закриття
            setTimeout(function () {
                if (modal.parentNode) {
                    modal.parentNode.removeChild(modal);
                }
            }, 300); // 300ms - час анімації fadeOut
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
            const openModalEl = document.querySelector('.modal.is-open');
            if (openModalEl) {
                closeModal(openModalEl);
            }
        }
    });

    // Відкриття модального вікна після HTMX завантаження
    document.body.addEventListener('htmx:afterSwap', function (event) {
        // Якщо завантажено модальне вікно
        const modal = event.detail.target.querySelector('.modal');
        if (modal) {
            openModal(modal);
        }
        // Якщо оновлено #main-content (успішний submit), закриваємо та ВИДАЛЯЄМО всі модальні вікна
        if (event.detail.target.id === 'main-content') {
            const openModals = document.querySelectorAll('.modal');
            openModals.forEach(function (modal) {
                closeModal(modal); // closeModal тепер видаляє з DOM
            });
        }
    });

    // Відкриття модального вікна при додаванні в body
    const observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            mutation.addedNodes.forEach(function (node) {
                if (node.nodeType === 1 && node.classList && node.classList.contains('modal')) {
                    // СПОЧАТКУ видаляємо ВСІ старі модальні з DOM
                    const oldModals = document.querySelectorAll('.modal');
                    oldModals.forEach(function (oldModal) {
                        if (oldModal !== node && oldModal.parentNode) {
                            oldModal.parentNode.removeChild(oldModal);
                        }
                    });

                    // ПОТІМ відкриваємо нове модальне
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
            const btn = e.target.closest('.btn-delete-comment');
            if (confirm('Видалити коментарій?')) {
                // HTMX обробить запит автоматично через hx-post атрибут
                // Якщо HTMX не доступний, виконаємо через fetch
                const hxPost = btn.getAttribute('hx-post');
                if (hxPost && typeof htmx === 'undefined') {
                    const formData = new FormData();
                    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]')?.value || '');
                    fetch(hxPost, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                        }
                    }).then(function () {
                        window.location.reload();
                    });
                }
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
                input.style.display = 'block';
                input.focus();

                function saveDate() {
                    const saveUrl = input.getAttribute('data-save-url');
                    if (!saveUrl) return;

                    const formData = new FormData();
                    formData.append('call_date', input.value);
                    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]')?.value || '');

                    // Використовуємо HTMX якщо доступний
                    if (input.hasAttribute('hx-post')) {
                        // HTMX обробить запит автоматично
                        input.dispatchEvent(new Event('change'));
                        display.style.display = 'flex';
                        input.style.display = 'none';
                    } else {
                        // Fallback на fetch
                        fetch(saveUrl, {
                            method: 'POST',
                            body: formData,
                            headers: {
                                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                            }
                        }).then(function (response) {
                            if (response.ok) {
                                return response.text();
                            } else {
                                throw new Error('Помилка збереження');
                            }
                        }).then(function (html) {
                            display.innerHTML = html;
                            display.style.display = 'flex';
                            input.style.display = 'none';
                            initCallDateEditor(); // Реініціалізуємо обробники
                        }).catch(function (error) {
                            console.error('Error saving call date:', error);
                            alert('Помилка збереження дати');
                        });
                    }
                }

                input.addEventListener('change', saveDate);
                input.addEventListener('blur', saveDate);
            });
        });
    }

    initCallDateEditor();
    document.body.addEventListener('htmx:afterSwap', initCallDateEditor);

    // ==========================================================================
    // Short Comment Auto-Save
    // ==========================================================================

    function initShortCommentEditor() {
        const shortCommentFields = document.querySelectorAll('.short-comment-text[contenteditable="true"]');
        shortCommentFields.forEach(function (field) {
            let saveTimeout;
            const saveUrl = field.getAttribute('data-save-url');
            if (!saveUrl) return;

            field.addEventListener('input', function () {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(function () {
                    const formData = new FormData();
                    formData.append('short_comment', field.textContent.trim());
                    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]')?.value || '');

                    fetch(saveUrl, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                        }
                    }).then(function (response) {
                        if (!response.ok) {
                            console.error('Error saving short comment');
                        }
                    }).catch(function (error) {
                        console.error('Error saving short comment:', error);
                    });
                }, 1000); // Зберігаємо через 1 секунду після останнього вводу
            });
        });
    }

    initShortCommentEditor();
    document.body.addEventListener('htmx:afterSwap', initShortCommentEditor);

    // ==========================================================================
    // Category Badge Colors (через CSS custom properties)
    // ==========================================================================

    function initCategoryBadges() {
        const categoryBadges = document.querySelectorAll('.badge-category[data-bg-color]');
        categoryBadges.forEach(function (badge) {
            const bgColor = badge.getAttribute('data-bg-color');
            const fgColor = badge.getAttribute('data-fg-color');
            if (bgColor) {
                badge.style.setProperty('--category-bg-color', bgColor);
            }
            if (fgColor) {
                badge.style.setProperty('--category-fg-color', fgColor);
            }
        });
    }

    initCategoryBadges();
    document.body.addEventListener('htmx:afterSwap', initCategoryBadges);

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

    // ==========================================================================
    // Rich Text Editor
    // ==========================================================================

    function initRichTextEditor() {
        const editors = document.querySelectorAll('.rich-text-editor');
        editors.forEach(function (editor) {
            const contentDiv = editor.querySelector('.rich-text-content');
            const textarea = editor.querySelector('textarea[name="full_description"]');
            const toolbar = editor.querySelector('.rich-text-toolbar');

            if (!contentDiv || !textarea) return;

            // Синхронізація з textarea при завантаженні
            if (textarea.value) {
                contentDiv.innerHTML = textarea.value;
            }

            // Placeholder
            function updatePlaceholder() {
                if (contentDiv.textContent.trim() === '') {
                    contentDiv.classList.add('is-empty');
                } else {
                    contentDiv.classList.remove('is-empty');
                }
            }
            updatePlaceholder();

            // Синхронізація з textarea перед відправкою форми
            const form = editor.closest('form');
            if (form) {
                form.addEventListener('submit', function () {
                    textarea.value = contentDiv.innerHTML;
                });
            }

            // Оновлення placeholder
            contentDiv.addEventListener('input', function () {
                updatePlaceholder();
                textarea.value = this.innerHTML;
                // Auto-resize
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 500) + 'px';
            });

            // Toolbar buttons
            toolbar.addEventListener('click', function (e) {
                const btn = e.target.closest('.toolbar-btn');
                if (!btn) return;

                e.preventDefault();
                const command = btn.getAttribute('data-command');
                contentDiv.focus();

                if (command === 'createLink') {
                    const url = prompt('Введите URL:', 'https://');
                    if (url) {
                        document.execCommand('createLink', false, url);
                    }
                } else if (command === 'insertEmoji') {
                    const emoji = prompt('Введите эмодзи или текст:', '😀');
                    if (emoji) {
                        document.execCommand('insertText', false, emoji);
                    }
                } else {
                    document.execCommand(command, false, null);
                }

                // Оновлюємо textarea після команди
                textarea.value = contentDiv.innerHTML;
            });

            // Initial resize
            contentDiv.style.height = 'auto';
            contentDiv.style.height = Math.min(contentDiv.scrollHeight, 500) + 'px';
        });
    }

    initRichTextEditor();
    document.body.addEventListener('htmx:afterSwap', initRichTextEditor);

    // ==========================================================================
    // Mobile Menu & Filter
    // ==========================================================================

    function initMobileMenu() {
        const menuBtn = document.getElementById('mobile-menu-btn');
        const menuOverlay = document.getElementById('mobile-menu-overlay');
        const menuClose = menuOverlay?.querySelector('.mobile-menu-close');

        if (menuBtn && menuOverlay) {
            menuBtn.addEventListener('click', function () {
                menuOverlay.classList.add('is-open');
                document.body.style.overflow = 'hidden';
            });

            if (menuClose) {
                menuClose.addEventListener('click', function () {
                    menuOverlay.classList.remove('is-open');
                    document.body.style.overflow = '';
                });
            }

            menuOverlay.addEventListener('click', function (e) {
                if (e.target === menuOverlay) {
                    menuOverlay.classList.remove('is-open');
                    document.body.style.overflow = '';
                }
            });
        }
    }

    function initMobileFilter() {
        const filterBtn = document.getElementById('mobile-filter-btn');
        const filterOverlay = document.getElementById('mobile-filter-overlay');
        const filterBody = document.getElementById('mobile-filter-body');
        const filterClose = filterOverlay?.querySelector('.mobile-filter-close');
        const filtersCard = document.querySelector('.filters-card');

        if (filterBtn && filterOverlay && filterBody) {
            // Move filters to mobile overlay on load
            if (filtersCard && !filterBody.querySelector('.filters-card')) {
                const filtersClone = filtersCard.cloneNode(true);
                filterBody.appendChild(filtersClone);
            }

            filterBtn.addEventListener('click', function () {
                // Re-clone filters in case they were updated
                if (filtersCard) {
                    filterBody.innerHTML = '';
                    const filtersClone = filtersCard.cloneNode(true);
                    filterBody.appendChild(filtersClone);
                }
                filterOverlay.classList.add('is-open');
                document.body.style.overflow = 'hidden';
            });

            if (filterClose) {
                filterClose.addEventListener('click', function () {
                    filterOverlay.classList.remove('is-open');
                    document.body.style.overflow = '';
                });
            }

            filterOverlay.addEventListener('click', function (e) {
                if (e.target === filterOverlay) {
                    filterOverlay.classList.remove('is-open');
                    document.body.style.overflow = '';
                }
            });
        }
    }

    initMobileMenu();
    initMobileFilter();
    document.body.addEventListener('htmx:afterSwap', function () {
        initMobileMenu();
        initMobileFilter();
    });

})();
