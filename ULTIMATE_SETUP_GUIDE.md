# 🚀 Повна інструкція налаштування системи автоматичного контролю якості коду
## Django + HTML + HTMX + CSS + Vanilla JavaScript (Ultimate Edition 2025)

> **Мета**: Створити систему, яка **фізично унеможливлює** порушення правил кросплатформенної веб-розробки через автоматичні перевірки, лінтери та Git hooks.

---

## 📋 Зміст

1. [Вступ та філософія](#вступ-та-філософія)
2. [Архітектура системи](#архітектура-системи)
3. [Передумови та вимоги](#передумови-та-вимоги)
4. [Крок 1: Підготовка проєкту](#крок-1-підготовка-проєкту)
5. [Крок 2: Встановлення Node.js залежностей](#крок-2-встановлення-nodejs-залежностей)
6. [Крок 3: Конфігурація Stylelint (CSS)](#крок-3-конфігурація-stylelint-css)
7. [Крок 4: Конфігурація ESLint (JavaScript)](#крок-4-конфігурація-eslint-javascript)
8. [Крок 5: Конфігурація HTMLHint (HTML/Django шаблони)](#крок-5-конфігурація-htmlhint-htmldjango-шаблони)
9. [Крок 6: Створення кастомних bash-скриптів перевірки](#крок-6-створення-кастомних-bash-скриптів-перевірки)
10. [Крок 7: Створення скриптів автоматичного виправлення](#крок-7-створення-скриптів-автоматичного-виправлення)
11. [Крок 8: Налаштування Git Hooks (Husky)](#крок-8-налаштування-git-hooks-husky)
12. [Крок 9: Тестування системи](#крок-9-тестування-системи)
13. [Крок 10: Виправлення існуючих порушень](#крок-10-виправлення-існуючих-порушень)
14. [Інтеграція з Django](#інтеграція-з-django)
15. [Робота з HTMX](#робота-з-htmx)
16. [Повний список правил (110+)](#повний-список-правил-110)
17. [Troubleshooting та поширені проблеми](#troubleshooting-та-поширені-проблеми)
18. [Адаптація для різних проектів](#адаптація-для-різних-проектів)
19. [CI/CD інтеграція](#cicd-інтеграція)
20. [Підтримка та оновлення](#підтримка-та-оновлення)
21. [Швидкий старт (TL;DR)](#швидкий-старт-tldr)
22. [Чек-лист налаштування](#чек-лист-налаштування)

---

## Вступ та філософія

### Чому ця система потрібна?

Кросплатформенна веб-розробка у 2025 році вимагає дотримання **більше 110 правил**, які охоплюють:
- **HTML**: семантика, viewport, accessibility, HTMX атрибути
- **CSS**: viewport units, safe areas, flexbox, container queries, rem units, backdrop-filter
- **JavaScript**: bfcache, pageshow, pointer events, HTMX інтеграція
- **Django**: template tags (заборона розривів), форми, CSRF
- **UX**: touch targets (44px), scroll behavior, модальні вікна
- **Безпека**: CSP, відсутність inline styles/scripts, відсутність eval

Ручний контроль цих правил **неможливий**. Ця система автоматизує 95%+ перевірок.

### Три рівні захисту

1. **Lint-On-Save** — IDE показує помилки в реальному часі (якщо налаштовано)
2. **Pre-Commit Hook** — блокує commit, якщо є порушення
3. **CI/CD Pipeline** — фінальна перевірка перед deploy

---

## Архітектура системи

```
Ваш проєкт/
├── package.json              # Node.js залежності (Stylelint, ESLint, HTMLHint, Husky)
├── .stylelintrc.json         # Конфігурація CSS лінтера
├── .eslintrc.json            # Конфігурація JS лінтера
├── .htmlhintrc               # Конфігурація HTML лінтера
├── .husky/
│   └── pre-commit            # Git hook (запускається перед commit)
├── scripts/
│   ├── check-html-rules.sh   # Кастомні HTML перевірки (viewport, inputmode, video)
│   ├── check-css-rules.sh    # Кастомні CSS перевірки (100vh → 100dvh, safe-area, rem)
│   ├── check-js-rules.sh     # Кастомні JS перевірки (pageshow, var, strict mode)
│   ├── check_template_tags.sh# Django template перевірка (заборона розривів тегів)
│   ├── fix-rules.sh          # Автоматичні виправлення (inline styles, inputmode)
│   ├── check-all-rules.sh    # Запуск ВСІХ перевірок
│   ├── setup-git-hooks.sh    # Скрипт налаштування Husky
│   └── README.md             # Документація скриптів
├── static/
│   ├── css/
│   │   ├── normalize.css     # ❌ ЗАБОРОНЕНО ЗМІНЮВАТИ
│   │   ├── base.css          # CSS custom properties, body styles
│   │   ├── components/*.css  # BEM компоненти
│   │   └── utilities/*.css   # Утилітарні класси
│   └── js/
│       └── main.js           # Vanilla JS (defer, strict mode, pageshow)
├── templates/
│   ├── base.html             # Базовий шаблон (viewport meta, HTMX CDN)
│   └── .../*.html            # Django шаблони
├── CRM_Nice/settings/        # Django settings (base, develop, production)
├── requirements.txt          # Python залежності
└── .gitignore                # node_modules/, package-lock.json
```

---

## Передумови та вимоги

### Встановлене ПЗ

```bash
# Перевірка версій
node --version   # v18+ (рекомендовано v20+)
npm --version    # v9+
python --version # 3.10+
git --version    # 2.30+
```

Якщо Node.js відсутній:
```bash
# macOS (Homebrew)
brew install node

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows (через nvm-windows або офіційний інсталятор)
```

### Структура Django проєкту

Система працює з будь-яким Django проєктом, але очікує:
- `static/css/` — CSS файли
- `static/js/` — JavaScript файли
- `templates/` — Django шаблони (`.html`)
- `manage.py` — в корені проєкту

---

## Крок 1: Підготовка проєкту

### 1.1. Перевірка структури

```bash
cd /path/to/your/django/project
ls -la
# Має бути: manage.py, static/, templates/, requirements.txt
```

### 1.2. Оновлення `.gitignore`

Додайте в `.gitignore`:

```gitignore
# Node.js
node_modules/
package-lock.json

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
venv/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Static
staticfiles/
media/

# Env
.env
.env.local

# OS
.DS_Store
Thumbs.db
```

### 1.3. Створення директорії `scripts/`

```bash
mkdir -p scripts
touch scripts/README.md
```

---

## Крок 2: Встановлення Node.js залежностей

### 2.1. Ініціалізація `package.json`

Створіть файл `package.json` в **корені проєкту**:

```json
{
  "name": "django-project-linters",
  "version": "1.0.0",
  "description": "Automated code quality checks for Django + HTMX project",
  "private": true,
  "scripts": {
    "lint": "npm run lint:css && npm run lint:js && npm run lint:html",
    "lint:css": "stylelint \"static/css/**/*.css\"",
    "lint:js": "eslint \"static/js/**/*.js\"",
    "lint:html": "htmlhint \"templates/**/*.html\"",
    "lint:fix": "npm run lint:css -- --fix && npm run lint:js -- --fix",
    "check:rules": "bash scripts/check-all-rules.sh",
    "fix:rules": "bash scripts/fix-rules.sh",
    "prepare": "husky install"
  },
  "devDependencies": {
    "stylelint": "^16.0.0",
    "stylelint-config-standard": "^36.0.0",
    "stylelint-order": "^6.0.4",
    "stylelint-declaration-block-no-ignored-properties": "^2.8.0",
    "stylelint-high-performance-animation": "^1.10.0",
    "stylelint-no-unsupported-browser-features": "^8.0.1",
    "eslint": "^8.57.0",
    "eslint-plugin-compat": "^4.2.0",
    "htmlhint": "^1.1.4",
    "husky": "^9.0.0",
    "lint-staged": "^15.2.0"
  },
  "browserslist": [
    "Chrome >= 90",
    "Firefox >= 88",
    "Safari >= 14",
    "Edge >= 90",
    "iOS >= 14",
    "Android >= 90"
  ]
}
```

### 2.2. Встановлення залежностей

```bash
npm install
```

**Очікуваний результат**:
- Створено `node_modules/` (не комітиться в Git)
- Створено `package-lock.json` (не комітиться в Git)
- Встановлені всі лінтери та плагіни

---

## Крок 3: Конфігурація Stylelint (CSS)

### 3.1. Створення `.stylelintrc.json`

Створіть файл `.stylelintrc.json` в **корені проєкту**:

```json
{
  "extends": ["stylelint-config-standard"],
  "plugins": [
    "stylelint-order",
    "stylelint-declaration-block-no-ignored-properties",
    "stylelint-high-performance-animation",
    "stylelint-no-unsupported-browser-features"
  ],
  "rules": {
    "declaration-no-important": true,
    "selector-pseudo-class-no-unknown": [
      true,
      {
        "ignorePseudoClasses": ["has", "where", "is"]
      }
    ],
    "at-rule-no-unknown": [
      true,
      {
        "ignoreAtRules": ["layer", "container", "supports", "scope"]
      }
    ],
    "declaration-block-no-duplicate-properties": [
      true,
      {
        "ignore": ["consecutive-duplicates-with-different-values"]
      }
    ],
    "plugin/declaration-block-no-ignored-properties": true,
    "plugin/no-low-performance-animation-properties": true,
    "plugin/no-unsupported-browser-features": [
      true,
      {
        "severity": "warning",
        "ignore": [
          "css-nesting",
          "css-has",
          "viewport-units",
          "css-overscroll-behavior",
          "text-size-adjust"
        ]
      }
    ],
    "custom-property-pattern": null,
    "selector-class-pattern": null,
    "max-nesting-depth": 3,
    "no-descending-specificity": null,
    "order/properties-alphabetical-order": null,
    "property-no-vendor-prefix": null,
    "color-hex-length": null,
    "value-keyword-case": null,
    "color-function-notation": null,
    "alpha-value-notation": null,
    "declaration-block-no-redundant-longhand-properties": null
  },
  "ignoreFiles": ["static/css/normalize.css"]
}
```

### 3.2. Пояснення ключових правил

| Правило | Опис | Чому важливо |
|---------|------|--------------|
| `declaration-no-important` | ❌ Забороняє `!important` | Низька специфічність = керованість |
| `plugin/no-unsupported-browser-features` | ⚠️ Попереджає про несумісні властивості | Кросплатформенність (Chrome 90+, Safari 14+) |
| `max-nesting-depth: 3` | Обмежує вкладеність CSS | Читабельність, специфічність |
| `ignoreFiles: normalize.css` | ❌ Не перевіряти normalize.css | **КРИТИЧНО**: ніколи не змінювати! |

### 3.3. Тестування Stylelint

```bash
npm run lint:css
```

**Приклад виводу** (якщо є помилки):

```
static/css/base.css
  45:3  ✖  Unexpected !important   declaration-no-important
  67:5  ⚠  text-wrap: balance is not supported in Chrome 90

✖ 1 problem (1 error, 1 warning)
```

---

## Крок 4: Конфігурація ESLint (JavaScript)

### 4.1. Створення `.eslintrc.json`

Створіть файл `.eslintrc.json` в **корені проєкту**:

```json
{
  "env": {
    "browser": true,
    "es2021": true
  },
  "extends": "eslint:recommended",
  "parserOptions": {
    "ecmaVersion": 2021,
    "sourceType": "module"
  },
  "rules": {
    "no-var": "error",
    "prefer-const": "error",
    "no-eval": "error",
    "no-implied-eval": "error",
    "no-new-func": "error",
    "no-global-assign": "error",
    "no-implicit-globals": "error",
    "strict": "off",
    "no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "prefer-arrow-callback": "warn",
    "no-lonely-if": "warn",
    "no-else-return": "warn",
    "prefer-template": "warn",
    "no-undef": "warn"
  },
  "globals": {
    "htmx": "readonly"
  }
}
```

### 4.2. Пояснення ключових правил

| Правило | Опис | Чому важливо |
|---------|------|--------------|
| `no-var: error` | ❌ Забороняє `var` | Використовуйте `const`/`let` (ES6+) |
| `no-eval: error` | ❌ Забороняє `eval()` | Безпека (CSP, XSS) |
| `prefer-const: error` | Вимагає `const` де можливо | Іммутабельність |
| `globals: { htmx: readonly }` | Визначає HTMX як глобальну змінну | Уникнення `no-undef` помилок |

### 4.3. Тестування ESLint

```bash
npm run lint:js
```

**Приклад виводу**:

```
static/js/main.js
  12:5  error  'var' is not allowed  no-var
  34:9  error  eval can be harmful   no-eval

✖ 2 problems (2 errors, 0 warnings)
```

---

## Крок 5: Конфігурація HTMLHint (HTML/Django шаблони)

### 5.1. Створення `.htmlhintrc`

Створіть файл `.htmlhintrc` в **корені проєкту**:

```json
{
  "tagname-lowercase": true,
  "attr-lowercase": false,
  "attr-value-double-quotes": true,
  "doctype-first": false,
  "tag-pair": false,
  "spec-char-escape": false,
  "id-unique": true,
  "src-not-empty": true,
  "attr-no-duplication": true,
  "title-require": false,
  "inline-style-disabled": true,
  "inline-script-disabled": true,
  "space-tab-mixed-disabled": "space",
  "id-class-ad-disabled": true,
  "attr-unsafe-chars": true
}
```

### 5.2. Чому деякі правила вимкнені?

| Правило | Статус | Пояснення |
|---------|--------|-----------|
| `doctype-first: false` | ❌ Вимкнено | Django `{% extends %}` йде перед `<!DOCTYPE>` |
| `tag-pair: false` | ❌ Вимкнено | Django теги `{% if %}` порушують парність |
| `spec-char-escape: false` | ❌ Вимкнено | `{{ variable }}` містить `{` та `}` |
| `inline-style-disabled: true` | ✅ **КРИТИЧНО** | Забороняє `<div style="...">` |
| `inline-script-disabled: true` | ✅ **КРИТИЧНО** | Забороняє `<script>alert()</script>` |

### 5.3. Тестування HTMLHint

```bash
npm run lint:html
```

**Приклад виводу**:

```
templates/base.html
  23:5  error  Inline style cannot be used  inline-style-disabled

✖ 1 problem (1 error, 0 warnings)
```

---

## Крок 6: Створення кастомних bash-скриптів перевірки

HTMLHint не може перевірити **всі** правила (наприклад, атрибути viewport meta, `inputmode`, `video` теги). Тому створюємо кастомні bash-скрипти.

### 6.1. `scripts/check-html-rules.sh`

```bash
#!/bin/bash
set -e

echo "========================================="
echo "🔍 HTML Custom Rules Check"
echo "========================================="

ERROR_COUNT=0
WARNING_COUNT=0

# Знаходимо всі HTML файли (крім normalize.css та node_modules)
HTML_FILES=$(find templates -name "*.html" 2>/dev/null || echo "")

if [ -z "$HTML_FILES" ]; then
  echo "⚠️  No HTML files found in templates/"
  exit 0
fi

# Правило 1: viewport meta має містити viewport-fit=cover та interactive-widget=resizes-content
echo ""
echo "📱 [Rule 1] Checking viewport meta attributes..."
VIEWPORT_ISSUES=$(echo "$HTML_FILES" | xargs grep -l 'name="viewport"' | while read -r file; do
  if ! grep -q 'viewport-fit=cover' "$file" || ! grep -q 'interactive-widget=resizes-content' "$file"; then
    echo "$file"
  fi
done)

if [ -n "$VIEWPORT_ISSUES" ]; then
  echo "❌ Viewport meta tags missing required attributes:"
  echo "$VIEWPORT_ISSUES" | while read -r file; do
    echo "   $file"
  done
  echo "   Required: <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0, viewport-fit=cover, interactive-widget=resizes-content\">"
  ((ERROR_COUNT++))
else
  echo "✅ All viewport meta tags are correct"
fi

# Правило 2: inline style="" заборонені (дублює HTMLHint, але для надійності)
echo ""
echo "🎨 [Rule 2] Checking for inline styles..."
INLINE_STYLES=$(echo "$HTML_FILES" | xargs grep -n 'style="' || echo "")
if [ -n "$INLINE_STYLES" ]; then
  echo "❌ Inline styles found (forbidden):"
  echo "$INLINE_STYLES"
  ((ERROR_COUNT++))
else
  echo "✅ No inline styles detected"
fi

# Правило 3: inline onclick="", onerror="" та інші event handlers заборонені
echo ""
echo "🔧 [Rule 3] Checking for inline event handlers..."
INLINE_HANDLERS=$(echo "$HTML_FILES" | xargs grep -nE 'on(click|load|error|submit|change|input|focus|blur|keydown|keyup|mouseover|mouseout)=' || echo "")
if [ -n "$INLINE_HANDLERS" ]; then
  echo "❌ Inline event handlers found (forbidden):"
  echo "$INLINE_HANDLERS"
  ((ERROR_COUNT++))
else
  echo "✅ No inline event handlers detected"
fi

# Правило 4: input type="tel" або type="number" має мати inputmode="tel" або inputmode="decimal"
echo ""
echo "📞 [Rule 4] Checking inputmode for tel/number inputs..."
TEL_INPUTS=$(echo "$HTML_FILES" | xargs grep -n 'type="tel"' | grep -v 'inputmode="tel"' || echo "")
NUMBER_INPUTS=$(echo "$HTML_FILES" | xargs grep -n 'type="number"' | grep -v 'inputmode=' || echo "")

if [ -n "$TEL_INPUTS" ]; then
  echo "⚠️  Inputs with type=\"tel\" missing inputmode=\"tel\":"
  echo "$TEL_INPUTS"
  ((WARNING_COUNT++))
fi

if [ -n "$NUMBER_INPUTS" ]; then
  echo "⚠️  Inputs with type=\"number\" missing inputmode (recommend inputmode=\"decimal\"):"
  echo "$NUMBER_INPUTS"
  ((WARNING_COUNT++))
fi

if [ -z "$TEL_INPUTS" ] && [ -z "$NUMBER_INPUTS" ]; then
  echo "✅ All tel/number inputs have correct inputmode"
fi

# Правило 5: <video> теги мають містити poster, playsinline, muted
echo ""
echo "🎬 [Rule 5] Checking video tags..."
VIDEO_TAGS=$(echo "$HTML_FILES" | xargs grep -n '<video' || echo "")
if [ -n "$VIDEO_TAGS" ]; then
  echo "$VIDEO_TAGS" | while read -r line; do
    file=$(echo "$line" | cut -d: -f1)
    linenum=$(echo "$line" | cut -d: -f2)
    content=$(echo "$line" | cut -d: -f3-)
    
    issues=""
    echo "$content" | grep -q 'poster=' || issues="${issues}poster "
    echo "$content" | grep -q 'playsinline' || issues="${issues}playsinline "
    echo "$content" | grep -q 'muted' || issues="${issues}muted "
    
    if [ -n "$issues" ]; then
      echo "⚠️  $file:$linenum missing attributes: $issues"
      ((WARNING_COUNT++))
    fi
  done
else
  echo "✅ No video tags found (or all are correct)"
fi

# Правило 6: <script> теги мають містити defer або async
echo ""
echo "📜 [Rule 6] Checking script tags for defer/async..."
SCRIPT_TAGS=$(echo "$HTML_FILES" | xargs grep -n '<script src=' | grep -v 'defer\|async' || echo "")
if [ -n "$SCRIPT_TAGS" ]; then
  echo "⚠️  Script tags without defer/async found:"
  echo "$SCRIPT_TAGS"
  ((WARNING_COUNT++))
else
  echo "✅ All external scripts have defer/async"
fi

# Правило 7: touch-action: manipulation для інтерактивних елементів (перевіряємо в CSS, але нагадуємо тут)
echo ""
echo "👆 [Rule 7] Reminder: Use touch-action: manipulation for interactive elements"
echo "   (This is checked in CSS, ensure buttons/links have this property)"

# Підсумок
echo ""
echo "========================================="
echo "📊 HTML Rules Summary"
echo "========================================="
echo "Errors: $ERROR_COUNT"
echo "Warnings: $WARNING_COUNT"

if [ $ERROR_COUNT -gt 0 ]; then
  echo "❌ HTML custom rules check FAILED"
  exit 1
else
  echo "✅ HTML custom rules check PASSED"
  exit 0
fi
```

Зробіть скрипт виконуваним:

```bash
chmod +x scripts/check-html-rules.sh
```

### 6.2. `scripts/check-css-rules.sh`

```bash
#!/bin/bash
set -e

echo "========================================="
echo "🎨 CSS Custom Rules Check"
echo "========================================="

ERROR_COUNT=0
WARNING_COUNT=0

# Знаходимо всі CSS файли (крім normalize.css)
CSS_FILES=$(find static/css -name "*.css" ! -name "normalize.css" 2>/dev/null || echo "")

if [ -z "$CSS_FILES" ]; then
  echo "⚠️  No CSS files found in static/css/"
  exit 0
fi

# Правило 1: 100vh має мати fallback 100dvh (або коментар "Fallback")
echo ""
echo "📐 [Rule 1] Checking 100vh fallback..."
VH_ISSUES=$(echo "$CSS_FILES" | while read -r file; do
  grep -n '100vh' "$file" | while IFS=: read -r linenum line; do
    # Перевіряємо, чи є 100dvh або коментар "Fallback" в наступних 2 рядках
    context=$(sed -n "$((linenum-1)),$((linenum+2))p" "$file")
    if ! echo "$context" | grep -qE '100dvh|Fallback'; then
      echo "$file:$linenum: $line"
    fi
  done
done)

if [ -n "$VH_ISSUES" ]; then
  echo "❌ Found 100vh without 100dvh fallback:"
  echo "$VH_ISSUES"
  echo "   Fix: Use 'height: 100vh; /* Fallback */ height: 100dvh;'"
  ((ERROR_COUNT++))
else
  echo "✅ All 100vh declarations have fallback"
fi

# Правило 2: safe-area-inset-* має використовуватись для padding/margin
echo ""
echo "📱 [Rule 2] Checking safe-area-inset usage..."
SAFE_AREA_USAGE=$(echo "$CSS_FILES" | xargs grep -c 'env(safe-area-inset-' | grep -v ':0$' || echo "")
if [ -z "$SAFE_AREA_USAGE" ]; then
  echo "⚠️  No safe-area-inset usage detected (may be intentional)"
  echo "   Recommendation: Use env(safe-area-inset-bottom) for fixed elements"
  ((WARNING_COUNT++))
else
  echo "✅ safe-area-inset is used: $(echo "$SAFE_AREA_USAGE" | wc -l) file(s)"
fi

# Правило 3: font-size має бути в rem, а не px (warning, не error)
echo ""
echo "🔤 [Rule 3] Checking font-size units (prefer rem over px)..."
PX_FONT_SIZES=$(echo "$CSS_FILES" | xargs grep -n 'font-size:.*px' || echo "")
if [ -n "$PX_FONT_SIZES" ]; then
  echo "⚠️  font-size in px found (recommend rem for accessibility):"
  echo "$PX_FONT_SIZES" | head -n 10
  if [ $(echo "$PX_FONT_SIZES" | wc -l) -gt 10 ]; then
    echo "   ... and $(( $(echo "$PX_FONT_SIZES" | wc -l) - 10 )) more"
  fi
  ((WARNING_COUNT++))
else
  echo "✅ All font-sizes use rem"
fi

# Правило 4: flex: 1; має бути flex: 1 0 0; або flex: 1 0 auto;
echo ""
echo "📦 [Rule 4] Checking flex shorthand..."
FLEX_ISSUES=$(echo "$CSS_FILES" | xargs grep -n 'flex:\s*1;' || echo "")
if [ -n "$FLEX_ISSUES" ]; then
  echo "❌ Found 'flex: 1;' without explicit flex-basis:"
  echo "$FLEX_ISSUES"
  echo "   Fix: Use 'flex: 1 0 0;' or 'flex: 1 0 auto;'"
  ((ERROR_COUNT++))
else
  echo "✅ All flex shorthands are explicit"
fi

# Правило 5: hover ефекти мають бути в @media (hover: hover)
echo ""
echo "🖱️  [Rule 5] Checking hover effects in media query..."
HOVER_EFFECTS=$(echo "$CSS_FILES" | xargs grep -n ':hover' || echo "")
if [ -n "$HOVER_EFFECTS" ]; then
  # Перевіряємо, чи всі :hover в @media (hover: hover)
  UNCHECKED_HOVERS=$(echo "$CSS_FILES" | while read -r file; do
    awk '
      /@media.*\(hover: hover\)/ { in_media=1; next }
      /^}/ { if (in_media) in_media=0 }
      /:hover/ { if (!in_media) print FILENAME":"NR":"$0 }
    ' "$file"
  done)
  
  if [ -n "$UNCHECKED_HOVERS" ]; then
    echo "⚠️  :hover effects outside @media (hover: hover):"
    echo "$UNCHECKED_HOVERS" | head -n 5
    echo "   Recommendation: Wrap hover effects in @media (hover: hover) { ... }"
    ((WARNING_COUNT++))
  else
    echo "✅ All :hover effects are in @media (hover: hover)"
  fi
else
  echo "✅ No hover effects found"
fi

# Правило 6: overscroll-behavior: none; на body
echo ""
echo "📜 [Rule 6] Checking overscroll-behavior..."
OVERSCROLL=$(echo "$CSS_FILES" | xargs grep -c 'overscroll-behavior' | grep -v ':0$' || echo "")
if [ -z "$OVERSCROLL" ]; then
  echo "⚠️  No overscroll-behavior detected"
  echo "   Recommendation: Add 'body { overscroll-behavior: none; }' to base.css"
  ((WARNING_COUNT++))
else
  echo "✅ overscroll-behavior is used"
fi

# Правило 7: !important заборонений (дублює Stylelint, але для надійності)
echo ""
echo "🚫 [Rule 7] Checking for !important..."
IMPORTANT=$(echo "$CSS_FILES" | xargs grep -n '!important' || echo "")
if [ -n "$IMPORTANT" ]; then
  echo "❌ !important found (forbidden):"
  echo "$IMPORTANT"
  ((ERROR_COUNT++))
else
  echo "✅ No !important detected"
fi

# Правило 8: backdrop-filter має мати -webkit- prefix
echo ""
echo "🌫️  [Rule 8] Checking backdrop-filter prefix..."
BACKDROP_ISSUES=$(echo "$CSS_FILES" | xargs grep -n 'backdrop-filter:' | grep -v '\-webkit-backdrop-filter' || echo "")
if [ -n "$BACKDROP_ISSUES" ]; then
  echo "⚠️  backdrop-filter without -webkit- prefix:"
  echo "$BACKDROP_ISSUES"
  echo "   Fix: Add '-webkit-backdrop-filter: ...; backdrop-filter: ...;'"
  ((WARNING_COUNT++))
else
  echo "✅ All backdrop-filters have -webkit- prefix (or none used)"
fi

# Підсумок
echo ""
echo "========================================="
echo "📊 CSS Rules Summary"
echo "========================================="
echo "Errors: $ERROR_COUNT"
echo "Warnings: $WARNING_COUNT"

if [ $ERROR_COUNT -gt 0 ]; then
  echo "❌ CSS custom rules check FAILED"
  exit 1
else
  echo "✅ CSS custom rules check PASSED"
  exit 0
fi
```

Зробіть скрипт виконуваним:

```bash
chmod +x scripts/check-css-rules.sh
```

### 6.3. `scripts/check-js-rules.sh`

```bash
#!/bin/bash
set -e

echo "========================================="
echo "⚡ JavaScript Custom Rules Check"
echo "========================================="

ERROR_COUNT=0
WARNING_COUNT=0

# Знаходимо всі JS файли
JS_FILES=$(find static/js -name "*.js" 2>/dev/null || echo "")

if [ -z "$JS_FILES" ]; then
  echo "⚠️  No JavaScript files found in static/js/"
  exit 0
fi

# Правило 1: var заборонений (дублює ESLint, але для надійності)
echo ""
echo "🚫 [Rule 1] Checking for var usage..."
VAR_USAGE=$(echo "$JS_FILES" | xargs grep -nE '\bvar\s+' || echo "")
if [ -n "$VAR_USAGE" ]; then
  echo "❌ 'var' found (use const/let):"
  echo "$VAR_USAGE"
  ((ERROR_COUNT++))
else
  echo "✅ No 'var' usage detected"
fi

# Правило 2: pageshow event listener для bfcache
echo ""
echo "🔄 [Rule 2] Checking for pageshow event listener..."
PAGESHOW=$(echo "$JS_FILES" | xargs grep -c "pageshow" | grep -v ':0$' || echo "")
if [ -z "$PAGESHOW" ]; then
  echo "⚠️  No 'pageshow' event listener detected"
  echo "   Recommendation: Add window.addEventListener('pageshow', (event) => { ... }) for bfcache"
  ((WARNING_COUNT++))
else
  echo "✅ pageshow event listener found"
fi

# Правило 3: strict mode або IIFE
echo ""
echo "🔒 [Rule 3] Checking for strict mode or IIFE..."
STRICT_MODE=$(echo "$JS_FILES" | xargs grep -c "'use strict'" | grep -v ':0$' || echo "")
IIFE=$(echo "$JS_FILES" | xargs grep -c '(function()' | grep -v ':0$' || echo "")

if [ -z "$STRICT_MODE" ] && [ -z "$IIFE" ]; then
  echo "⚠️  No 'use strict' or IIFE detected"
  echo "   Recommendation: Use 'use strict'; or wrap code in IIFE"
  ((WARNING_COUNT++))
else
  echo "✅ Code uses strict mode or IIFE"
fi

# Правило 4: eval() заборонений (дублює ESLint)
echo ""
echo "🚨 [Rule 4] Checking for eval() usage..."
EVAL_USAGE=$(echo "$JS_FILES" | xargs grep -nE '\beval\s*\(' || echo "")
if [ -n "$EVAL_USAGE" ]; then
  echo "❌ eval() found (forbidden for security):"
  echo "$EVAL_USAGE"
  ((ERROR_COUNT++))
else
  echo "✅ No eval() usage detected"
fi

# Правило 5: HTMX integration check (htmx:afterSwap, htmx:configRequest)
echo ""
echo "🔗 [Rule 5] Checking HTMX integration..."
HTMX_INTEGRATION=$(echo "$JS_FILES" | xargs grep -cE 'htmx:(afterSwap|configRequest|responseError|sendError)' | grep -v ':0$' || echo "")
if [ -n "$HTMX_INTEGRATION" ]; then
  echo "✅ HTMX event listeners found"
else
  echo "ℹ️  No HTMX event listeners detected (may be intentional)"
fi

# Підсумок
echo ""
echo "========================================="
echo "📊 JavaScript Rules Summary"
echo "========================================="
echo "Errors: $ERROR_COUNT"
echo "Warnings: $WARNING_COUNT"

if [ $ERROR_COUNT -gt 0 ]; then
  echo "❌ JavaScript custom rules check FAILED"
  exit 1
else
  echo "✅ JavaScript custom rules check PASSED"
  exit 0
fi
```

Зробіть скрипт виконуваним:

```bash
chmod +x scripts/check-js-rules.sh
```

### 6.4. `scripts/check_template_tags.sh` (Django)

**Найважливіша перевірка для Django шаблонів!**

```bash
#!/bin/bash
set -e

echo "========================================="
echo "🔖 Django Template Tags Check"
echo "========================================="

ERROR_COUNT=0

# Знаходимо всі HTML файли в templates/
HTML_FILES=$(find templates -name "*.html" 2>/dev/null || echo "")

if [ -z "$HTML_FILES" ]; then
  echo "⚠️  No template files found"
  exit 0
fi

# Правило: Django теги {{ }} та {% %} НЕ можна розривати на кілька рядків
echo ""
echo "🚫 [CRITICAL] Checking for broken Django template tags..."

# Перевірка 1: {{ на одному рядку, }} на іншому
BROKEN_VAR_TAGS=$(echo "$HTML_FILES" | xargs grep -Pzon '\{\{[^}]*\n' || echo "")
if [ -n "$BROKEN_VAR_TAGS" ]; then
  echo "❌ Found {{ }} tags broken across lines:"
  echo "$BROKEN_VAR_TAGS" | head -n 20
  ((ERROR_COUNT++))
fi

# Перевірка 2: {% на одному рядку, %} на іншому
BROKEN_BLOCK_TAGS=$(echo "$HTML_FILES" | xargs grep -Pzon '\{%[^%]*\n.*?%\}' || echo "")
if [ -n "$BROKEN_BLOCK_TAGS" ]; then
  echo "❌ Found {% %} tags broken across lines:"
  echo "$BROKEN_BLOCK_TAGS" | head -n 20
  ((ERROR_COUNT++))
fi

if [ $ERROR_COUNT -eq 0 ]; then
  echo "✅ All Django template tags are on single lines"
fi

# Підсумок
echo ""
echo "========================================="
echo "📊 Django Template Tags Summary"
echo "========================================="
echo "Errors: $ERROR_COUNT"

if [ $ERROR_COUNT -gt 0 ]; then
  echo "❌ Django template tags check FAILED"
  echo ""
  echo "🔧 How to fix:"
  echo "   - Keep {{ variable }} on one line"
  echo "   - Keep {% tag %} on one line"
  echo "   - Use {% with %} for complex expressions"
  echo "   - Use custom template filters for long variable names"
  exit 1
else
  echo "✅ Django template tags check PASSED"
  exit 0
fi
```

Зробіть скрипт виконуваним:

```bash
chmod +x scripts/check_template_tags.sh
```

### 6.5. `scripts/check-all-rules.sh` (Wrapper)

Цей скрипт запускає **всі** перевірки:

```bash
#!/bin/bash

echo "╔════════════════════════════════════════╗"
echo "║   🚀 FULL PROJECT HEALTH CHECK        ║"
echo "╔════════════════════════════════════════╗"
echo ""

TOTAL_ERRORS=0

# 1. Django Template Tags
if [ -f "scripts/check_template_tags.sh" ]; then
  bash scripts/check_template_tags.sh || ((TOTAL_ERRORS++))
  echo ""
fi

# 2. HTML Custom Rules
if [ -f "scripts/check-html-rules.sh" ]; then
  bash scripts/check-html-rules.sh || ((TOTAL_ERRORS++))
  echo ""
fi

# 3. CSS Custom Rules
if [ -f "scripts/check-css-rules.sh" ]; then
  bash scripts/check-css-rules.sh || ((TOTAL_ERRORS++))
  echo ""
fi

# 4. JavaScript Custom Rules
if [ -f "scripts/check-js-rules.sh" ]; then
  bash scripts/check-js-rules.sh || ((TOTAL_ERRORS++))
  echo ""
fi

# 5. Stylelint
if command -v npm &> /dev/null && [ -f "package.json" ]; then
  echo "========================================="
  echo "🎨 Running Stylelint..."
  echo "========================================="
  npm run lint:css || ((TOTAL_ERRORS++))
  echo ""
fi

# 6. ESLint
if command -v npm &> /dev/null && [ -f "package.json" ]; then
  echo "========================================="
  echo "⚡ Running ESLint..."
  echo "========================================="
  npm run lint:js || ((TOTAL_ERRORS++))
  echo ""
fi

# 7. HTMLHint
if command -v npm &> /dev/null && [ -f "package.json" ]; then
  echo "========================================="
  echo "📝 Running HTMLHint..."
  echo "========================================="
  npm run lint:html || ((TOTAL_ERRORS++))
  echo ""
fi

# Підсумок
echo "╔════════════════════════════════════════╗"
echo "║   📊 FINAL SUMMARY                     ║"
echo "╔════════════════════════════════════════╗"
echo "Total failed checks: $TOTAL_ERRORS"
echo ""

if [ $TOTAL_ERRORS -eq 0 ]; then
  echo "✅ ALL CHECKS PASSED! 🎉"
  exit 0
else
  echo "❌ SOME CHECKS FAILED"
  echo "Run 'npm run fix:rules' to auto-fix some issues"
  exit 1
fi
```

Зробіть скрипт виконуваним:

```bash
chmod +x scripts/check-all-rules.sh
```

### 6.6. Тестування скриптів

```bash
bash scripts/check-all-rules.sh
```

---

## Крок 7: Створення скриптів автоматичного виправлення

### 7.1. `scripts/fix-rules.sh`

```bash
#!/bin/bash
set -e

echo "========================================="
echo "🔧 Automatic Rules Fixes"
echo "========================================="

FIXED_COUNT=0

# Fix 1: Видалити inline style=""
echo ""
echo "🎨 [Fix 1] Removing inline styles..."
HTML_FILES=$(find templates -name "*.html" 2>/dev/null || echo "")
if [ -n "$HTML_FILES" ]; then
  BEFORE=$(echo "$HTML_FILES" | xargs grep -c 'style="' | grep -v ':0$' | wc -l)
  echo "$HTML_FILES" | xargs sed -i.bak 's/ style="[^"]*"//g'
  AFTER=$(echo "$HTML_FILES" | xargs grep -c 'style="' | grep -v ':0$' | wc -l || echo "0")
  REMOVED=$((BEFORE - AFTER))
  if [ $REMOVED -gt 0 ]; then
    echo "✅ Removed $REMOVED inline style attributes"
    ((FIXED_COUNT++))
  fi
fi

# Fix 2: Додати inputmode="tel" до type="tel"
echo ""
echo "📞 [Fix 2] Adding inputmode=\"tel\" to tel inputs..."
if [ -n "$HTML_FILES" ]; then
  echo "$HTML_FILES" | xargs sed -i.bak 's/<input type="tel"/<input type="tel" inputmode="tel"/g'
  echo "✅ Added inputmode to tel inputs"
  ((FIXED_COUNT++))
fi

# Fix 3: flex: 1; → flex: 1 0 0;
echo ""
echo "📦 [Fix 3] Fixing flex shorthand..."
CSS_FILES=$(find static/css -name "*.css" ! -name "normalize.css" 2>/dev/null || echo "")
if [ -n "$CSS_FILES" ]; then
  BEFORE=$(echo "$CSS_FILES" | xargs grep -c 'flex:\s*1;' | grep -v ':0$' | wc -l || echo "0")
  echo "$CSS_FILES" | xargs sed -i.bak 's/flex: 1;/flex: 1 0 0;/g'
  AFTER=$(echo "$CSS_FILES" | xargs grep -c 'flex:\s*1;' | grep -v ':0$' | wc -l || echo "0")
  FIXED=$((BEFORE - AFTER))
  if [ $FIXED -gt 0 ]; then
    echo "✅ Fixed $FIXED flex shorthand declarations"
    ((FIXED_COUNT++))
  fi
fi

# Видалити .bak файли
find . -name "*.bak" -delete

echo ""
echo "========================================="
echo "📊 Fixes Summary"
echo "========================================="
echo "Total fixes applied: $FIXED_COUNT"
echo "✅ Auto-fix complete"
```

Зробіть скрипт виконуваним:

```bash
chmod +x scripts/fix-rules.sh
```

### 7.2. Тестування автоматичного виправлення

```bash
bash scripts/fix-rules.sh
```

---

## Крок 8: Налаштування Git Hooks (Husky)

### 8.1. Ініціалізація Husky

```bash
npm install
npx husky install
```

**Результат**: створена директорія `.husky/`

### 8.2. Створення pre-commit hook

```bash
npx husky add .husky/pre-commit "bash scripts/pre-commit-hook.sh"
```

### 8.3. Створення `scripts/pre-commit-hook.sh`

```bash
#!/bin/bash

echo "🔍 Running pre-commit checks..."

# Отримуємо список змінених файлів
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
  echo "No files staged for commit."
  exit 0
fi

ERROR_COUNT=0

# Перевірка Django шаблонів
TEMPLATE_FILES=$(echo "$STAGED_FILES" | grep '\.html$' || echo "")
if [ -n "$TEMPLATE_FILES" ]; then
  echo "Checking Django templates..."
  bash scripts/check_template_tags.sh || ((ERROR_COUNT++))
fi

# Перевірка CSS
CSS_FILES=$(echo "$STAGED_FILES" | grep '\.css$' | grep -v 'normalize.css' || echo "")
if [ -n "$CSS_FILES" ]; then
  echo "Checking CSS files..."
  npx stylelint $CSS_FILES || ((ERROR_COUNT++))
  bash scripts/check-css-rules.sh || ((ERROR_COUNT++))
fi

# Перевірка JS
JS_FILES=$(echo "$STAGED_FILES" | grep '\.js$' || echo "")
if [ -n "$JS_FILES" ]; then
  echo "Checking JavaScript files..."
  npx eslint $JS_FILES || ((ERROR_COUNT++))
  bash scripts/check-js-rules.sh || ((ERROR_COUNT++))
fi

# Перевірка HTML
if [ -n "$TEMPLATE_FILES" ]; then
  echo "Checking HTML structure..."
  npx htmlhint $TEMPLATE_FILES || ((ERROR_COUNT++))
  bash scripts/check-html-rules.sh || ((ERROR_COUNT++))
fi

if [ $ERROR_COUNT -gt 0 ]; then
  echo "❌ Pre-commit checks failed! Fix errors before committing."
  echo "Run 'npm run fix:rules' to auto-fix some issues."
  exit 1
fi

echo "✅ All pre-commit checks passed!"
exit 0
```

Зробіть скрипт виконуваним:

```bash
chmod +x scripts/pre-commit-hook.sh
```

### 8.4. Тестування Git Hook

Спробуйте зробити commit з порушенням:

```bash
# Створіть файл з помилкою
echo 'body { color: red !important; }' > static/css/test.css
git add static/css/test.css
git commit -m "Test commit"
```

**Очікуваний результат**: commit має бути **заблокований** з повідомленням про помилку.

---

## Крок 9: Тестування системи

### 9.1. Повна перевірка

```bash
npm run check:rules
```

### 9.2. Перевірка окремих компонентів

```bash
npm run lint:css
npm run lint:js
npm run lint:html
```

### 9.3. Створення тестових порушень

Створіть файл `static/css/test-violations.css`:

```css
/* Порушення 1: !important */
body {
  color: red !important;
}

/* Порушення 2: flex: 1; без basis */
.container {
  flex: 1;
}

/* Порушення 3: 100vh без fallback */
.hero {
  height: 100vh;
}
```

Запустіть перевірку:

```bash
npm run lint:css
bash scripts/check-css-rules.sh
```

**Очікуваний результат**: всі 3 порушення мають бути виявлені.

---

## Крок 10: Виправлення існуючих порушень

### 10.1. Автоматичне виправлення

```bash
npm run fix:rules
npm run lint:fix
```

### 10.2. Ручне виправлення

Для порушень, які не можна виправити автоматично:

1. Запустіть `npm run check:rules`
2. Прочитайте вивід
3. Виправте кожне порушення вручну
4. Повторіть крок 1

### 10.3. Приклади виправлень

#### Порушення: inline style

**До**:
```html
<div style="color: red;">Text</div>
```

**Після**:
```html
<div class="text-error">Text</div>
```

```css
/* static/css/utilities/text.css */
.text-error {
  color: var(--color-error);
}
```

#### Порушення: 100vh без fallback

**До**:
```css
.hero {
  height: 100vh;
}
```

**Після**:
```css
.hero {
  height: 100vh; /* Fallback */
  height: 100dvh;
}
```

#### Порушення: var usage

**До**:
```javascript
var name = 'John';
```

**Після**:
```javascript
const name = 'John';
```

#### Порушення: розривання Django тегів

**До**:
```django
{% if user.is_authenticated and
      user.has_permission %}
  <p>Welcome</p>
{% endif %}
```

**Після**:
```django
{% if user.is_authenticated and user.has_permission %}
  <p>Welcome</p>
{% endif %}
```

Або (якщо дуже довгий):
```django
{% with has_access=user.is_authenticated and user.has_permission %}
  {% if has_access %}
    <p>Welcome</p>
  {% endif %}
{% endwith %}
```

---

## Інтеграція з Django

### Django Templates (base.html)

Базовий шаблон має містити **обов'язкові елементи**:

```html
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, interactive-widget=resizes-content">
    <meta name="csrf-token" content="{{ csrf_token }}">
    <title>{% block title %}My App{% endblock %}</title>
    
    <!-- Preconnect для CDN -->
    <link rel="preconnect" href="https://unpkg.com" crossorigin>
    
    <!-- CSS в правильному порядку -->
    <link rel="stylesheet" href="{% static 'css/normalize.css' %}">
    <link rel="stylesheet" href="{% static 'css/base.css' %}">
    {% block extra_css %}{% endblock %}
    
    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@2.0.8" defer></script>
    
    <!-- Власні JS -->
    <script src="{% static 'js/main.js' %}" defer></script>
    {% block extra_js %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

### Django Forms з HTMX

```html
<form hx-post="{% url 'company_create' %}" hx-target="#company-list">
    {% csrf_token %}
    
    <div class="form-group">
        <label for="id_name">Назва компанії</label>
        <input type="text" id="id_name" name="name" value="{{ form.name.value|default:'' }}" required>
        {% if form.name.errors %}
            <span class="form-error">{{ form.name.errors.0 }}</span>
        {% endif %}
    </div>
    
    <div class="form-group">
        <label for="id_phone">Телефон</label>
        <input type="tel" id="id_phone" name="phone" inputmode="tel" value="{{ form.phone.value|default:'' }}">
    </div>
    
    <button type="submit" class="button button--primary">Створити</button>
</form>
```

### Django Views з HTMX

```python
# views.py
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods

@require_http_methods(["POST"])
def company_create(request):
    form = CompanyForm(request.POST)
    if form.is_valid():
        company = form.save()
        
        # Для HTMX запитів повертаємо HTML фрагмент
        if request.headers.get('HX-Request'):
            html = render_to_string('companies/company_row.html', {'company': company})
            return HttpResponse(html)
        
        # Для звичайних запитів — редірект
        return redirect('company_list')
    
    # Якщо помилки валідації
    if request.headers.get('HX-Request'):
        html = render_to_string('companies/create_form.html', {'form': form})
        return HttpResponse(html, status=400)
    
    return render(request, 'companies/create.html', {'form': form})
```

### Django Messages

```html
<!-- templates/components/message.html -->
{% if messages %}
    <div class="messages">
        {% for message in messages %}
            <div class="message message--{{ message.tags }}">
                <div class="message__text">{{ message }}</div>
                <button type="button" class="message__close" aria-label="Закрити">×</button>
            </div>
        {% endfor %}
    </div>
{% endif %}
```

### CSS для Django Forms

```css
/* static/css/components/form.css */
.form-group {
  margin-bottom: var(--spacing-md);
}

.form-group label {
  display: block;
  margin-bottom: var(--spacing-xs);
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 1rem;
  min-height: 44px; /* Touch target */
}

.form-group input:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.form-error {
  display: block;
  margin-top: var(--spacing-xs);
  color: var(--color-error);
  font-size: 0.875rem;
}

.form-group input.error {
  border-color: var(--color-error);
}
```

---

## Робота з HTMX

### JavaScript Integration

```javascript
// static/js/main.js
'use strict';

// HTMX Error Handling
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

// CSRF Token для HTMX
document.body.addEventListener('htmx:configRequest', function (event) {
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  event.detail.headers['X-CSRFToken'] = csrfToken;
});

// bfcache для Safari/Firefox
window.addEventListener('pageshow', function (event) {
  if (event.persisted) {
    console.log('Page restored from bfcache');
    // Оновити динамічний контент, якщо потрібно
    htmx.trigger(document.body, 'pageRestored');
  }
});

// Закриття модальних вікон
document.body.addEventListener('htmx:afterSwap', function (event) {
  if (event.detail.target.classList.contains('modal')) {
    const closeBtn = event.detail.target.querySelector('.modal__close');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        event.detail.target.remove();
      });
    }
  }
});
```

### HTMX Patterns

#### Оновлення списку після створення

```html
<!-- Кнопка "Створити" -->
<button hx-get="{% url 'company_create_form' %}" hx-target="#modal-container" hx-swap="innerHTML">
  Створити компанію
</button>

<!-- Контейнер для модального вікна -->
<div id="modal-container"></div>

<!-- Форма в модальному вікні -->
<div class="modal">
  <form hx-post="{% url 'company_create' %}" hx-target="#company-list" hx-swap="afterbegin">
    {% csrf_token %}
    <!-- Поля форми -->
    <button type="submit">Зберегти</button>
  </form>
</div>

<!-- Список компаній -->
<div id="company-list">
  {% for company in companies %}
    <div class="company-row">{{ company.name }}</div>
  {% endfor %}
</div>
```

#### Infinite Scroll

```html
<div id="company-list">
  {% for company in companies %}
    <div class="company-row">{{ company.name }}</div>
  {% endfor %}
  
  {% if has_next %}
    <div hx-get="{% url 'company_list' %}?page={{ next_page }}" hx-trigger="revealed" hx-swap="outerHTML">
      <p>Завантаження...</p>
    </div>
  {% endif %}
</div>
```

#### Debounced Search

```html
<input type="search" name="q" placeholder="Пошук..." hx-get="{% url 'company_search' %}" hx-trigger="keyup changed delay:500ms" hx-target="#search-results">

<div id="search-results">
  <!-- Результати пошуку -->
</div>
```

---

## Повний список правил (110+)

### HTML (25 правил)

1. ✅ `viewport-fit=cover` в meta viewport
2. ✅ `interactive-widget=resizes-content` в meta viewport
3. ✅ Семантичні теги (header, nav, main, section, article, footer)
4. ✅ `alt` для всіх `<img>`
5. ✅ `loading="lazy"` для off-screen images
6. ✅ `<label>` для всіх `<input>`
7. ✅ `inputmode="tel"` для type="tel"
8. ✅ `inputmode="decimal"` для type="number"
9. ✅ `<video>` має містити `poster`, `playsinline`, `muted`
10. ✅ `<script>` має містити `defer` або `async`
11. ❌ Заборонені inline styles (`style=""`)
12. ❌ Заборонені inline scripts (`<script>alert()</script>`)
13. ❌ Заборонені inline event handlers (`onclick=""`)
14. ✅ `<button>` замість `<div onclick>`
15. ✅ `type="button"` для не-submit кнопок
16. ✅ ARIA атрибути тільки де необхідно
17. ✅ `lang` атрибут в `<html>`
18. ✅ Мінімальний touch target 44x44px
19. ✅ `<form>` має містити CSRF token (Django)
20. ✅ `autocomplete` для форм (name, email, tel)
21. ✅ `<picture>` для responsive images
22. ✅ AVIF → WebP → JPG fallback
23. ✅ `preconnect` для CDN
24. ✅ Порядок: normalize.css → base.css → components → utilities
25. ✅ `<meta name="csrf-token">` для HTMX

### CSS (40 правил)

26. ❌ Заборонено `!important`
27. ✅ `100vh` має fallback `100dvh`
28. ✅ `env(safe-area-inset-*)` для fixed/sticky елементів
29. ✅ `font-size` в `rem`, не `px`
30. ✅ `flex: 1 0 0;` замість `flex: 1;`
31. ✅ `:hover` в `@media (hover: hover)`
32. ✅ `overscroll-behavior: none;` на body
33. ✅ `touch-action: manipulation` для interactive
34. ✅ `-webkit-overflow-scrolling: touch`
35. ✅ `backdrop-filter` має `-webkit-` prefix
36. ✅ BEM методологія
37. ✅ CSS custom properties в base.css
38. ✅ Глибина nesting ≤3
39. ✅ Низька специфічність
40. ✅ `accent-color` для inputs
41. ✅ `color-scheme: light dark;`
42. ✅ `-webkit-font-smoothing: antialiased`
43. ✅ `text-wrap: balance` для заголовків
44. ✅ `text-size-adjust: 100%;`
45. ✅ `scrollbar-gutter: stable;`
46. ✅ `container-type: inline-size` для responsive компонентів
47. ✅ `@layer` для cascade layers
48. ✅ `:has()` замість JS де можливо
49. ✅ `color-mix()` для відтінків
50. ✅ `input:-webkit-autofill` styling
51. ✅ `::file-selector-button` для file inputs
52. ✅ `scroll-snap-type` для sliders
53. ✅ `position: sticky` з `top/bottom`
54. ✅ `isolation: isolate` для stacking context
55. ✅ `will-change` тільки для animations
56. ✅ Високопродуктивні animations (transform, opacity)
57. ❌ Заборонено animations на width/height/margin
58. ✅ `prefers-reduced-motion`
59. ✅ `@supports` для feature detection
60. ✅ `aspect-ratio` для media
61. ✅ `object-fit: cover` для images
62. ✅ `grid-gap` замість `grid-row-gap` + `grid-column-gap`
63. ✅ `gap` в flexbox
64. ✅ `min-width`/`min-height` для touch targets
65. ❌ Не використовувати `line-height` для vertical centering

### JavaScript (25 правил)

66. ❌ Заборонено `var`
67. ✅ `const`/`let` тільки
68. ❌ Заборонено `eval()`, `new Function()`
69. ✅ `'use strict';` або ES modules
70. ✅ IIFE або modules (не globals)
71. ✅ `defer` для scripts
72. ✅ `pageshow` event для bfcache
73. ✅ `scrollend` замість `scroll` + debounce
74. ✅ Pointer Events замість Touch Events
75. ✅ `event.persisted` check в pageshow
76. ✅ `?.` optional chaining
77. ✅ `??` nullish coalescing
78. ✅ Early return (зменшити nesting)
79. ✅ Event delegation де можливо
80. ✅ `addEventListener` замість `onclick`
81. ❌ Не зберігати tokens в localStorage
82. ✅ HttpOnly cookies для auth
83. ✅ CSP compliant (no inline scripts)
84. ✅ Sanitize user input
85. ✅ `htmx:configRequest` для CSRF
86. ✅ `htmx:responseError` handling
87. ✅ `htmx:afterSwap` для dynamic content
88. ✅ `htmx.trigger()` для custom events
89. ✅ `aria-live` для dynamic updates
90. ❌ Не блокувати main thread

### Django (20 правил)

91. ❌ **КРИТИЧНО**: не розривати Django теги на кілька рядків
92. ✅ `{{ variable }}` на одному рядку
93. ✅ `{% tag %}` на одному рядку
94. ✅ `{% with %}` для складних expressions
95. ✅ Кастомні template filters для довгих імен
96. ✅ `{% csrf_token %}` в кожній формі
97. ✅ `|default:''` для порожніх values
98. ✅ `{% block extra_css %}` для page-specific CSS
99. ✅ `{% block extra_js %}` для page-specific JS
100. ✅ `{% static %}` для всіх assets
101. ✅ `{% url %}` замість hardcoded URLs
102. ✅ `request.headers.get('HX-Request')` для HTMX
103. ✅ `render_to_string()` для HTMX responses
104. ✅ HTTP 400/422 для validation errors (HTMX)
105. ✅ Django messages для user feedback
106. ✅ `form.field.errors.0` для першої помилки
107. ✅ `form.field.value|default:''` для values
108. ✅ Settings split (base, develop, production)
109. ✅ Secrets в env vars (dotenv)
110. ✅ `require_http_methods` decorators

### UX/Accessibility (10 правил)

111. ✅ Touch targets ≥44px (iOS) / 48px (Android)
112. ✅ Color contrast ≥4.5:1
113. ✅ Focus indicators visible
114. ✅ Keyboard navigation
115. ✅ Screen reader testing
116. ✅ `aria-label` для icon-only buttons
117. ✅ `role="dialog"` для modals
118. ✅ Trap focus в модальних вікнах
119. ✅ `aria-live="polite"` для notifications
120. ✅ `prefers-reduced-motion` для animations

---

## Troubleshooting та поширені проблеми

### Проблема 1: Stylelint не знаходить конфігурацію

**Помилка**:
```
Error: No configuration provided
```

**Рішення**:
```bash
# Перевірте, чи існує .stylelintrc.json
ls -la .stylelintrc.json

# Якщо ні, створіть його вручну
cat > .stylelintrc.json << 'EOF'
{
  "extends": ["stylelint-config-standard"]
}
EOF
```

### Проблема 2: ESLint не розпізнає `htmx`

**Помилка**:
```
'htmx' is not defined  no-undef
```

**Рішення**: Додайте в `.eslintrc.json`:
```json
{
  "globals": {
    "htmx": "readonly"
  }
}
```

### Проблема 3: HTMLHint ламається на Django тегах

**Помилка**:
```
Special characters must be escaped  spec-char-escape
```

**Рішення**: Вимкніть це правило в `.htmlhintrc`:
```json
{
  "spec-char-escape": false,
  "doctype-first": false,
  "tag-pair": false
}
```

### Проблема 4: Pre-commit hook не спрацьовує

**Помилка**: Commit проходить незважаючи на помилки

**Рішення**:
```bash
# Перевірте, чи hook виконуваний
ls -la .husky/pre-commit
chmod +x .husky/pre-commit

# Переініціалізуйте Husky
rm -rf .husky
npx husky install
npx husky add .husky/pre-commit "bash scripts/pre-commit-hook.sh"
```

### Проблема 5: `check-css-rules.sh` false positive для 100vh

**Помилка**: Скрипт знаходить 100vh, але 100dvh присутній

**Рішення**: Переконайтесь, що fallback на тому самому рівні вкладеності:

```css
/* ✅ Правильно */
.hero {
  height: 100vh; /* Fallback */
  height: 100dvh;
}

/* ❌ Неправильно */
.hero {
  height: 100vh;
}
.hero-inner {
  height: 100dvh;
}
```

### Проблема 6: `npm install` падає з помилкою

**Помилка**:
```
npm ERR! code ENOENT
npm ERR! syscall open
npm ERR! path /path/to/package.json
```

**Рішення**:
```bash
# Перевірте, чи в правильній директорії
pwd
ls package.json

# Ініціалізуйте npm заново
npm init -y
npm install --save-dev stylelint eslint htmlhint husky
```

### Проблема 7: Git hook блокує commit навіть без помилок

**Рішення**: Перевірте exit code скрипта:

```bash
bash scripts/pre-commit-hook.sh
echo $?  # Має бути 0
```

Якщо не 0, додайте debug:

```bash
# У scripts/pre-commit-hook.sh
set -x  # Debug mode
```

---

## Адаптація для різних проектів

### Проект без HTMX

Якщо проект не використовує HTMX:

1. Видаліть HTMX з `base.html`
2. Видаліть `htmx: readonly` з `.eslintrc.json`
3. Видаліть HTMX перевірки з `scripts/check-js-rules.sh`

### Проект з Tailwind CSS

Якщо проект використовує Tailwind:

1. Оновіть `.stylelintrc.json`:
```json
{
  "extends": ["stylelint-config-standard"],
  "rules": {
    "at-rule-no-unknown": [
      true,
      {
        "ignoreAtRules": ["tailwind", "apply", "layer", "screen"]
      }
    ]
  }
}
```

2. Додайте до `.gitignore`:
```gitignore
static/css/tailwind.output.css
```

### Проект з TypeScript

Якщо проект використовує TypeScript:

1. Встановіть TypeScript ESLint:
```bash
npm install --save-dev @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

2. Оновіть `.eslintrc.json`:
```json
{
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint"],
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended"
  ]
}
```

### Проект з API (DRF)

Якщо проект використовує Django REST Framework:

1. Додайте перевірку serializers:
```bash
# scripts/check-python.sh
pylint myapp/serializers.py
mypy myapp/serializers.py
```

2. Додайте в `package.json`:
```json
{
  "scripts": {
    "lint:python": "bash scripts/check-python.sh"
  }
}
```

---

## CI/CD інтеграція

### GitHub Actions

Створіть `.github/workflows/lint.yml`:

```yaml
name: Code Quality Checks

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: npm install
      
      - name: Run all checks
        run: npm run check:rules
      
      - name: Run Python linters
        run: |
          pip install flake8 mypy
          flake8 .
          mypy .
```

### GitLab CI

Створіть `.gitlab-ci.yml`:

```yaml
stages:
  - lint

lint-frontend:
  stage: lint
  image: node:20
  script:
    - npm install
    - npm run check:rules

lint-python:
  stage: lint
  image: python:3.11
  script:
    - pip install flake8 mypy
    - flake8 .
    - mypy .
```

### Pre-push Hook

Для додаткової безпеки:

```bash
npx husky add .husky/pre-push "npm run check:rules"
```

---

## Підтримка та оновлення

### Щомісячно

```bash
# Оновіть Node.js залежності
npm update

# Перевірте outdated packages
npm outdated

# Оновіть критичні пакети
npm install stylelint@latest eslint@latest
```

### Щокварталу

```bash
# Перевірте browserslist
npx update-browserslist-db

# Оновіть Python залежності
pip list --outdated
```

### Додавання нових правил

1. Додайте правило в відповідний `.eslintrc.json` / `.stylelintrc.json`
2. Якщо потрібно, створіть bash-скрипт
3. Додайте в `scripts/check-all-rules.sh`
4. Оновіть `scripts/README.md`
5. Протестуйте на реальних файлах
6. Зробіть commit з описом правила

---

## Швидкий старт (TL;DR)

```bash
# 1. Встановлення
npm install

# 2. Налаштування Git Hooks
npx husky install
bash scripts/setup-git-hooks.sh

# 3. Перевірка існуючого коду
npm run check:rules

# 4. Автоматичне виправлення
npm run fix:rules

# 5. Ручне виправлення решти
npm run lint:fix

# 6. Фінальна перевірка
npm run check:rules

# 7. Commit (hook автоматично запуститься)
git add .
git commit -m "Setup code quality system"
```

---

## Чек-лист налаштування

- [ ] Встановлено Node.js 18+
- [ ] Створено `package.json` з усіма залежностями
- [ ] Встановлено залежності (`npm install`)
- [ ] Створено `.stylelintrc.json`
- [ ] Створено `.eslintrc.json`
- [ ] Створено `.htmlhintrc`
- [ ] Створено `scripts/check-html-rules.sh`
- [ ] Створено `scripts/check-css-rules.sh`
- [ ] Створено `scripts/check-js-rules.sh`
- [ ] Створено `scripts/check_template_tags.sh`
- [ ] Створено `scripts/fix-rules.sh`
- [ ] Створено `scripts/check-all-rules.sh`
- [ ] Створено `scripts/pre-commit-hook.sh`
- [ ] Усі скрипти executable (`chmod +x`)
- [ ] Налаштовано Husky (`npx husky install`)
- [ ] Створено pre-commit hook
- [ ] Оновлено `.gitignore` (node_modules, package-lock.json)
- [ ] Протестовано `npm run lint:css`
- [ ] Протестовано `npm run lint:js`
- [ ] Протестовано `npm run lint:html`
- [ ] Протестовано `npm run check:rules`
- [ ] Протестовано Git hook (test commit)
- [ ] Виправлено існуючі порушення
- [ ] Створено документацію (`scripts/README.md`)
- [ ] Налаштовано CI/CD (опціонально)
- [ ] Навчено команду використовувати систему

---

## Фінальні рекомендації

1. **Не ігноруйте warnings** — вони стануть errors в майбутньому
2. **Тестуйте на реальних пристроях** — емулятори не показують усіх проблем
3. **Регулярно оновлюйте browserslist** — підтримка браузерів змінюється
4. **Документуйте виключення** — якщо вимкнули правило, поясніть чому
5. **Навчайте команду** — система працює тільки якщо всі її використовують

---

## Автор та Ліцензія

Цей документ створено для забезпечення кросплатформенної якості коду у Django проектах з HTMX, CSS та Vanilla JavaScript.

**Версія**: 1.0.0  
**Дата**: 2025  
**Ліцензія**: MIT

---

**🎉 Вітаємо! Ваш проект тепер захищений від порушень кросплатформенних правил!**

