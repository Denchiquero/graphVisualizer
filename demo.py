import subprocess
import sys
import tempfile
import os


def run_command(command):
    #Запуск команды и вывод результата
    print(f"\n>>> Run: {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        print("STDOUT:")
        print(result.stdout if result.stdout else "(empty)")

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print(f"Exit code: {result.returncode}")

        return result.returncode

    except Exception as e:
        print(f"error: {e}")

        return 1


def create_test_file():
    #Создание временного тестового файла
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        f.write('{"dependencies": []}')
        return f.name


def main():

    print("Demo")

    # Сценарий 1: Успешный запуск с URL
    print("\n1.1. Run with url:")
    run_command(
        f'{sys.executable} main.py --package requests --url https://pypi.org/simple/ --version 2.28.0 --filter "http"')

    # Сценарий 2: Успешный запуск с файлом (тестовый режим)
    temp_file = None
    try:
        temp_file = create_test_file()
        print("\n1.2. Run with file in test mode:")
        run_command(f'{sys.executable} main.py --package numpy --path "{temp_file}" --test-mode --version 1.21.0')
    finally:
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)

    # Сценарий 3: Ошибка - отсутствует имя пакета
    print("\n1.3. No --package:")
    run_command(f'{sys.executable} main.py --url https://pypi.org/simple/')

    # Сценарий 4: Ошибка - указаны и URL и путь
    print("\n1.4. url and path both:")
    run_command(f'{sys.executable} main.py --package test --url https://pypi.org/simple/ --path file.json')

    # Сценарий 5: Ошибка - некорректный URL
    print("\n1.5. invalid url")
    run_command(f'{sys.executable} main.py --package test --url invalid-url')

    # Сценарий 6: Помощь по использованию
    print("\n1.6. help")
    run_command(f'{sys.executable} main.py --help')

    # Сценарий 7: Минимальная успешная конфигурация
    print("\n1.7. Minimal konfig:")
    run_command(f'{sys.executable} main.py --package django --url https://pypi.org/simple/')

    print("\n2.1. Getting dependencies React with no version:")
    run_command(f'{sys.executable} main.py --package express --url https://registry.npmjs.org')

    print("\n2.2. Getting dependencies React 16.14.0:")
    run_command(f'{sys.executable} main.py --package react --url https://registry.npmjs.org --version 16.14.0')

    print("\n2.3. Getting dependencies Lodash with filter 'es' (has no dependencies):")
    run_command(f'{sys.executable} main.py --package lodash --url https://registry.npmjs.org --filter es')


if __name__ == "__main__":
    main()