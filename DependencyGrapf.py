from collections import deque
from typing import Dict, Any, Set, List


class DependencyGraph:

    def __init__(self):
        self.graph = {}  # {package: {dependencies}}
        self.visited = set()

    def add_dependency(self, package: str, dependencies: Dict[str, str]):

        self.graph[package] = dependencies

    def bfs_traversal(self, start_package: str, filter_substring: str = None) -> Dict[str, Any]:

        if start_package not in self.graph:
            return {'dependencies': {}, 'cycles': []}

        visited = set()
        queue = deque([(start_package, 0, [start_package])])  # (package, level, path)
        dependencies = {}
        cycles = []
        visited_paths = set()

        while queue:
            current_package, level, path = queue.popleft()

            # Пропускаем пакеты, содержащие фильтрующую подстроку
            if filter_substring and filter_substring.lower() in current_package.lower():
                continue

            if current_package not in visited:
                visited.add(current_package)
                dependencies[current_package] = level

                # Добавляем зависимости текущего пакета в очередь
                if current_package in self.graph:
                    for dep in self.graph[current_package]:
                        # Проверяем цикличность
                        if dep in path:
                            # Найден цикл
                            cycle_start = path.index(dep)
                            cycle = path[cycle_start:] + [dep]
                            if cycle not in cycles:
                                cycles.append(cycle)
                            continue

                        # Проверяем, не посещали ли мы уже этот путь
                        new_path = path + [dep]
                        path_key = tuple(new_path)
                        if path_key not in visited_paths:
                            visited_paths.add(path_key)
                            queue.append((dep, level + 1, new_path))

        return {'dependencies': dependencies, 'cycles': cycles}

    def get_transitive_dependencies(self, start_package: str, filter_substring: str = None) -> Dict[str, Any]:
        bfs_result = self.bfs_traversal(start_package, filter_substring)

        # Добавляем граф в результат для построения дерева
        bfs_result['graph'] = self.graph

        return bfs_result