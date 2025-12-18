# ⚡ ШВИДКЕ ВИПРАВЛЕННЯ - Деплой CRM Nice на Render

## ❌ Помилка: "Cannot have more than one active free tier database"

## ✅ ШВИДКЕ РІШЕННЯ (2 хвилини)

### Спосіб А: З існуючою PostgreSQL базою (рекомендовано для production)

1. **Отримайте DATABASE_URL вашої існуючої бази:**
   - Render Dashboard → ваша PostgreSQL база → копіюйте **Internal Database URL**

2. **Створіть Web Service:**
   - [Render Dashboard](https://dashboard.render.com/) → **"New +"** → **"Web Service"**
   - Repository: `BonisOleg/odessa`
   - Build Command: `./build.sh`
   - Start Command: `gunicorn CRM_Nice.wsgi:application`

3. **Додайте Environment Variables:**
   ```
   DJANGO_SETTINGS_MODULE=CRM_Nice.settings.production
   DEBUG=False
   ALLOWED_HOSTS=your-app.onrender.com
   DATABASE_URL=<ваш Internal Database URL>
   CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com
   ```

4. **"Create Web Service"** → Готово! ✅

---

### Спосіб Б: З SQLite (швидке тестування)

⚠️ Для тестування, не для production!

1. **Створіть Web Service:**
   - [Render Dashboard](https://dashboard.render.com/) → **"New +"** → **"Blueprint"**
   - Repository: `BonisOleg/odessa`

2. **Додайте Environment Variables:**
   ```
   ALLOWED_HOSTS=your-app.onrender.com
   CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com
   ```
   
   **⚠️ НЕ ДОДАВАЙТЕ `DATABASE_URL`** - застосунок автоматично використає SQLite

3. **"Apply"** → Готово! ✅

---

## 📝 Що виправлено в коді:

✅ `render.yaml` - не створює нову базу даних  
✅ `production.py` - підтримує PostgreSQL або SQLite  
✅ Код оновлено в GitHub: `git@github.com:BonisOleg/odessa.git`

---

## 🎯 Після деплою:

Створіть суперюзера через Shell:
```bash
python manage.py createsuperuser
```

---

## 📚 Детальна інструкція: `RENDER_FIX.md`
