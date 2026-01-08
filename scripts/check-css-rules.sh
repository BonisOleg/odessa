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

# Перевірка 1: 100vh має мати fallback на 100dvh
echo "📐 Перевірка viewport units..."
# Перевіряємо файли з 100vh
VH_FILES=$(grep -r '100vh' "$REPO_ROOT/static/css" --include="*.css" 2>/dev/null | cut -d: -f1 | sort -u || true)
VH_WITHOUT_DVH=""

if [ -n "$VH_FILES" ]; then
    for file in $VH_FILES; do
        # Перевіряємо чи є 100dvh в тому ж файлі (може бути на наступному рядку)
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
SAFE_AREA=$(grep -r 'env(safe-area-inset' "$REPO_ROOT/static/css/base.css" 2>/dev/null || true)
if [ -z "$SAFE_AREA" ]; then
    echo -e "${RED}❌ ПОМИЛКА: Відсутні env(safe-area-inset-*) в base.css${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ Safe area insets присутні${NC}"
fi

# Перевірка 3: rem для font-size
echo ""
echo "🔤 Перевірка rem для font-size..."
PX_FONT_SIZE=$(grep -r 'font-size.*px' "$REPO_ROOT/static/css" --include="*.css" --exclude="normalize.css" 2>/dev/null | grep -v '/\*' | grep -v '16px' || true)
if [ -n "$PX_FONT_SIZE" ]; then
    echo -e "${YELLOW}⚠️  УВАГА: font-size в px (рекомендовано rem):${NC}"
    echo "$PX_FONT_SIZE"
fi

# Перевірка 4: flex без flex-basis
echo ""
echo "🔧 Перевірка flex-basis..."
FLEX_WITHOUT_BASIS=$(grep -r 'flex:\s*1\s*;' "$REPO_ROOT/static/css" --include="*.css" 2>/dev/null || true)
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
HOVER_WITHOUT_MEDIA=$(grep -r ':hover' "$REPO_ROOT/static/css" --include="*.css" -A 2 -B 2 2>/dev/null | grep -v '@media.*hover' || true)
if [ -n "$HOVER_WITHOUT_MEDIA" ]; then
    echo -e "${YELLOW}⚠️  УВАГА: :hover без @media (hover: hover):${NC}"
    echo "   Може призвести до \"липкого\" hover на touchscreen"
fi

# Перевірка 6: overscroll-behavior
echo ""
echo "📜 Перевірка overscroll-behavior..."
OVERSCROLL=$(grep -r 'overscroll-behavior' "$REPO_ROOT/static/css/base.css" 2>/dev/null || true)
if [ -z "$OVERSCROLL" ]; then
    echo -e "${YELLOW}⚠️  УВАГА: Відсутній overscroll-behavior в base.css${NC}"
fi

# Перевірка 7: !important
echo ""
echo "❗ Перевірка !important..."
IMPORTANT=$(grep -r '!important' "$REPO_ROOT/static/css" --include="*.css" --exclude="normalize.css" 2>/dev/null || true)
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
BACKDROP_FILTER=$(grep -r 'backdrop-filter' "$REPO_ROOT/static/css" --include="*.css" 2>/dev/null || true)
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



