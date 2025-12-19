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

# Перевірка 1: Viewport meta має містити необхідні атрибути
echo "📱 Перевірка viewport meta..."
if grep -r "viewport" "$REPO_ROOT/templates/base.html" | grep -q "interactive-widget=resizes-content"; then
    echo -e "${GREEN}✅ Viewport meta містить interactive-widget=resizes-content${NC}"
else
    echo -e "${RED}❌ ПОМИЛКА: Viewport meta не містить interactive-widget=resizes-content${NC}"
    echo "   Додайте: interactive-widget=resizes-content"
    ERRORS=$((ERRORS + 1))
fi

if grep -r "viewport" "$REPO_ROOT/templates/base.html" | grep -q "viewport-fit=cover"; then
    echo -e "${GREEN}✅ Viewport meta містить viewport-fit=cover${NC}"
else
    echo -e "${RED}❌ ПОМИЛКА: Viewport meta не містить viewport-fit=cover${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Перевірка 2: Inline styles заборонені
echo ""
echo "🎨 Перевірка inline styles..."
INLINE_STYLES=$(grep -r 'style=' "$REPO_ROOT/templates" --include="*.html" --exclude-dir=".git" 2>/dev/null || true)
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
if [ -n "$VIDEO_WITHOUT_POSTER" ]; then
    echo -e "${YELLOW}⚠️  УВАГА: <video> без poster атрибуту:${NC}"
    echo "$VIDEO_WITHOUT_POSTER"
fi

VIDEO_WITHOUT_PLAYSINLINE=$(grep -r '<video' "$REPO_ROOT/templates" --include="*.html" 2>/dev/null | grep -v 'playsinline' || true)
if [ -n "$VIDEO_WITHOUT_PLAYSINLINE" ]; then
    echo -e "${RED}❌ ПОМИЛКА: <video> без playsinline (ЗАБОРОНЕНО для iOS):${NC}"
    echo "$VIDEO_WITHOUT_PLAYSINLINE"
    ERRORS=$((ERRORS + 1))
fi

# Перевірка 7: Scripts мають defer
echo ""
echo "⏱️  Перевірка defer для scripts..."
SCRIPTS_WITHOUT_DEFER=$(grep -r '<script src=' "$REPO_ROOT/templates" --include="*.html" 2>/dev/null | grep -v 'defer' | grep -v 'async' || true)
if [ -n "$SCRIPTS_WITHOUT_DEFER" ]; then
    echo -e "${RED}❌ ПОМИЛКА: <script> без defer/async:${NC}"
    echo "$SCRIPTS_WITHOUT_DEFER"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✅ Всі scripts мають defer${NC}"
fi

# Перевірка 8: Мінімальний розмір полів форм
echo ""
echo "📏 Перевірка мінімальних розмірів полів (CSS)..."
MIN_FONT_SIZE=$(grep -r 'font-size.*16px' "$REPO_ROOT/static/css/components/form.css" 2>/dev/null || true)
if [ -z "$MIN_FONT_SIZE" ]; then
    echo -e "${YELLOW}⚠️  УВАГА: Перевірте що form controls мають font-size: 16px для iOS${NC}"
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
