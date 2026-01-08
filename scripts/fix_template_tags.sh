#!/bin/bash
# Скрипт для автоматичного виправлення розривів Django тегів у шаблонах

set -e

TEMPLATES_DIR="templates"
FIXED=0

echo "🔧 Виправлення розривів Django тегів у шаблонах..."

# Знаходимо всі файли з розривами {{ }} тегів
while IFS= read -r file; do
    # Перевіряємо, чи є розриви
    if grep -q '{{[^}]*$' "$file" 2>/dev/null; then
        echo "📝 Виправляю: $file"
        
        # Виправляємо розриви {{ }} тегів
        # Знаходимо рядки з розривами та об'єднуємо їх
        python3 << 'PYTHON_SCRIPT'
import re
import sys

file_path = sys.argv[1]

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Знаходимо всі розриви {{ }} тегів
# Патерн: {{ щось на рядку без }}
pattern = r'(\{\{[^}]*)\n\s*(\}\})'

def fix_break(match):
    open_tag = match.group(1).rstrip()
    close_tag = match.group(2)
    # Об'єднуємо тег в один рядок
    return f"{open_tag}{close_tag}"

# Виправляємо розриви
new_content = re.sub(pattern, fix_break, content)

# Також виправляємо випадки, коли тег розривається на кілька рядків
# {{ variable
#     }}
pattern2 = r'(\{\{[^}]*?)\n\s+(\}\})'
new_content = re.sub(pattern2, r'\1\2', new_content)

if new_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ Виправлено: {file_path}")
    sys.exit(0)
else:
    sys.exit(1)

PYTHON_SCRIPT
        "$file"
        
        if [ $? -eq 0 ]; then
            FIXED=$((FIXED + 1))
        fi
    fi
done < <(find "$TEMPLATES_DIR" -type f -name "*.html" 2>/dev/null || true)

if [ $FIXED -gt 0 ]; then
    echo ""
    echo "✅ Виправлено $FIXED файл(ів)!"
    exit 0
else
    echo "✅ Розривів не знайдено - все добре!"
    exit 0
fi



