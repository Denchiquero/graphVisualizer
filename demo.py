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


def create_test_repo_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        f.write('''{
  "A": {"B": "^1.0.0", "C": "^2.0.0"},
  "B": {"D": "^1.0.0", "E": "^1.0.0"},
  "C": {"D": "^1.0.0", "F": "^1.0.0"},
  "D": {"B": "^1.0.0"},
  "E": {},
  "F": {"G": "^1.0.0"},
  "G": {}
}''')
        return f.name

def create_test_cycle():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        f.write('''{
          "A": {"B": "^1.0.0", "C": "^2.0.0"},
          "B": {"D": "^1.0.0", "E": "^1.0.0"},
          "C": {"D": "^1.0.0", "F": "^1.0.0"},
          "D": {"B": "^1.0.0", "G": "^1.0.0"},
          "E": {"H": "^1.0.0"},
          "F": {"I": "^1.0.0"},
          "G": {"A": "^1.0.0"},
          "H": {},
          "I": {"J": "^1.0.0"},
          "J": {}
        }''')
        return f.name

def main():

    print("Demo")

    # print("\n1.1. Run with url:")
    # run_command(
    #     f'{sys.executable} main.py --package requests --url https://pypi.org/simple/ --version 2.28.0 --filter "http"')
    #
    # temp_file = None
    # try:
    #     temp_file = create_test_file()
    #     print("\n1.2. Run with file in test mode:")
    #     run_command(f'{sys.executable} main.py --package numpy --path "{temp_file}" --test-mode --version 1.21.0')
    # finally:
    #     if temp_file and os.path.exists(temp_file):
    #         os.unlink(temp_file)
    #
    # print("\n1.3. No --package:")
    # run_command(f'{sys.executable} main.py --url https://pypi.org/simple/')
    #
    # print("\n1.4. url and path both:")
    # run_command(f'{sys.executable} main.py --package test --url https://pypi.org/simple/ --path file.json')
    #
    # print("\n1.5. invalid url")
    # run_command(f'{sys.executable} main.py --package test --url invalid-url')
    #
    # print("\n1.6. help")
    # run_command(f'{sys.executable} main.py --help')
    #
    # print("\n1.7. Minimal konfig:")
    # run_command(f'{sys.executable} main.py --package django --url https://pypi.org/simple/')

    # print("\n2.1. Getting dependencies React with no version:")
    # run_command(f'{sys.executable} main.py --package express --url https://registry.npmjs.org')
    #
    # print("\n2.2. Getting dependencies React 16.14.0:")
    # run_command(f'{sys.executable} main.py --package react --url https://registry.npmjs.org --version 16.14.0')
    #
    # print("\n2.3. Getting dependencies Lodash with filter 'es' (has no dependencies):")
    # run_command(f'{sys.executable} main.py --package lodash --url https://registry.npmjs.org --filter es')

    print("\n3.1. Test mode with file (cyclic dependencies):")
    test_file = create_test_repo_file()
    run_command(f'{sys.executable} main.py --package A --path "{test_file}" --test-mode')

    print("\n3.2. Test mode with filter:")
    run_command(f'{sys.executable} main.py --package A --path "{test_file}" --test-mode --filter "B"')

    print("\n3.3. Real NPM package with transitive dependencies:")
    run_command(f'{sys.executable} main.py --package express --url https://registry.npmjs.org')

    print("\n3.4. Express with limited depth:")
    run_command(f'{sys.executable} main.py --package express --url https://registry.npmjs.org --max-depth 2')

    print("\n3.5. No dependencies:")
    run_command(f'{sys.executable} main.py --package lodash --url https://registry.npmjs.org')

    print("\n3.6. Cycles:")
    test_cycle = create_test_cycle()
    run_command(f'{sys.executable} main.py --package A --path "{test_cycle}" --test-mode --max-depth 7')




if __name__ == "__main__":
    main()