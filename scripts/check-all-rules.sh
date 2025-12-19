#!/bin/bash
# Головний скрипт перевірки ВСІХ правил

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

echo "🚀 Запуск повної перевірки (Ultimate Edition 2025)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. HTML перевірки
bash "$REPO_ROOT/scripts/check-html-rules.sh" || true
HTML_EXIT=$?

# 2. CSS перевірки
bash "$REPO_ROOT/scripts/check-css-rules.sh" || true
CSS_EXIT=$?

# 3. JS перевірки
bash "$REPO_ROOT/scripts/check-js-rules.sh" || true
JS_EXIT=$?

# 4. Django template перевірки
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
