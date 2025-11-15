# Описание проекта

Инструмент для анализа и визуализации графов зависимостей пакетов. Поддерживает работу с NPM реестром и локальными тестовыми файлами.
Архитектура
Основные классы
### 1. DependencyGraphConfig

Назначение: Конфигурация параметров запуска
Методы:
    validate() - валидация параметров конфигурации
    to_dict() - сериализация в словарь
    display() - отображение параметров
Параметры:
    package_name - имя анализируемого пакета
    repository_url - URL репозитория
    repository_path - путь к тестовому файлу
    test_mode - режим тестирования
    package_version - версия пакета
    filter_substring - фильтр пакетов
    max_depth - максимальная глубина анализа

### 2. NPMDependencyFetcher

Назначение: Получение информации о пакетах из NPM реестра
Методы:
    get_package_info() - получение информации о пакете
    extract_dependencies() - извлечение зависимостей
    get_dependencies() - основной метод получения зависимостей

### 3. DependencyGraph

Назначение: Представление и анализ графа зависимостей
Методы:
    add_dependency() - добавление зависимости
    bfs_traversal() - обход графа в ширину
    get_transitive_dependencies() - получение транзитивных зависимостей

#### Основные функции
- Обработка аргументов командной строки
parse_arguments() - парсинг аргументов CLI
setup_config() - настройка конфигурации

- Построение графа зависимостей
build_dependency_graph() - построение графа BFS с ограничением глубины
fetch_and_display_dependencies() - основной поток получения и отображения

- Визуализация
build_tree_structure() - построение структуры дерева
print_tree() - отображение дерева зависимостей
display_dependency_results() - вывод результатов

#### Тестирование

    demo.py - демонстрация различных сценариев
    Тестовые файлы с циклическими зависимостями

#### Использование

#### Анализ NPM пакета
`python main.py --package express --url https://registry.npmjs.org`

#### Тестовый режим с файлом
`python main.py --package A --path deps.json --test-mode`

#### С ограничением глубины и фильтром
`python main.py --package react --url https://registry.npmjs.org --max-depth 3 --filter "dev"`

#### Пример

```
C:\Users\denis\OneDrive\Документы\Packages\.venv\Scripts\python.exe main.py --package A --path "C:\Users\denis\AppData\Local\Temp\tmpp8uhp062.json" --test-mode
STDOUT:
PARAMS KONFIGURATION
package_name: A
repository_url: None
repository_path: C:\Users\denis\AppData\Local\Temp\tmpp8uhp062.json
test_mode: True
package_version: None
filter_substring: None
max_depth: 2

Dependencies graph A (max depth: 2):

A
├── B
│   └── E
└── C
    ├── D
    └── F

Executed sucessfuly

Exit code: 0
```

Проект демонстрирует практики работы с графами, API вызовами и визуализацией древовидных структур в консоли