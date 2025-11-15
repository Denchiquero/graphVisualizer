import argparse
import json
import sys
import os
from collections import deque
from urllib.parse import urlparse
from typing import Dict, Any, List

from NPMDependencyFetcher import NPMDependencyFetcher
from DependencyGrapf import DependencyGraph


class DependencyGraphConfig:

    def __init__(self):
        self.package_name = None
        self.repository_url = None
        self.repository_path = None
        self.test_mode = False
        self.package_version = None
        self.filter_substring = None
        self.errors = []
        self.max_depth = 2

    def validate(self) -> bool:

        self.errors = []

        # Проверка имени пакета
        if not self.package_name:
            self.errors.append("package name is required")
        elif not isinstance(self.package_name, str) or len(self.package_name.strip()) == 0:
            self.errors.append("package name must be not empty")

        # Проверка репозитория
        if self.repository_url and self.repository_path:
            self.errors.append("you can input either package name or repository url not both")

        if not self.repository_url and not self.repository_path:
            self.errors.append("you must input either package name or repository url")

        # Валидация URL
        if self.repository_url:
            try:
                result = urlparse(self.repository_url)
                if not all([result.scheme, result.netloc]):
                    self.errors.append(f"Invalid URL: {self.repository_url}")
            except Exception as e:
                self.errors.append(f"URL parse error : {str(e)}")

        # Валидация пути к файлу
        if self.repository_path and self.test_mode:
            if not os.path.exists(self.repository_path):
                self.errors.append(f"File not exists: {self.repository_path}")
            elif not os.path.isfile(self.repository_path):
                self.errors.append(f"Path is not a file: {self.repository_path}")

        # Валидация версии пакета
        if self.package_version and not self._validate_version(self.package_version):
            self.errors.append(f"Version format invalid: {self.package_version}")

        return len(self.errors) == 0

    def _validate_version(self, version: str) -> bool:

        if not version or not isinstance(version, str):
            return False

        return len(version.strip()) > 0

    def to_dict(self) -> Dict[str, Any]:

        return {
            'package_name': self.package_name,
            'repository_url': self.repository_url,
            'repository_path': self.repository_path,
            'test_mode': self.test_mode,
            'package_version': self.package_version,
            'filter_substring': self.filter_substring,
            'max_depth': self.max_depth
        }

    def display(self):

        config_dict = self.to_dict()
        print("PARAMS KONFIGURATION")
        for key, value in config_dict.items():
            print(f"{key}: {value}")


def parse_arguments():

    parser = argparse.ArgumentParser(
        description='package dependencies graph visualizer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples of using:
  python main.py --package requests --url https://pypi.org/simple/
  python main.py --package numpy --path deps.json --test-mode --version 1.21.0
  python main.py --package django --url https://pypi.org/simple/ --filter "security"
        '''
    )

    # Обязательные параметры
    parser.add_argument(
        '--package',
        required=True,
        help='PAckage name'
    )

    # Взаимоисключающие параметры для репозитория
    repo_group = parser.add_mutually_exclusive_group(required=True)
    repo_group.add_argument(
        '--url',
        help='URL of package repository',
    )
    repo_group.add_argument(
        '--path',
        help='path to test package repository',
    )

    # Опциональные параметры
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='test repository mode'
    )
    parser.add_argument(
        '--version',
        help='package version'
    )
    parser.add_argument(
        '--filter',
        dest='filter_substring',
        help='substring for package filter'
    )

    parser.add_argument(
        '--max-depth',
        type=int,
        default=2,
        help='maximum depth for dependency traversal (default: 2)'
    )

    return parser.parse_args()


def setup_config(args) -> DependencyGraphConfig:

    config = DependencyGraphConfig()

    config.package_name = args.package
    config.repository_url = args.url
    config.repository_path = args.path
    config.test_mode = args.test_mode
    config.package_version = args.version
    config.filter_substring = args.filter_substring
    config.max_depth = args.max_depth

    return config


def fetch_and_display_dependencies(config: DependencyGraphConfig):

    # Режим тестирования с файлом
    if config.test_mode and config.repository_path:
        dependencies_data = load_test_dependencies(config.repository_path)
        if not dependencies_data:
            print(f"Unable to load dependencies {config.repository_path}")
            return {}
    else:
        # Режим работы с NPM реестром
        fetcher = NPMDependencyFetcher()
        dependencies_data = build_dependency_graph(fetcher, config.package_name, config.package_version,
                                                   max_depth=config.max_depth)

    if not dependencies_data:
        print(f"Package {config.package_name} not have dependencies or not found")
        return {}

    # Строим граф и получаем транзитивные зависимости
    graph = DependencyGraph()
    for package, deps in dependencies_data.items():
        graph.add_dependency(package, deps)

    result = graph.get_transitive_dependencies(config.package_name, config.filter_substring)

    # Отображаем результаты в виде дерева с ограничением глубины
    display_dependency_results(config.package_name, result, config.filter_substring, config.max_depth)

    return result


def build_dependency_graph(fetcher: NPMDependencyFetcher, start_package: str, version: str = None,
                           max_depth: int = 3) -> Dict[str, Dict[str, str]]:
    graph = {}
    visited = set()
    queue = deque([(start_package, version, 0)])  # (package, version, depth)

    while queue:
        current_package, current_version, depth = queue.popleft()

        if current_package in visited:
            continue

        visited.add(current_package)

        # Ограничение глубины для больших графов
        if depth >= max_depth:
            graph[current_package] = {}
            continue

        # Получаем информацию о пакете
        package_info = fetcher.get_package_info(current_package, current_version)
        if not package_info:
            graph[current_package] = {}
            continue

        # Извлекаем зависимости
        dependencies = fetcher.extract_dependencies(package_info)
        graph[current_package] = dependencies

        # Добавляем зависимости в очередь для обработки
        for dep_name, dep_version in dependencies.items():
            if dep_name not in visited and dep_name not in [p[0] for p in queue]:
                queue.append((dep_name, dep_version, depth + 1))

    return graph


def load_test_dependencies(file_path: str) -> Dict[str, Dict[str, str]]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading test dependencies: {e}")
        return {}


def display_dependency_results(package_name: str, result: Dict[str, Any], filter_substring: str = None, max_depth: int = 10):

    dependencies = result['dependencies']
    cycles = result['cycles']

    if not dependencies or len(dependencies) <= 1:
        print(f"\nPackage {package_name} not have dependencies")
        return

    print(f"\nDependencies graph {package_name} (max depth: {max_depth}):")
    print("=" * 50)

    # Строим структуру дерева из графа с ограничением глубины
    tree_structure = build_tree_structure(package_name, result, filter_substring, max_depth)

    # Выводим дерево с ограничением глубины
    print_tree(package_name, tree_structure, cycles, filter_substring, max_depth)

    if filter_substring:
        print(f"\nFilter: '{filter_substring}'")

    if cycles:
        print(f"\nCycles:")
        for i, cycle in enumerate(cycles, 1):
            print(f"  Cycle {i}: {' → '.join(cycle)}")


def build_tree_structure(root: str, result: Dict[str, Any], filter_substring: str = None, max_level: int = 10) -> Dict[
    str, List[str]]:

    graph = result.get('graph', {})
    tree = {}
    visited_levels = {}

    stack = [(root, 0)]

    while stack:
        current, level = stack.pop()

        # Строгое ограничение глубины
        if level >= max_level:
            continue

        if current not in tree:
            tree[current] = []

        if current in graph:
            for child in graph[current]:
                # Пропускаем отфильтрованные пакеты
                if filter_substring and filter_substring.lower() in child.lower():
                    continue

                # Проверяем, не превышает ли добавление этого ребенка максимальный уровень
                if child not in visited_levels or visited_levels[child] > level + 1:
                    if child not in tree[current]:
                        tree[current].append(child)
                    visited_levels[child] = level + 1
                    if level + 1 < max_level:  # строго меньше
                        stack.append((child, level + 1))

    return tree


def print_tree(root: str, tree: Dict[str, List[str]], cycles: List[List[str]], filter_substring: str = None,
               max_depth: int = 10):

    def is_in_cycle(node, path):

        for cycle in cycles:
            if node in cycle and any(n in path for n in cycle):
                return True
        return False

    stack = [(root, 0, [], [])]  # (node, depth, prefix_parts, path)

    while stack:
        current_node, depth, prefix_parts, path = stack.pop()

        if filter_substring and filter_substring.lower() in current_node.lower():
            continue

        # Проверяем цикл
        is_cycle_node = is_in_cycle(current_node, path)

        # Строим префикс
        if depth == 0:
            print(current_node + (" CYCLE" if is_cycle_node else ""))
        else:
            prefix = ""
            for i, part in enumerate(prefix_parts):
                if i == len(prefix_parts) - 1:
                    prefix += "└── " if part else "├── "
                else:
                    prefix += "    " if part else "│   "
            print(f"{prefix}{current_node}" + (" CYCLE" if is_cycle_node else ""))

        # Если достигли максимальной глубины или узел в цикле, не идем глубже
        if depth >= max_depth or is_cycle_node:
            continue

        # Добавляем детей
        if current_node in tree:
            children = tree[current_node]
            new_path = path + [current_node]

            for i, child in enumerate(reversed(children)):
                is_last = (i == 0)  # Поскольку переворачиваем
                stack.append((child, depth + 1, prefix_parts + [is_last], new_path))

def main():

    try:

        if sys.platform == "win32":
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

        args = parse_arguments()

        config = setup_config(args)

        # Валидация параметров
        if not config.validate():
            print("Konfig error:", file=sys.stderr)
            for error in config.errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)

        config.display()

        dependencies = fetch_and_display_dependencies(config)

        print("\nExecuted sucessfuly")

    except argparse.ArgumentError as e:
        print(f"Error in cli arguments: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\ninterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()