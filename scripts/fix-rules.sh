#!/bin/bash
# Автоматичне виправлення деяких порушень

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

echo "🔧 Автоматичне виправлення порушень..."
echo ""

# 1. Видалення inline styles з HTML
echo "🎨 Видалення inline styles..."
find "$REPO_ROOT/templates" -name "*.html" -type f -exec sed -i.bak 's/ style="[^"]*"//g' {} \; 2>/dev/null || true
find "$REPO_ROOT/templates" -name "*.bak" -delete 2>/dev/null || true
echo "✅ Inline styles видалено"

# 2. Додавання inputmode до tel полів
echo ""
echo "⌨️  Додавання inputmode='tel' до type='tel'..."
find "$REPO_ROOT/templates" -name "*.html" -type f -exec sed -i.bak 's/type="tel"/type="tel" inputmode="tel"/g' {} \; 2>/dev/null || true
find "$REPO_ROOT/templates" -name "*.bak" -delete 2>/dev/null || true
echo "✅ inputmode додано"

# 3. Заміна 100vh на 100dvh з fallback (обережно - потребує ручної перевірки)
echo ""
echo "📐 Виправлення viewport units..."
echo "⚠️  УВАГА: Це потребує ручної перевірки!"
echo "   Перевірте файли після виконання"

# 4. Виправлення flex: 1
echo ""
echo "🔧 Виправлення flex: 1..."
find "$REPO_ROOT/static/css" -name "*.css" -type f -exec sed -i.bak 's/flex: 1;/flex: 1 0 0;/g' {} \; 2>/dev/null || true
find "$REPO_ROOT/static/css" -name "*.bak" -delete 2>/dev/null || true
echo "✅ Flex properties виправлено"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Автоматичні виправлення завершено!"
echo "⚠️  ВАЖЛИВО: Перевірте зміни перед комітом!"



