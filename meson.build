project(
    'geomodels',
    'cpp', 'cython',
    license: 'MIT License',
    meson_version: '>=1.3.0',
    version: run_command(
        [
            'python3',
            '-c',
            'print(open("geomodels/_version.py").read().split("=")[-1])'
        ],
        check: true
    ).stdout().strip().strip('"'),
    default_options: ['cpp_std=c++11'],
)

subdir(meson.project_name())
