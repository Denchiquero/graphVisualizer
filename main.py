import argparse
import sys
import os
from urllib.parse import urlparse
from typing import Dict, Any

from NPMDependencyFetcher import NPMDependencyFetcher


class DependencyGraphConfig:

    def __init__(self):
        self.package_name = None
        self.repository_url = None
        self.repository_path = None
        self.test_mode = False
        self.package_version = None
        self.filter_substring = None
        self.errors = []

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
            'filter_substring': self.filter_substring
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

    return parser.parse_args()


def setup_config(args) -> DependencyGraphConfig:

    config = DependencyGraphConfig()

    config.package_name = args.package
    config.repository_url = args.url
    config.repository_path = args.path
    config.test_mode = args.test_mode
    config.package_version = args.version
    config.filter_substring = args.filter_substring

    return config


def fetch_and_display_dependencies(config: DependencyGraphConfig):

    fetcher = NPMDependencyFetcher()

    dependencies = fetcher.get_dependencies(config.package_name, config.package_version)


    if config.filter_substring:
        filtered_deps = {
            name: version for name, version in dependencies.items()
            if config.filter_substring.lower() in name.lower()
        }
        dependencies = filtered_deps

    if dependencies:
        print(f"\nStraight dependencies {config.package_name}:")
        print("-" * 50)
        for dep_name, dep_version in dependencies.items():
            print(f"  {dep_name}: {dep_version}")
        print(f"\nTotal dependencies: {len(dependencies)}")
    else:
        print(f"\nPAckage {config.package_name} not have dependencies or not found")

    return dependencies


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