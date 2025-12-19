#!/bin/bash
# Скрипт для налаштування git hooks

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

if [ ! -d "$HOOKS_DIR" ]; then
    echo "❌ Помилка: .git/hooks директорія не знайдена"
    echo "💡 Переконайтеся, що ви знаходитесь в git репозиторії"
    exit 1
fi

echo "🔧 Налаштування git pre-commit hook..."

# Створюємо pre-commit hook
cat > "$HOOKS_DIR/pre-commit" << 'HOOK_CONTENT'
#!/bin/bash
# Pre-commit hook для перевірки розривів Django тегів

REPO_ROOT="$(git rev-parse --show-toplevel)"
CHECK_SCRIPT="$REPO_ROOT/scripts/check_template_tags.sh"
FIX_SCRIPT="$REPO_ROOT/scripts/fix_template_tags.sh"

# Перевіряємо, чи є змінені HTML файли
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.html$' || true)

if [ -z "$CHANGED_FILES" ]; then
    exit 0
fi

echo "🔍 Перевірка Django тегів у змінених шаблонах..."

# Спочатку намагаємося автоматично виправити
if [ -f "$FIX_SCRIPT" ]; then
    cd "$REPO_ROOT"
    "$FIX_SCRIPT" 2>/dev/null || true
    # Додаємо виправлені файли до staging
    git add -u templates/ 2>/dev/null || true
fi

# Перевіряємо наявність розривів
if [ -f "$CHECK_SCRIPT" ]; then
    cd "$REPO_ROOT"
    if ! "$CHECK_SCRIPT"; then
        echo ""
        echo "❌ Коміт заблоковано: знайдено розриви Django тегів!"
        echo "💡 Виправте розриви вручну або запустіть: ./scripts/fix_template_tags.sh"
        exit 1
    fi
fi

exit 0
HOOK_CONTENT

chmod +x "$HOOKS_DIR/pre-commit"

echo "✅ Git pre-commit hook налаштовано!"
echo ""
echo "Тепер при кожному коміті буде:"
echo "  1. Автоматично виправляти розриви тегів (якщо можливо)"
echo "  2. Блокувати коміт, якщо знайдено розриви, які не можна виправити автоматично"
echo ""
echo "Для ручної перевірки: ./scripts/check_template_tags.sh"
echo "Для ручного виправлення: ./scripts/fix_template_tags.sh"
