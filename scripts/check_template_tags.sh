#!/bin/bash
# Скрипт для перевірки розривів Django тегів у шаблонах

set -e

TEMPLATES_DIR="templates"
ERRORS=0

echo "🔍 Перевірка розривів Django тегів у шаблонах..."

# Перевірка розривів {{ }} тегів
while IFS= read -r file; do
    if grep -n '{{[^}]*$' "$file" > /dev/null 2>&1; then
        echo "❌ Знайдено розрив {{ }} тега у файлі: $file"
        grep -n '{{[^}]*$' "$file" | while IFS=: read -r line_num line; do
            echo "   Рядок $line_num: $line"
        done
        ERRORS=$((ERRORS + 1))
    fi
done < <(find "$TEMPLATES_DIR" -type f -name "*.html" 2>/dev/null || true)

# Перевірка розривів {% %} тегів (складніше, бо можуть бути багаторядкові блоки)
# Перевіряємо тільки простий випадок - тег що починається і не закривається на тому ж рядку
while IFS= read -r file; do
    if grep -nP '{%\s+(if|for|with|block|extends|include|url|load)\s+[^%]*$' "$file" > /dev/null 2>&1; then
        echo "⚠️  Можливий розрив {% %} тега у файлі: $file"
        grep -nP '{%\s+(if|for|with|block|extends|include|url|load)\s+[^%]*$' "$file" | while IFS=: read -r line_num line; do
            echo "   Рядок $line_num: $line"
        done
        # Не рахуємо це як помилку, бо може бути валідний багаторядковий блок
    fi
done < <(find "$TEMPLATES_DIR" -type f -name "*.html" 2>/dev/null || true)

if [ $ERRORS -eq 0 ]; then
    echo "✅ Розривів {{ }} тегів не знайдено!"
    exit 0
else
    echo ""
    echo "❌ Знайдено $ERRORS файл(ів) з розривами тегів!"
    echo "💡 Виправте розриви: Django теги {{ }} та {% %} мають бути в одному рядку"
    exit 1
fi
