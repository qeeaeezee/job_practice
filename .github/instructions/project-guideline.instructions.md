---
applyTo: '**'
---
Coding standards, domain knowledge, and preferences that AI should follow.

# Project Guideline

## 1. 回答使用的語系
- 回答我的敘述總是繁體中文

## 2. 代碼風格
- 使用空格而不是 tab 縮排
- 使用 2 個空格作為縮排
- 總是使用 python3 而不是 python

## 3. 程式運行方式
- 總是使用 source venv/bin/activate && python3 -m pytest jobs/tests.py -v 這樣的形式來運行，一定要 source 並且用 python3