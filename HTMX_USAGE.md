# HTMX Usage Guide - CRM_Nice

## Вступ

HTMX дозволяє отримувати доступ до сучасних браузерних можливостей без написання JavaScript. Версія: **2.0.8**

## Підключення

HTMX вже підключений в `templates/base.html`:

```html
<script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js" defer></script>
```

## CSRF Token

CSRF token автоматично додається до всіх HTMX запитів через JavaScript в `static/js/main.js`:

```javascript
document.body.addEventListener('htmx:configRequest', function(event) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        event.detail.headers['X-CSRFToken'] = csrfToken.value;
    }
});
```

## Базові приклади

### GET запит

```html
<button hx-get="/api/data" hx-target="#result">
    Завантажити дані
</button>
<div id="result"></div>
```

### POST запит (форма)

```html
<form hx-post="/api/submit" hx-target="#result">
    {% csrf_token %}
    <input type="text" name="name" required>
    <button type="submit">Відправити</button>
</form>
<div id="result"></div>
```

### View в Django

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def api_data(request):
    data = {"message": "Дані завантажені!"}
    return JsonResponse(data)
```

## Атрибути HTMX

### hx-get, hx-post, hx-put, hx-delete
Вказує метод HTTP запиту та URL.

```html
<button hx-get="/api/data">GET</button>
<button hx-post="/api/data">POST</button>
```

### hx-target
Вказує елемент, куди буде вставлено відповідь.

```html
<button hx-get="/api/data" hx-target="#result">Завантажити</button>
<div id="result"></div>
```

### hx-swap
Вказує, як вставляти контент.

- `innerHTML` (за замовчуванням) - замінює внутрішній контент
- `outerHTML` - замінює весь елемент
- `beforebegin` - перед елементом
- `afterbegin` - на початку елемента
- `beforeend` - в кінці елемента
- `afterend` - після елемента

```html
<button hx-get="/api/data" hx-target="#result" hx-swap="outerHTML">
    Завантажити
</button>
```

### hx-trigger
Вказує подію, що викликає запит.

```html
<!-- Клік (за замовчуванням) -->
<button hx-get="/api/data">Клік</button>

<!-- При наведенні -->
<div hx-get="/api/data" hx-trigger="mouseenter">
    Наведіть курсор
</div>

<!-- При зміні значення -->
<input hx-get="/api/search" hx-trigger="input changed delay:500ms" name="q">
```

### hx-indicator
Показує індикатор завантаження.

```html
<button hx-get="/api/data" hx-indicator="#spinner">
    Завантажити
</button>
<div id="spinner" class="htmx-indicator">Завантаження...</div>
```

CSS для індикатора:

```css
.htmx-indicator {
    display: none;
}

.htmx-request .htmx-indicator {
    display: inline;
}

.htmx-request.htmx-indicator {
    display: inline;
}
```

## Робота з формами

### Проста форма

```html
<form hx-post="/api/submit" hx-target="#result">
    {% csrf_token %}
    <input type="text" name="name" required>
    <input type="email" name="email" required>
    <button type="submit">Відправити</button>
</form>
<div id="result"></div>
```

### View для форми

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["POST"])
def api_submit(request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    
    # Обробка даних...
    
    return JsonResponse({"success": True, "message": "Дані збережено!"})
```

### Валідація форми

```html
<form hx-post="/api/submit" 
      hx-target="#result"
      hx-swap="outerHTML">
    {% csrf_token %}
    <div>
        <input type="text" name="name" required>
        <span class="error"></span>
    </div>
    <button type="submit">Відправити</button>
</form>
<div id="result"></div>
```

## Обробка помилок

### hx-swap-oob
Дозволяє оновлювати кілька елементів одночасно.

```html
<button hx-get="/api/data" hx-target="#result">
    Завантажити
</button>
<div id="result"></div>
<div id="error"></div>
```

View повертає:

```html
<div id="result">Дані завантажено!</div>
<div id="error" hx-swap-oob="true"></div>
```

### Обробка помилок через події

```html
<div hx-get="/api/data" 
     hx-target="#result"
     hx-on::htmx:response-error="showError(event)">
    Завантажити
</div>
<div id="result"></div>
<div id="error" style="display: none;"></div>

<script>
function showError(event) {
    document.getElementById('error').textContent = 'Помилка завантаження!';
    document.getElementById('error').style.display = 'block';
}
</script>
```

## Best Practices

### 1. Завжди використовуйте CSRF token

```html
<form hx-post="/api/submit">
    {% csrf_token %}
    <!-- поля форми -->
</form>
```

### 2. Використовуйте індикатори завантаження

```html
<button hx-get="/api/data" hx-indicator="#spinner">
    Завантажити
</button>
<div id="spinner" class="htmx-indicator">Завантаження...</div>
```

### 3. Обробляйте помилки

```python
from django.http import JsonResponse

def api_data(request):
    try:
        # Логіка
        return JsonResponse({"success": True, "data": data})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
```

### 4. Використовуйте семантичні HTTP методи

- `hx-get` для отримання даних
- `hx-post` для створення
- `hx-put` для оновлення
- `hx-delete` для видалення

### 5. Оптимізуйте запити

```html
<!-- Затримка для пошуку -->
<input hx-get="/api/search" 
       hx-trigger="input changed delay:500ms"
       name="q">
```

### 6. Використовуйте hx-swap-oob для складних оновлень

```html
<div id="main-content"></div>
<div id="sidebar"></div>
<div id="notification"></div>
```

View може оновити всі три елементи одночасно.

## Приклади компонентів

### Модальне вікно

```html
<button hx-get="/modal/content" 
        hx-target="body"
        hx-swap="beforeend">
    Відкрити модальне вікно
</button>
```

### Пагінація

```html
<div hx-get="/api/items?page=1" hx-target="#items">
    <div id="items"></div>
    <button hx-get="/api/items?page=2" hx-target="#items">Наступна</button>
</div>
```

### Пошук в реальному часі

```html
<input type="search" 
       hx-get="/api/search"
       hx-trigger="input changed delay:300ms"
       hx-target="#results"
       name="q">
<div id="results"></div>
```

## Документація

- Офіційний сайт: https://htmx.org/
- Документація: https://htmx.org/docs/
- Приклади: https://htmx.org/examples/
- Django інтеграція: https://django-htmx.readthedocs.io/



