project(
    'geomodels', 'cpp', 'cython',
    license: 'MIT License',
    meson_version: '>=1.3.0',
    version: '1:0:0b5',
)

py = import('python').find_installation(pure: false)

geographiclib_dep = dependency('geographiclib')

py.extension_module(
    'geomodels._ext',
    'geomodels/_ext.pyx',
    dependencies: geographiclib_dep,
    install: true,
    override_options : ['cython_language=cpp'],
)
