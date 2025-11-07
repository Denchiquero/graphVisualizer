import unittest
import tempfile
import os
from main import DependencyGraphConfig


class TestDependencyGraphConfig(unittest.TestCase):

    def setUp(self):
        self.config = DependencyGraphConfig()

    # Тест валидной конфигурации с URL
    def test_valid_config_with_url(self):

        self.config.package_name = "requests"
        self.config.repository_url = "https://pypi.org/simple/"
        self.config.test_mode = True
        self.config.package_version = "2.28.0"
        self.config.filter_substring = "http"

        self.assertTrue(self.config.validate())
        self.assertEqual(len(self.config.errors), 0)

    #Тест валидной конфигурации с путем к файлу
    def test_valid_config_with_path(self):

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('test data')
            temp_path = f.name

        try:
            self.config.package_name = "numpy"
            self.config.repository_path = temp_path
            self.config.test_mode = True
            self.config.package_version = "1.21.0"

            self.assertTrue(self.config.validate())
            self.assertEqual(len(self.config.errors), 0)
        finally:
            os.unlink(temp_path)

    # Тест отсутствия имени пакета
    def test_missing_package_name(self):

        self.config.repository_url = "https://pypi.org/simple/"

        self.assertFalse(self.config.validate())
        self.assertIn("Имя пакета обязательно", self.config.errors[0])

    # Тест указания и URL и пути одновременно
    def test_both_url_and_path(self):

        self.config.package_name = "package"
        self.config.repository_url = "https://pypi.org/simple/"
        self.config.repository_path = "/some/path"

        self.assertFalse(self.config.validate())
        self.assertIn("Можно указать только URL репозитория ИЛИ путь", self.config.errors[0])

    # Тест отсутствия и URL и пути
    def test_neither_url_nor_path(self):

        self.config.package_name = "package"

        self.assertFalse(self.config.validate())
        self.assertIn("Необходимо указать либо URL репозитория", self.config.errors[0])

    # Тест некорректного URL
    def test_invalid_url(self):

        self.config.package_name = "package"
        self.config.repository_url = "not-a-valid-url"

        self.assertFalse(self.config.validate())
        self.assertIn("Некорректный URL", self.config.errors[0])

    # Тест несуществующего файла
    def test_nonexistent_file(self):

        self.config.package_name = "package"
        self.config.repository_path = "/nonexistent/path/file.json"
        self.config.test_mode = True

        self.assertFalse(self.config.validate())
        self.assertIn("Файл не существует", self.config.errors[0])

    # Тест некорректного формата версии
    def test_invalid_version_format(self):

        self.config.package_name = "package"
        self.config.repository_url = "https://pypi.org/simple/"
        self.config.package_version = ""  # Пустая версия

        self.assertFalse(self.config.validate())
        self.assertIn("Некорректный формат версии", self.config.errors[0])

    # Тест преобразования в словарь
    def test_to_dict_method(self):

        self.config.package_name = "test-package"
        self.config.repository_url = "https://test.org/"
        self.config.test_mode = True
        self.config.package_version = "1.0.0"
        self.config.filter_substring = "test"

        config_dict = self.config.to_dict()

        self.assertEqual(config_dict['package_name'], "test-package")
        self.assertEqual(config_dict['repository_url'], "https://test.org/")
        self.assertEqual(config_dict['test_mode'], True)
        self.assertEqual(config_dict['package_version'], "1.0.0")
        self.assertEqual(config_dict['filter_substring'], "test")


if __name__ == '__main__':
    unittest.main()