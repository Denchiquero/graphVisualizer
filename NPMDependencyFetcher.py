import json
import urllib
from typing import Optional, Dict


class NPMDependencyFetcher:

    def __init__(self, registry_url: str = "https://registry.npmjs.org"):
        self.registry_url = registry_url.rstrip('/')
        self.package_version = None

    def get_package_info(self, package_name: str, version: str = None) -> Optional[Dict]:
        try:

            self.package_version = version

            url = f"{self.registry_url}/{package_name}"
            if version:
                url = f"{self.registry_url}/{package_name}/{version}"

            print(f"\nFetch: {url}")

            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return data
                else:
                    print(f"HTTP error: {response.status}")
                    return None

        except urllib.error.HTTPError as e:
            print(f"HTTP error getting package {package_name}: {e.code} {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"URL error getting package {package_name}: {e.reason}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON parsing error for package {package_name}: {e}")
            return None
        except Exception as e:
            print(f"error {package_name}: {e}")
            return None

    def extract_dependencies(self, package_info: Dict) -> Dict[str, str]:

        dependencies = {}

        try:

            version_data = None
            if 'version' in package_info:

                version_data = package_info
            elif 'versions' in package_info and package_info.get('dist-tags', {}).get('latest'):

                latest_version = package_info['dist-tags']['latest']
                version_data = package_info['versions'].get(latest_version, {})
            elif 'versions' in package_info and self.package_version:

                version_data = package_info['versions'].get(self.package_version, {})

            if version_data:

                deps = version_data.get('dependencies', {})
                dev_deps = version_data.get('devDependencies', {})
                peer_deps = version_data.get('peerDependencies', {})

                all_deps = {**deps, **dev_deps, **peer_deps}
                dependencies.update(all_deps)

        except Exception as e:
            print(f"Ошибка при извлечении зависимостей: {e}")

        return dependencies

    def get_dependencies(self, package_name: str, version: str = None) -> Dict[str, str]:

        package_info = self.get_package_info(package_name, version)
        if not package_info:
            return {}

        return self.extract_dependencies(package_info)