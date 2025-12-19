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

# Django templates
TEMPLATE_FILES=$(echo "$CHANGED_FILES" | grep 'templates/.*\.html$' || true)
if [ -n "$TEMPLATE_FILES" ]; then
    echo "🔧 Перевірка Django templates..."
    if [ -f "$REPO_ROOT/scripts/check_template_tags.sh" ]; then
        # Спочатку намагаємося автоматично виправити
        if [ -f "$REPO_ROOT/scripts/fix_template_tags.sh" ]; then
            cd "$REPO_ROOT"
            "$REPO_ROOT/scripts/fix_template_tags.sh" 2>/dev/null || true
            git add -u templates/ 2>/dev/null || true
        fi
        
        # Перевіряємо наявність розривів
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
