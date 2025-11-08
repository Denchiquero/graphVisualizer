#!/usr/bin/env python3
"""
Тесты для проверки функциональности получения зависимостей
"""

import unittest
from unittest.mock import patch, MagicMock
from main import NPMDependencyFetcher


class TestNPMDependencyFetcher(unittest.TestCase):

    def setUp(self):
        self.fetcher = NPMDependencyFetcher()

    @patch('urllib.request.urlopen')
    def test_get_package_info_success(self, mock_urlopen):

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"name": "react", "version": "18.2.0"}'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.fetcher.get_package_info('react')

        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'react')
        self.assertEqual(result['version'], '18.2.0')

    def test_extract_dependencies(self):

        package_info = {
            'dependencies': {
                'prop-types': '^15.0.0',
                'loose-envify': '^1.0.0'
            },
            'devDependencies': {
                'jest': '^29.0.0'
            }
        }

        dependencies = self.fetcher.extract_dependencies(package_info)

        self.assertEqual(len(dependencies), 3)
        self.assertIn('prop-types', dependencies)
        self.assertIn('loose-envify', dependencies)
        self.assertIn('jest', dependencies)

    def test_extract_dependencies_empty(self):

        package_info = {}

        dependencies = self.fetcher.extract_dependencies(package_info)

        self.assertEqual(len(dependencies), 0)


if __name__ == '__main__':
    unittest.main()