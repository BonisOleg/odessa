# Повна інструкція налаштування системи автоматичних перевірок (Ultimate Edition 2025)

**Версія:** 1.0  
**Дата:** Грудень 2025  
**Призначення:** Налаштування системи, яка фізично блокує порушення правил кросплатформної розробки

---

## 📋 Зміст

1. [Огляд системи](#огляд-системи)
2. [Крок 1: Підготовка проекту](#крок-1-підготовка-проекту)
3. [Крок 2: Встановлення залежностей](#крок-2-встановлення-залежностей)
4. [Крок 3: Створення конфігурацій linters](#крок-3-створення-конфігурацій-linters)
5. [Крок 4: Створення скриптів перевірки](#крок-4-створення-скриптів-перевірки)
6. [Крок 5: Налаштування Git Hooks](#крок-5-налаштування-git-hooks)
7. [Крок 6: Виправлення існуючих порушень](#крок-6-виправлення-існуючих-порушень)
8. [Крок 7: Тестування системи](#крок-7-тестування-системи)
9. [Повний список правил](#повний-список-правил)
10. [Troubleshooting](#troubleshooting)

---

## Огляд системи

### Що робить система

Система автоматично перевіряє та блокує порушення правил кросплатформної розробки через:

- **Pre-commit hooks** - блокування комітів з порушеннями
- **Linters** (Stylelint, ESLint, HTMLHint) - перевірка синтаксису
- **Custom скрипти** - глибока перевірка правил з посібників
- **Автоматичні виправлення** - де можливо

### Що перевіряється

- ✅ HTML: viewport meta, inputmode, inline styles/scripts
- ✅ CSS: 100vh → 100dvh, flex-basis, hover медіа-запити, !important
- ✅ JavaScript: var, bfcache, strict mode
- ✅ Django templates: розриви тегів

---

## Крок 1: Підготовка проекту

### 1.1 Перевірка структури

Переконайтеся, що у вас є:
- Корінь проекту з `.git`
- Директорія `static/` або `assets/` для CSS/JS
- Директорія `templates/` або `src/` для HTML
- Файл `.gitignore`

### 1.2 Оновлення .gitignore

Додайте до `.gitignore`:

```gitignore
# Node.js
node_modules/
package-lock.json
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Backup files
*.bak
*.tmp
```

---

## Крок 2: Встановлення залежностей

### 2.1 Створення package.json

Створіть файл `package.json` в корені проекту:

```json
{
  "name": "project-linters",
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

**Важливо:** Адаптуйте шляхи (`static/css/**/*.css`, `templates/**/*.html`) під структуру вашого проекту!

### 2.2 Встановлення залежностей

```bash
npm install
```

---

## Крок 3: Створення конфігурацій linters

### 3.1 .stylelintrc.json

Створіть файл `.stylelintrc.json`:

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
        "ignore": ["css-nesting", "css-has", "viewport-units", "css-overscroll-behavior", "text-size-adjust"]
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

**Адаптація:** Змініть `ignoreFiles` на ваші файли, які не потрібно перевіряти (наприклад, vendor CSS).

### 3.2 .eslintrc.json

Створіть файл `.eslintrc.json`:

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

**Адаптація:** Додайте до `globals` ваші глобальні змінні (наприклад, `jQuery`, `Vue` тощо).

### 3.3 .htmlhintrc

Створіть файл `.htmlhintrc`:

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

**Примітка:** `tag-pair: false` та `spec-char-escape: false` для Django/шаблонів, які використовують `{{ }}` та `{% %}`.

---

## Крок 4: Створення скриптів перевірки

### 4.1 Створення директорії scripts

```bash
mkdir -p scripts
```

### 4.2 scripts/check-html-rules.sh

Створіть файл `scripts/check-html-rules.sh`:

```bash
#!/bin/bash
# Перевірка HTML правил з кросплатформного посібника

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ERRORS=0

echo "🔍 Перевірка HTML правил (Ultimate Edition 2025)..."
echo ""

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# АДАПТАЦІЯ: Змініть шлях до вашого базового шаблону
BASE_TEMPLATE="$REPO_ROOT/templates/base.html"
if [ ! -f "$BASE_TEMPLATE" ]; then
    BASE_TEMPLATE="$REPO_ROOT/src/index.html"
fi

# Перевірка 1: Viewport meta має містити необхідні атрибути
echo "📱 Перевірка viewport meta..."
if [ -f "$BASE_TEMPLATE" ]; then
    if grep -r "viewport" "$BASE_TEMPLATE" | grep -q "interactive-widget=resizes-content"; then
        echo -e "${GREEN}✅ Viewport meta містить interactive-widget=resizes-content${NC}"
    else
        echo -e "${RED}❌ ПОМИЛКА: Viewport meta не містить interactive-widget=resizes-content${NC}"
        echo "   Додайте: interactive-widget=resizes-content"
        ERRORS=$((ERRORS + 1))
    fi

    if grep -r "viewport" "$BASE_TEMPLATE" | grep -q "viewport-fit=cover"; then
        echo -e "${GREEN}✅ Viewport meta містить viewport-fit=cover${NC}"
    else
        echo -e "${RED}❌ ПОМИЛКА: Viewport meta не містить viewport-fit=cover${NC}"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo -e "${YELLOW}⚠️  Базовий шаблон не знайдено: $BASE_TEMPLATE${NC}"
fi

# Перевірка 2: Inline styles заборонені
echo ""
echo "🎨 Перевірка inline styles..."
# АДАПТАЦІЯ: Змініть шлях до ваших HTML файлів
INLINE_STYLES=$(grep -r 'style=' "$REPO_ROOT/templates" --include="*.html" --exclude-dir=".git" 2>/dev/null || true)
if [ -z "$INLINE_STYLES" ]; then
    INLINE_STYLES=$(grep -r 'style=' "$REPO_ROOT/src" --include="*.html" --exclude-dir=".git" 2>/dev/null || true)
fi

if [ -n "$INLINE_STYLES" ]; then
    echo -e "${RED}❌ ПОМИЛКА: Знайдено inline styles (ЗАБОРОНЕНО):${NC}"
    echo "$INLINE_STYLES"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ Inline styles не знайдено${NC}"
fi

# Перевірка 3: Inline scripts заборонені
echo ""
echo "📜 Перевірка inline scripts..."
INLINE_SCRIPTS=$(grep -r '<script[^>]*>' "$REPO_ROOT/templates" --include="*.html" 2>/dev/null | grep -v 'src=' | grep -v 'defer' || true)
if [ -z "$INLINE_SCRIPTS" ]; then
    INLINE_SCRIPTS=$(grep -r '<script[^>]*>' "$REPO_ROOT/src" --include="*.html" 2>/dev/null | grep -v 'src=' | grep -v 'defer' || true)
fi

if [ -n "$INLINE_SCRIPTS" ]; then
    echo -e "${RED}❌ ПОМИЛКА: Знайдено inline scripts (ЗАБОРОНЕНО):${NC}"
    echo "$INLINE_SCRIPTS"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ Inline scripts не знайдено${NC}"
fi

# Перевірка 4: inputmode для tel полів
echo ""
echo "⌨️  Перевірка inputmode для type=\"tel\"..."
TEL_WITHOUT_INPUTMODE=$(grep -r 'type="tel"' "$REPO_ROOT/templates" --include="*.html" 2>/dev/null | grep -v 'inputmode=' || true)
if [ -z "$TEL_WITHOUT_INPUTMODE" ]; then
    TEL_WITHOUT_INPUTMODE=$(grep -r 'type="tel"' "$REPO_ROOT/src" --include="*.html" 2>/dev/null | grep -v 'inputmode=' || true)
fi

if [ -n "$TEL_WITHOUT_INPUTMODE" ]; then
    echo -e "${RED}❌ ПОМИЛКА: type=\"tel\" без inputmode (ЗАБОРОНЕНО):${NC}"
    echo "$TEL_WITHOUT_INPUTMODE"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ Всі type=\"tel\" мають inputmode${NC}"
fi

# Перевірка 5: inputmode для number полів
echo ""
echo "🔢 Перевірка inputmode для type=\"number\"..."
NUMBER_WITHOUT_INPUTMODE=$(grep -r 'type="number"' "$REPO_ROOT/templates" --include="*.html" 2>/dev/null | grep -v 'inputmode=' || true)
if [ -z "$NUMBER_WITHOUT_INPUTMODE" ]; then
    NUMBER_WITHOUT_INPUTMODE=$(grep -r 'type="number"' "$REPO_ROOT/src" --include="*.html" 2>/dev/null | grep -v 'inputmode=' || true)
fi

if [ -n "$NUMBER_WITHOUT_INPUTMODE" ]; then
    echo -e "${RED}❌ ПОМИЛКА: type=\"number\" без inputmode (ЗАБОРОНЕНО):${NC}"
    echo "$NUMBER_WITHOUT_INPUTMODE"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ Всі type=\"number\" мають inputmode${NC}"
fi

# Перевірка 6: video має poster
echo ""
echo "🎬 Перевірка <video> атрибутів..."
VIDEO_WITHOUT_POSTER=$(grep -r '<video' "$REPO_ROOT/templates" --include="*.html" 2>/dev/null | grep -v 'poster=' || true)
if [ -z "$VIDEO_WITHOUT_POSTER" ]; then
    VIDEO_WITHOUT_POSTER=$(grep -r '<video' "$REPO_ROOT/src" --include="*.html" 2>/dev/null | grep -v 'poster=' || true)
fi

if [ -n "$VIDEO_WITHOUT_POSTER" ]; then
    echo -e "${YELLOW}⚠️  УВАГА: <video> без poster атрибуту:${NC}"
    echo "$VIDEO_WITHOUT_POSTER"
fi

VIDEO_WITHOUT_PLAYSINLINE=$(grep -r '<video' "$REPO_ROOT/templates" --include="*.html" 2>/dev/null | grep -v 'playsinline' || true)
if [ -z "$VIDEO_WITHOUT_PLAYSINLINE" ]; then
    VIDEO_WITHOUT_PLAYSINLINE=$(grep -r '<video' "$REPO_ROOT/src" --include="*.html" 2>/dev/null | grep -v 'playsinline' || true)
fi

if [ -n "$VIDEO_WITHOUT_PLAYSINLINE" ]; then
    echo -e "${RED}❌ ПОМИЛКА: <video> без playsinline (ЗАБОРОНЕНО для iOS):${NC}"
    echo "$VIDEO_WITHOUT_PLAYSINLINE"
    ERRORS=$((ERRORS + 1))
fi

# Перевірка 7: Scripts мають defer
echo ""
echo "⏱️  Перевірка defer для scripts..."
SCRIPTS_WITHOUT_DEFER=$(grep -r '<script src=' "$REPO_ROOT/templates" --include="*.html" 2>/dev/null | grep -v 'defer' | grep -v 'async' || true)
if [ -z "$SCRIPTS_WITHOUT_DEFER" ]; then
    SCRIPTS_WITHOUT_DEFER=$(grep -r '<script src=' "$REPO_ROOT/src" --include="*.html" 2>/dev/null | grep -v 'defer' | grep -v 'async' || true)
fi

if [ -n "$SCRIPTS_WITHOUT_DEFER" ]; then
    echo -e "${RED}❌ ПОМИЛКА: <script> без defer/async:${NC}"
    echo "$SCRIPTS_WITHOUT_DEFER"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ Всі scripts мають defer${NC}"
fi

# Підсумок
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Всі HTML перевірки пройдено успішно!${NC}"
    exit 0
else
    echo -e "${RED}❌ Знайдено $ERRORS помилок HTML${NC}"
    exit 1
fi
```

**Адаптація:** Змініть шляхи `templates/` та `src/` на ваші директорії з HTML файлами.

### 4.3 scripts/check-css-rules.sh

Створіть файл `scripts/check-css-rules.sh`:

```bash
#!/bin/bash
# Перевірка CSS правил з кросплатформного посібника

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ERRORS=0

echo "🎨 Перевірка CSS правил (Ultimate Edition 2025)..."
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# АДАПТАЦІЯ: Змініть шлях до ваших CSS файлів
CSS_DIR="$REPO_ROOT/static/css"
if [ ! -d "$CSS_DIR" ]; then
    CSS_DIR="$REPO_ROOT/src/css"
fi
if [ ! -d "$CSS_DIR" ]; then
    CSS_DIR="$REPO_ROOT/assets/css"
fi

# АДАПТАЦІЯ: Змініть шлях до вашого базового CSS файлу
BASE_CSS="$CSS_DIR/base.css"
if [ ! -f "$BASE_CSS" ]; then
    BASE_CSS="$CSS_DIR/main.css"
fi
if [ ! -f "$BASE_CSS" ]; then
    BASE_CSS="$CSS_DIR/styles.css"
fi

# Перевірка 1: 100vh має мати fallback на 100dvh
echo "📐 Перевірка viewport units..."
VH_FILES=$(grep -r '100vh' "$CSS_DIR" --include="*.css" 2>/dev/null | cut -d: -f1 | sort -u || true)
VH_WITHOUT_DVH=""

if [ -n "$VH_FILES" ]; then
    for file in $VH_FILES; do
        # Перевіряємо чи є 100dvh в тому ж файлі
        if grep -q '100dvh' "$file" 2>/dev/null; then
            continue
        fi
        # Перевіряємо чи є коментар Fallback поруч
        VH_LINES=$(grep -n '100vh' "$file" 2>/dev/null | cut -d: -f1 || true)
        for line in $VH_LINES; do
            # Перевіряємо навколишні рядки (поточний, попередній, наступний)
            CONTEXT=$(sed -n "$((line-1)),$((line+1))p" "$file" 2>/dev/null | grep -i 'fallback\|100dvh' || true)
            if [ -z "$CONTEXT" ]; then
                VH_LINE=$(sed -n "${line}p" "$file" 2>/dev/null)
                VH_WITHOUT_DVH="${VH_WITHOUT_DVH}${file}:${line}: ${VH_LINE}\n"
            fi
        done
    done
fi

if [ -n "$VH_WITHOUT_DVH" ]; then
    echo -e "${RED}❌ ПОМИЛКА: 100vh без fallback на 100dvh:${NC}"
    echo -e "$VH_WITHOUT_DVH"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ Viewport units коректні${NC}"
fi

# Перевірка 2: Safe area insets
echo ""
echo "📱 Перевірка safe-area-inset..."
if [ -f "$BASE_CSS" ]; then
    SAFE_AREA=$(grep -r 'env(safe-area-inset' "$BASE_CSS" 2>/dev/null || true)
    if [ -z "$SAFE_AREA" ]; then
        echo -e "${RED}❌ ПОМИЛКА: Відсутні env(safe-area-inset-*) в $BASE_CSS${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✅ Safe area insets присутні${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Базовий CSS файл не знайдено: $BASE_CSS${NC}"
fi

# Перевірка 3: rem для font-size
echo ""
echo "🔤 Перевірка rem для font-size..."
# АДАПТАЦІЯ: Змініть назву файлу normalize.css на ваш
PX_FONT_SIZE=$(grep -r 'font-size.*px' "$CSS_DIR" --include="*.css" --exclude="normalize.css" 2>/dev/null | grep -v '/\*' | grep -v '16px' || true)
if [ -n "$PX_FONT_SIZE" ]; then
    echo -e "${YELLOW}⚠️  УВАГА: font-size в px (рекомендовано rem):${NC}"
    echo "$PX_FONT_SIZE"
fi

# Перевірка 4: flex без flex-basis
echo ""
echo "🔧 Перевірка flex-basis..."
FLEX_WITHOUT_BASIS=$(grep -r 'flex:\s*1\s*;' "$CSS_DIR" --include="*.css" 2>/dev/null || true)
if [ -n "$FLEX_WITHOUT_BASIS" ]; then
    echo -e "${RED}❌ ПОМИЛКА: flex: 1 без explicit flex-basis:${NC}"
    echo "$FLEX_WITHOUT_BASIS"
    echo "   Має бути: flex: 1 0 0 або flex: 1 0 auto"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ Flex properties коректні${NC}"
fi

# Перевірка 5: hover без media query
echo ""
echo "🖱️  Перевірка :hover в @media (hover: hover)..."
HOVER_WITHOUT_MEDIA=$(grep -r ':hover' "$CSS_DIR" --include="*.css" -A 2 -B 2 2>/dev/null | grep -v '@media.*hover' || true)
if [ -n "$HOVER_WITHOUT_MEDIA" ]; then
    echo -e "${YELLOW}⚠️  УВАГА: :hover без @media (hover: hover):${NC}"
    echo "   Може призвести до \"липкого\" hover на touchscreen"
fi

# Перевірка 6: overscroll-behavior
echo ""
echo "📜 Перевірка overscroll-behavior..."
if [ -f "$BASE_CSS" ]; then
    OVERSCROLL=$(grep -r 'overscroll-behavior' "$BASE_CSS" 2>/dev/null || true)
    if [ -z "$OVERSCROLL" ]; then
        echo -e "${YELLOW}⚠️  УВАГА: Відсутній overscroll-behavior в $BASE_CSS${NC}"
    else
        echo -e "${GREEN}✅ overscroll-behavior присутній${NC}"
    fi
fi

# Перевірка 7: !important
echo ""
echo "❗ Перевірка !important..."
# АДАПТАЦІЯ: Змініть список файлів для ігнорування
IMPORTANT=$(grep -r '!important' "$CSS_DIR" --include="*.css" --exclude="normalize.css" 2>/dev/null || true)
if [ -n "$IMPORTANT" ]; then
    echo -e "${RED}❌ ПОМИЛКА: Використання !important (ЗАБОРОНЕНО):${NC}"
    echo "$IMPORTANT"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ !important не використовується${NC}"
fi

# Перевірка 8: backdrop-filter з префіксом
echo ""
echo "🌫️  Перевірка backdrop-filter prefixes..."
BACKDROP_FILTER=$(grep -r 'backdrop-filter' "$CSS_DIR" --include="*.css" 2>/dev/null || true)
if [ -n "$BACKDROP_FILTER" ]; then
    WEBKIT_BACKDROP=$(echo "$BACKDROP_FILTER" | grep -c '-webkit-backdrop-filter' || true)
    if [ "$WEBKIT_BACKDROP" -eq 0 ]; then
        echo -e "${RED}❌ ПОМИЛКА: backdrop-filter без -webkit- префіксу${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✅ backdrop-filter має префікси${NC}"
    fi
fi

# Підсумок
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Всі CSS перевірки пройдено успішно!${NC}"
    exit 0
else
    echo -e "${RED}❌ Знайдено $ERRORS помилок CSS${NC}"
    exit 1
fi
```

**Адаптація:** Змініть шляхи `static/css/`, `src/css/`, `assets/css/` та назви файлів (`base.css`, `main.css`) під ваш проект.

### 4.4 scripts/check-js-rules.sh

Створіть файл `scripts/check-js-rules.sh`:

```bash
#!/bin/bash
# Перевірка JavaScript правил

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ERRORS=0

echo "📜 Перевірка JavaScript правил..."
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# АДАПТАЦІЯ: Змініть шлях до ваших JS файлів
JS_DIR="$REPO_ROOT/static/js"
if [ ! -d "$JS_DIR" ]; then
    JS_DIR="$REPO_ROOT/src/js"
fi
if [ ! -d "$JS_DIR" ]; then
    JS_DIR="$REPO_ROOT/assets/js"
fi

# АДАПТАЦІЯ: Змініть назву головного JS файлу
MAIN_JS="$JS_DIR/main.js"
if [ ! -f "$MAIN_JS" ]; then
    MAIN_JS="$JS_DIR/app.js"
fi
if [ ! -f "$MAIN_JS" ]; then
    MAIN_JS="$JS_DIR/index.js"
fi

# Перевірка 1: var заборонено
echo "🔤 Перевірка var (має бути const/let)..."
VAR_USAGE=$(grep -r '\bvar\b' "$JS_DIR" --include="*.js" 2>/dev/null || true)
if [ -n "$VAR_USAGE" ]; then
    echo -e "${RED}❌ ПОМИЛКА: Використання var (ЗАБОРОНЕНО):${NC}"
    echo "$VAR_USAGE"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ var не використовується${NC}"
fi

# Перевірка 2: pageshow для bfcache
echo ""
echo "💾 Перевірка pageshow event listener..."
if [ -f "$MAIN_JS" ]; then
    PAGESHOW=$(grep -r 'pageshow' "$MAIN_JS" 2>/dev/null || true)
    if [ -z "$PAGESHOW" ]; then
        echo -e "${YELLOW}⚠️  РЕКОМЕНДАЦІЯ: Додайте pageshow event listener для bfcache${NC}"
        echo "   window.addEventListener('pageshow', (event) => {"
        echo "     if (event.persisted) { /* restore state */ }"
        echo "   });"
    else
        echo -e "${GREEN}✅ pageshow event listener присутній${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Головний JS файл не знайдено: $MAIN_JS${NC}"
fi

# Перевірка 3: scrollend event
echo ""
echo "📜 Перевірка scrollend event..."
SCROLLEND=$(grep -r 'scrollend' "$JS_DIR" --include="*.js" 2>/dev/null || true)
if [ -z "$SCROLLEND" ]; then
    echo -e "${GREEN}ℹ️  scrollend event не використовується (це OK)${NC}"
fi

# Перевірка 4: IIFE або strict mode
echo ""
echo "🔒 Перевірка 'use strict' або IIFE..."
if [ -f "$MAIN_JS" ]; then
    STRICT_MODE=$(grep -r "'use strict'" "$MAIN_JS" 2>/dev/null || true)
    IIFE=$(grep -r '(function' "$MAIN_JS" 2>/dev/null || true)
    if [ -z "$STRICT_MODE" ] && [ -z "$IIFE" ]; then
        echo -e "${YELLOW}⚠️  УВАГА: Відсутній 'use strict' або IIFE${NC}"
    else
        echo -e "${GREEN}✅ 'use strict' або IIFE присутні${NC}"
    fi
fi

# Підсумок
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Всі JS перевірки пройдено успішно!${NC}"
    exit 0
else
    echo -e "${RED}❌ Знайдено $ERRORS помилок JS${NC}"
    exit 1
fi
```

**Адаптація:** Змініть шляхи та назви файлів під ваш проект.

### 4.5 scripts/check-all-rules.sh

Створіть файл `scripts/check-all-rules.sh`:

```bash
#!/bin/bash
# Головний скрипт перевірки ВСІХ правил

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

echo "🚀 Запуск повної перевірки (Ultimate Edition 2025)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. HTML перевірки
if [ -f "$REPO_ROOT/scripts/check-html-rules.sh" ]; then
    bash "$REPO_ROOT/scripts/check-html-rules.sh" || true
    HTML_EXIT=$?
else
    HTML_EXIT=0
fi

# 2. CSS перевірки
if [ -f "$REPO_ROOT/scripts/check-css-rules.sh" ]; then
    bash "$REPO_ROOT/scripts/check-css-rules.sh" || true
    CSS_EXIT=$?
else
    CSS_EXIT=0
fi

# 3. JS перевірки
if [ -f "$REPO_ROOT/scripts/check-js-rules.sh" ]; then
    bash "$REPO_ROOT/scripts/check-js-rules.sh" || true
    JS_EXIT=$?
else
    JS_EXIT=0
fi

# 4. Django template перевірки (якщо є)
if [ -f "$REPO_ROOT/scripts/check_template_tags.sh" ]; then
    bash "$REPO_ROOT/scripts/check_template_tags.sh" || true
    DJANGO_EXIT=$?
else
    DJANGO_EXIT=0
fi

# 5. Stylelint (якщо npm встановлено)
if command -v npm &> /dev/null && [ -f "$REPO_ROOT/package.json" ]; then
    echo ""
    echo "🎨 Запуск Stylelint..."
    cd "$REPO_ROOT"
    npm run lint:css || true
    STYLELINT_EXIT=$?
else
    echo ""
    echo "⚠️  Stylelint пропущено (npm не встановлено)"
    STYLELINT_EXIT=0
fi

# 6. ESLint (якщо npm встановлено)
if command -v npm &> /dev/null && [ -f "$REPO_ROOT/package.json" ]; then
    echo ""
    echo "📜 Запуск ESLint..."
    cd "$REPO_ROOT"
    npm run lint:js || true
    ESLINT_EXIT=$?
else
    echo ""
    echo "⚠️  ESLint пропущено (npm не встановлено)"
    ESLINT_EXIT=0
fi

# 7. HTMLHint (якщо npm встановлено)
if command -v npm &> /dev/null && [ -f "$REPO_ROOT/package.json" ]; then
    echo ""
    echo "📄 Запуск HTMLHint..."
    cd "$REPO_ROOT"
    npm run lint:html || true
    HTMLHINT_EXIT=$?
else
    echo ""
    echo "⚠️  HTMLHint пропущено (npm не встановлено)"
    HTMLHINT_EXIT=0
fi

# Підсумок
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 ПІДСУМОК ПЕРЕВІРОК:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TOTAL_ERRORS=$((HTML_EXIT + CSS_EXIT + JS_EXIT + DJANGO_EXIT + STYLELINT_EXIT + ESLINT_EXIT + HTMLHINT_EXIT))

[ $HTML_EXIT -eq 0 ] && echo "✅ HTML перевірки" || echo "❌ HTML перевірки"
[ $CSS_EXIT -eq 0 ] && echo "✅ CSS перевірки" || echo "❌ CSS перевірки"
[ $JS_EXIT -eq 0 ] && echo "✅ JS перевірки" || echo "❌ JS перевірки"
[ $DJANGO_EXIT -eq 0 ] && echo "✅ Django templates" || echo "❌ Django templates"
[ $STYLELINT_EXIT -eq 0 ] && echo "✅ Stylelint" || echo "❌ Stylelint"
[ $ESLINT_EXIT -eq 0 ] && echo "✅ ESLint" || echo "❌ ESLint"
[ $HTMLHINT_EXIT -eq 0 ] && echo "✅ HTMLHint" || echo "❌ HTMLHint"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $TOTAL_ERRORS -eq 0 ]; then
    echo "🎉 ВСІ ПЕРЕВІРКИ ПРОЙДЕНО УСПІШНО!"
    exit 0
else
    echo "❌ ПЕРЕВІРКИ НЕ ПРОЙДЕНО"
    echo "💡 Запустіть: npm run fix:rules для автоматичного виправлення"
    exit 1
fi
```

### 4.6 scripts/fix-rules.sh

Створіть файл `scripts/fix-rules.sh`:

```bash
#!/bin/bash
# Автоматичне виправлення деяких порушень

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

echo "🔧 Автоматичне виправлення порушень..."
echo ""

# АДАПТАЦІЯ: Змініть шляхи до ваших HTML файлів
HTML_DIRS=("$REPO_ROOT/templates" "$REPO_ROOT/src")
CSS_DIRS=("$REPO_ROOT/static/css" "$REPO_ROOT/src/css" "$REPO_ROOT/assets/css")

# 1. Видалення inline styles з HTML
echo "🎨 Видалення inline styles..."
for dir in "${HTML_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        find "$dir" -name "*.html" -type f -exec sed -i.bak 's/ style="[^"]*"//g' {} \; 2>/dev/null || true
        find "$dir" -name "*.bak" -delete 2>/dev/null || true
    fi
done
echo "✅ Inline styles видалено"

# 2. Додавання inputmode до tel полів
echo ""
echo "⌨️  Додавання inputmode='tel' до type='tel'..."
for dir in "${HTML_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        find "$dir" -name "*.html" -type f -exec sed -i.bak 's/type="tel"/type="tel" inputmode="tel"/g' {} \; 2>/dev/null || true
        find "$dir" -name "*.bak" -delete 2>/dev/null || true
    fi
done
echo "✅ inputmode додано"

# 3. Виправлення flex: 1
echo ""
echo "🔧 Виправлення flex: 1..."
for dir in "${CSS_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        find "$dir" -name "*.css" -type f -exec sed -i.bak 's/flex: 1;/flex: 1 0 0;/g' {} \; 2>/dev/null || true
        find "$dir" -name "*.bak" -delete 2>/dev/null || true
    fi
done
echo "✅ Flex properties виправлено"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Автоматичні виправлення завершено!"
echo "⚠️  ВАЖЛИВО: Перевірте зміни перед комітом!"
```

**Адаптація:** Змініть масиви `HTML_DIRS` та `CSS_DIRS` під структуру вашого проекту.

### 4.7 Надання прав на виконання

```bash
chmod +x scripts/check-html-rules.sh
chmod +x scripts/check-css-rules.sh
chmod +x scripts/check-js-rules.sh
chmod +x scripts/check-all-rules.sh
chmod +x scripts/fix-rules.sh
```

---

## Крок 5: Налаштування Git Hooks

### 5.1 Створення scripts/setup-git-hooks.sh

Створіть файл `scripts/setup-git-hooks.sh`:

```bash
#!/bin/bash
# Налаштування git hooks з повною перевіркою

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

if [ ! -d "$HOOKS_DIR" ]; then
    echo "❌ Помилка: .git/hooks директорія не знайдена"
    echo "💡 Переконайтеся, що ви знаходитесь в git репозиторії"
    exit 1
fi

echo "🔧 Налаштування git pre-commit hook (Ultimate Edition 2025)..."

cat > "$HOOKS_DIR/pre-commit" << 'HOOK_CONTENT'
#!/bin/bash
# Pre-commit hook з повною перевіркою всіх правил

REPO_ROOT="$(git rev-parse --show-toplevel)"

# Кольори
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 Pre-commit перевірка..."
echo ""

# Перевірка змінених файлів
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

# HTML файли
HTML_FILES=$(echo "$CHANGED_FILES" | grep '\.html$' || true)
if [ -n "$HTML_FILES" ]; then
    echo "📄 Перевірка HTML..."
    if [ -f "$REPO_ROOT/scripts/check-html-rules.sh" ]; then
        bash "$REPO_ROOT/scripts/check-html-rules.sh" || exit 1
    fi
fi

# CSS файли
CSS_FILES=$(echo "$CHANGED_FILES" | grep '\.css$' || true)
if [ -n "$CSS_FILES" ]; then
    echo "🎨 Перевірка CSS..."
    if [ -f "$REPO_ROOT/scripts/check-css-rules.sh" ]; then
        bash "$REPO_ROOT/scripts/check-css-rules.sh" || exit 1
    fi
    
    if command -v npm &> /dev/null && [ -f "$REPO_ROOT/package.json" ]; then
        echo "🔍 Stylelint..."
        cd "$REPO_ROOT"
        npm run lint:css || exit 1
    fi
fi

# JS файли
JS_FILES=$(echo "$CHANGED_FILES" | grep '\.js$' || true)
if [ -n "$JS_FILES" ]; then
    echo "📜 Перевірка JS..."
    if [ -f "$REPO_ROOT/scripts/check-js-rules.sh" ]; then
        bash "$REPO_ROOT/scripts/check-js-rules.sh" || exit 1
    fi
    
    if command -v npm &> /dev/null && [ -f "$REPO_ROOT/package.json" ]; then
        echo "🔍 ESLint..."
        cd "$REPO_ROOT"
        npm run lint:js || exit 1
    fi
fi

# Django templates (якщо є)
TEMPLATE_FILES=$(echo "$CHANGED_FILES" | grep 'templates/.*\.html$' || true)
if [ -n "$TEMPLATE_FILES" ]; then
    echo "🔧 Перевірка Django templates..."
    if [ -f "$REPO_ROOT/scripts/check_template_tags.sh" ]; then
        if [ -f "$REPO_ROOT/scripts/fix_template_tags.sh" ]; then
            cd "$REPO_ROOT"
            "$REPO_ROOT/scripts/fix_template_tags.sh" 2>/dev/null || true
            git add -u templates/ 2>/dev/null || true
        fi
        
        cd "$REPO_ROOT"
        if ! "$REPO_ROOT/scripts/check_template_tags.sh"; then
            echo ""
            echo -e "${RED}❌ Коміт заблоковано: знайдено розриви Django тегів!${NC}"
            echo "💡 Виправте розриви вручну або запустіть: ./scripts/fix_template_tags.sh"
            exit 1
        fi
    fi
fi

echo ""
echo -e "${GREEN}✅ Всі перевірки пройдено! Коміт дозволено.${NC}"
exit 0
HOOK_CONTENT

chmod +x "$HOOKS_DIR/pre-commit"

echo "✅ Git pre-commit hook налаштовано!"
echo ""
echo "Тепер при кожному коміті буде перевірятись:"
echo "  ✅ HTML правила (viewport, inputmode, inline styles)"
echo "  ✅ CSS правила (vh units, safe-area, rem, flexbox, hover)"
echo "  ✅ JS правила (var, bfcache, strict mode)"
echo "  ✅ Django templates (розриви тегів)"
echo "  ✅ Stylelint, ESLint, HTMLHint"
echo ""
echo "Для ручної перевірки: npm run check:rules"
echo "Для автовиправлення: npm run fix:rules"
```

### 5.2 Запуск налаштування

```bash
bash scripts/setup-git-hooks.sh
```

---

## Крок 6: Виправлення існуючих порушень

### 6.1 Перевірка поточних порушень

```bash
npm run check:rules
```

### 6.2 Автоматичне виправлення

```bash
npm run fix:rules
```

### 6.3 Ручне виправлення типових помилок

#### Viewport meta

**Знайдіть:** `<meta name="viewport" content="...">`

**Замініть на:**
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, interactive-widget=resizes-content">
```

#### 100vh → 100dvh

**Знайдіть:** `height: 100vh;` або `min-height: 100vh;`

**Замініть на:**
```css
.hero {
  height: 100vh; /* Fallback */
  height: 100dvh;
}
```

#### flex: 1 → flex: 1 0 0

**Знайдіть:** `flex: 1;`

**Замініть на:**
```css
.item {
  flex: 1 0 0; /* або flex: 1 0 auto */
}
```

#### inputmode для tel

**Знайдіть:** `<input type="tel"`

**Замініть на:**
```html
<input type="tel" inputmode="tel"
```

#### Inline styles

**Знайдіть:** `style="..."`

**Винесіть в CSS:**
```html
<!-- ❌ Погано -->
<div style="display: none;">...</div>

<!-- ✅ Добре -->
<div class="is-hidden">...</div>
```

```css
.is-hidden {
  display: none;
}
```

#### pageshow event

**Додайте в головний JS файл:**
```javascript
window.addEventListener('pageshow', function (event) {
    if (event.persisted) {
        // Сторінка відновлена з bfcache
        document.body.classList.remove('is-loading');
        // Перезапускаємо ініціалізацію компонентів
    }
});
```

---

## Крок 7: Тестування системи

### 7.1 Повна перевірка

```bash
npm run check:rules
```

Очікуваний результат:
```
✅ HTML перевірки
✅ CSS перевірки
✅ JS перевірки
✅ Stylelint
✅ ESLint
✅ HTMLHint
🎉 ВСІ ПЕРЕВІРКИ ПРОЙДЕНО УСПІШНО!
```

### 7.2 Тест блокування коміту

```bash
# Створити тестовий файл з порушенням
echo "body { color: red !important; }" > static/css/test.css

# Додати до staging
git add static/css/test.css

# Спробувати закомітити (має заблокуватись)
git commit -m "test violation"
# ❌ МАЄ ЗАБЛОКУВАТИСЬ

# Видалити тестовий файл
git reset HEAD static/css/test.css
rm static/css/test.css
```

### 7.3 Тест автоматичного виправлення

```bash
# Створити тестовий файл
echo '<input type="tel" name="phone">' > test.html

# Запустити автовиправлення
npm run fix:rules

# Перевірити результат
cat test.html
# Має бути: <input type="tel" name="phone" inputmode="tel">

# Видалити тестовий файл
rm test.html
```

---

## Повний список правил

### ❌ ЗАБОРОНЕНО (блокується комітом)

#### CSS:
1. `!important` (крім normalize.css override)
2. `100vh` без fallback на `100dvh`
3. `px` для `font-size` (тільки `rem`)
4. `flex: 1` без explicit `flex-basis`
5. `:hover` без `@media (hover: hover)`
6. Inline styles (`style=""`)

#### HTML:
7. Inline styles (`style=""`)
8. Inline scripts (`<script>` без `src`)
9. `<input type="tel">` без `inputmode="tel"`
10. `<input type="number">` без `inputmode="decimal"`
11. Viewport meta без `interactive-widget=resizes-content`
12. `<video autoplay>` без `muted` та `playsinline`

#### JavaScript:
13. `var` (тільки `const`/`let`)
14. Глобальні змінні
15. `eval()`
16. Inline handlers (`onclick=""`)

#### Django:
17. Розрив тегів `{{ }}` та `{% %}` на кілька рядків

### ✅ ОБОВ'ЯЗКОВО (перевіряється)

#### Viewport:
1. Viewport meta з `viewport-fit=cover` та `interactive-widget=resizes-content`
2. `env(safe-area-inset-*)` в body

#### CSS:
3. `rem` для розмірів шрифтів
4. `flex: 1 0 0` або `flex: 1 0 auto`
5. `overscroll-behavior: none` на body
6. `-webkit-backdrop-filter` разом з `backdrop-filter`

#### HTML:
7. `inputmode="tel"` для `type="tel"`
8. `inputmode="decimal"` для `type="number"`
9. `defer` на всіх `<script src="">`
10. `poster` для `<video>`

#### JavaScript:
11. `'use strict'` або IIFE
12. `pageshow` event listener для bfcache
13. `defer` атрибут для всіх скриптів

---

## Troubleshooting

### Проблема: Stylelint не знаходить конфігурацію

**Рішення:**
1. Перевірте, що `.stylelintrc.json` знаходиться в корені проекту
2. Перевірте синтаксис JSON: `cat .stylelintrc.json | python -m json.tool`
3. Перевірте шляхи в `package.json`: `"lint:css": "stylelint \"static/css/**/*.css\""`

### Проблема: ESLint не знаходить конфігурацію

**Рішення:**
1. Перевірте, що `.eslintrc.json` знаходиться в корені проекту
2. Або створіть `.eslintrc.js` замість `.json`:
```javascript
module.exports = {
  // ... конфігурація
};
```

### Проблема: Скрипти не виконуються

**Рішення:**
```bash
chmod +x scripts/*.sh
```

### Проблема: Pre-commit hook не спрацьовує

**Рішення:**
1. Перевірте права: `ls -la .git/hooks/pre-commit`
2. Перезапустіть налаштування: `bash scripts/setup-git-hooks.sh`
3. Перевірте вручну: `bash .git/hooks/pre-commit`

### Проблема: npm install не працює

**Рішення:**
1. Перевірте версію Node.js: `node --version` (потрібна >= 14)
2. Очистіть кеш: `npm cache clean --force`
3. Видаліть `node_modules` та `package-lock.json` і запустіть знову

### Проблема: Скрипти не знаходять файли

**Рішення:**
1. Адаптуйте шляхи в скриптах під структуру вашого проекту
2. Перевірте шляхи: `find . -name "*.css" -type f | head -5`
3. Оновіть змінні `CSS_DIR`, `HTML_DIRS`, `JS_DIR` в скриптах

---

## Адаптація для різних проектів

### React/Vue/Angular

**Зміни в package.json:**
```json
{
  "lint:css": "stylelint \"src/**/*.css\"",
  "lint:js": "eslint \"src/**/*.{js,jsx,ts,tsx}\"",
  "lint:html": "htmlhint \"public/**/*.html\""
}
```

**Зміни в скриптах:**
- `HTML_DIRS=("$REPO_ROOT/src" "$REPO_ROOT/public")`
- `CSS_DIRS=("$REPO_ROOT/src/css" "$REPO_ROOT/src/styles")`
- `JS_DIRS=("$REPO_ROOT/src")`

### Next.js

**Зміни в package.json:**
```json
{
  "lint:css": "stylelint \"**/*.css\"",
  "lint:js": "eslint \"**/*.{js,jsx,ts,tsx}\"",
  "lint:html": "htmlhint \"out/**/*.html\""
}
```

### WordPress

**Зміни в package.json:**
```json
{
  "lint:css": "stylelint \"wp-content/themes/**/*.css\"",
  "lint:js": "eslint \"wp-content/themes/**/*.js\"",
  "lint:html": "htmlhint \"wp-content/themes/**/*.php\""
}
```

**Примітка:** Для PHP файлів HTMLHint може не працювати, використовуйте тільки CSS/JS перевірки.

### Статичний сайт (Jekyll, Hugo, Eleventy)

**Зміни в package.json:**
```json
{
  "lint:css": "stylelint \"_site/**/*.css\"",
  "lint:js": "eslint \"src/**/*.js\"",
  "lint:html": "htmlhint \"_site/**/*.html\""
}
```

---

## Додаткові налаштування

### IDE Інтеграція

#### VS Code

Встановіть розширення:
- Stylelint
- ESLint
- HTMLHint

Додайте до `.vscode/settings.json`:
```json
{
  "editor.codeActionsOnSave": {
    "source.fixAll.stylelint": true,
    "source.fixAll.eslint": true
  },
  "stylelint.validate": ["css"],
  "eslint.validate": ["javascript"],
  "htmlhint.enable": true
}
```

#### WebStorm/PhpStorm

1. Settings → Languages & Frameworks → Style Sheets → Stylelint
2. Enable Stylelint
3. Settings → Languages & Frameworks → JavaScript → Code Quality Tools → ESLint
4. Enable ESLint

### CI/CD Інтеграція

#### GitHub Actions

Створіть `.github/workflows/lint.yml`:

```yaml
name: Lint and Check Rules

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm install
      
      - name: Run all checks
        run: npm run check:rules
```

#### GitLab CI

Додайте до `.gitlab-ci.yml`:

```yaml
lint:
  stage: test
  image: node:18
  before_script:
    - npm install
  script:
    - npm run check:rules
  only:
    - merge_requests
    - main
```

---

## Чек-лист налаштування

Виконайте всі кроки по порядку:

- [ ] Крок 1: Підготовка проекту
  - [ ] Оновлено `.gitignore`
  - [ ] Перевірено структуру проекту

- [ ] Крок 2: Встановлення залежностей
  - [ ] Створено `package.json`
  - [ ] Адаптовано шляхи під проект
  - [ ] Виконано `npm install`

- [ ] Крок 3: Створення конфігурацій
  - [ ] Створено `.stylelintrc.json`
  - [ ] Створено `.eslintrc.json`
  - [ ] Створено `.htmlhintrc`
  - [ ] Адаптовано під проект

- [ ] Крок 4: Створення скриптів
  - [ ] Створено `scripts/check-html-rules.sh`
  - [ ] Створено `scripts/check-css-rules.sh`
  - [ ] Створено `scripts/check-js-rules.sh`
  - [ ] Створено `scripts/check-all-rules.sh`
  - [ ] Створено `scripts/fix-rules.sh`
  - [ ] Надано права на виконання (`chmod +x`)
  - [ ] Адаптовано шляхи під проект

- [ ] Крок 5: Налаштування Git Hooks
  - [ ] Створено `scripts/setup-git-hooks.sh`
  - [ ] Виконано `bash scripts/setup-git-hooks.sh`

- [ ] Крок 6: Виправлення порушень
  - [ ] Запущено `npm run check:rules`
  - [ ] Виправлено всі помилки
  - [ ] Запущено `npm run fix:rules` (де можливо)

- [ ] Крок 7: Тестування
  - [ ] Всі перевірки проходять успішно
  - [ ] Pre-commit hook блокує порушення
  - [ ] Автовиправлення працює

---

## Швидкий старт (TL;DR)

```bash
# 1. Створіть package.json (скопіюйте з вище)
# 2. Встановіть залежності
npm install

# 3. Створіть конфігурації (.stylelintrc.json, .eslintrc.json, .htmlhintrc)
# 4. Створіть скрипти в scripts/ (скопіюйте з вище, адаптуйте шляхи)
chmod +x scripts/*.sh

# 5. Налаштуйте git hooks
bash scripts/setup-git-hooks.sh

# 6. Перевірте та виправте порушення
npm run check:rules
npm run fix:rules

# 7. Готово!
```

---

## Підтримка та оновлення

### Оновлення залежностей

```bash
npm update
```

### Додавання нових правил

1. Додайте правило до відповідного скрипта (`check-html-rules.sh`, `check-css-rules.sh`, `check-js-rules.sh`)
2. Додайте до конфігурації linter (якщо можливо)
3. Оновіть документацію

### Видалення правил

Якщо правило більше не актуальне:
1. Видаліть з скриптів перевірки
2. Видаліть з конфігурації linter
3. Оновіть документацію

---

## Додаткові ресурси

- [Кросплатформний посібник 2025](COMPREHENSIVE_RULES_GUIDE.md) - повний перелік правил
- [MDN Web Docs](https://developer.mozilla.org/) - документація веб-стандартів
- [Can I Use](https://caniuse.com/) - підтримка браузерами
- [Web Features Explorer](https://webfeatures.dev/) - статус Baseline

---

## Висновок

Після виконання всіх кроків ваша система буде:

✅ **Автоматично перевіряти** всі правила при коміті  
✅ **Блокувати коміти** з порушеннями  
✅ **Автоматично виправляти** прості помилки  
✅ **Забезпечувати якість** коду на всіх платформах  

**Порушити правила стає фізично неможливо!**

---

**Версія документа:** 1.0  
**Останнє оновлення:** Грудень 2025  
**Автор:** Ultimate Edition 2025 Setup Guide
