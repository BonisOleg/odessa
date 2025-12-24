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

# Перевірка 1: var заборонено
echo "🔤 Перевірка var (має бути const/let)..."
VAR_USAGE=$(grep -r '\bvar\b' "$REPO_ROOT/static/js" --include="*.js" 2>/dev/null || true)
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
PAGESHOW=$(grep -r 'pageshow' "$REPO_ROOT/static/js/main.js" 2>/dev/null || true)
if [ -z "$PAGESHOW" ]; then
    echo -e "${YELLOW}⚠️  РЕКОМЕНДАЦІЯ: Додайте pageshow event listener для bfcache${NC}"
    echo "   window.addEventListener('pageshow', (event) => {"
    echo "     if (event.persisted) { /* restore state */ }"
    echo "   });"
fi

# Перевірка 3: scrollend event
echo ""
echo "📜 Перевірка scrollend event..."
SCROLLEND=$(grep -r 'scrollend' "$REPO_ROOT/static/js" --include="*.js" 2>/dev/null || true)
if [ -z "$SCROLLEND" ]; then
    echo -e "${GREEN}ℹ️  scrollend event не використовується (це OK)${NC}"
fi

# Перевірка 4: IIFE або strict mode
echo ""
echo "🔒 Перевірка 'use strict' або IIFE..."
STRICT_MODE=$(grep -r "'use strict'" "$REPO_ROOT/static/js/main.js" 2>/dev/null || true)
IIFE=$(grep -r '(function' "$REPO_ROOT/static/js/main.js" 2>/dev/null || true)
if [ -z "$STRICT_MODE" ] && [ -z "$IIFE" ]; then
    echo -e "${YELLOW}⚠️  УВАГА: Відсутній 'use strict' або IIFE${NC}"
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

