py = import('python').find_installation(pure: false)

geographiclib_dep = dependency('geographiclib')

py.extension_module(
    '_ext',
    'geomodels/_ext.pyx',
    dependencies: geographiclib_dep,
    install: true,
    override_options : ['cython_language=cpp'],
)
