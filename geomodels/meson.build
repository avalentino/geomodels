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
  pure: false,
  subdir: meson.project_name(),
)