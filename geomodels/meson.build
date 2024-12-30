py = import('python').find_installation(pure: false)

geographiclib_dep = dependency('geographiclib')

py.extension_module(
    '_ext',
    '_ext.pyx',
    dependencies: geographiclib_dep,
    install: true,
    subdir: meson.project_name(),
    override_options : ['cython_language=cpp'],
)

python_sources = [
    'cli.py',
    'data.py',
    'error.py',
    '__init__.py',
    '__main__.py',
    '_typing.py',
    '_utils.py',
    '_version.py',
    'wmmf.py',
]

py.install_sources(
    python_sources,
    # pure: false,
    subdir: meson.project_name(),
)

python_tests_sources = [
  'tests/__init__.py',
  'tests/test_cli.py',
  'tests/test_common.py',
  'tests/test_data.py',
  'tests/test_geoid.py',
  'tests/test_gravity.py',
  'tests/test_magnetic.py',
  'tests/test_wmmf.py',
  'tests/utils.py',
]

py.install_sources(
    python_tests_sources,
    # pure: false,
    subdir: meson.project_name() + '/tests',
)

python_test_data = [
  'tests/data/igrf12coeffs.txt',
]

py.install_sources(
    python_test_data,
    # pure: false,
    subdir: meson.project_name() + '/tests/data',
)
