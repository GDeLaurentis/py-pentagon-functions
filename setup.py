import subprocess

from pathlib import Path

from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


with (this_directory / "pentagon_functions" / "version.py").open() as f:
    exec(f.read())
    version = __version__  # noqa


class MesonBuildExt(build_ext):
    def run(self):
        import whichcraft
        
        if (whichcraft.which("pentagon_functions_evaluator_python") is not None or
            Path("~/local/bin/pentagon_functions_evaluator_python").expanduser().exists()):
            print("\nPentagonFunctions-cpp already found - skipping installation.")
            return

        repo_url = "https://gitlab.com/pentagon-functions/PentagonFunctions-cpp.git"
        repo_dir = this_directory / "PentagonFunctions-cpp"
        build_dir = repo_dir / "build"
        prefix_directory = Path.home() / "local"

        # Clone the repository if it doesn't exist
        if not repo_dir.exists():
            print("\nCloning PentagonFunctions-cpp repository:")
            subprocess.run(["git", "clone", "--branch", "devel", repo_url, str(repo_dir)], check=True)
        else:
            print("\nRepository already exists, updating it:")
            subprocess.run(["git", "-C", str(repo_dir), "fetch"], check=True)
            subprocess.run(["git", "-C", str(repo_dir), "pull"], check=True)

        # Create the build directory if it doesn't exist
        build_dir.mkdir(parents=True, exist_ok=True)    

        # Check if Meson is already configured in build_dir
        if not (build_dir / 'meson-private').exists():
            # Run Meson setup outside build_dir - TODO: improve, e.g. if QD is available
            print("\nRunning Meson setup:")
            meson_cmd = ['meson', 'setup', str(build_dir), f'-Dprefix={prefix_directory}']
            subprocess.run(meson_cmd, check=True, capture_output=False, text=True, cwd=repo_dir)
        else:
            print("\nMeson setup already complete; skipping reconfiguration.")

        # Run Ninja build inside build_dir
        print("\nRunning Ninja build:")
        subprocess.run(['ninja'], check=True, capture_output=False, text=True, cwd=build_dir)

        # Run Ninja install inside build_dir
        print("\nRunning Ninja install:")
        subprocess.run(['ninja', 'install'], check=True, capture_output=False, text=True, cwd=build_dir)


# It appears to be hard to determine whether pip was called with any extra such as with-cpp
# Instead decide whether to install cpp depending on whether the pentagon_functions_evaluator_python is visible.
cmdclass = {'build_ext': MesonBuildExt}


setup(
    name='pentagon_functions',
    version=version,
    description='A Python interface to PentagonFunctions-cpp',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Giuseppe De Laurentis and the Pentagon Functions authors',
    url='https://github.com/GDeLaurentis/py-pentagon-functions',
    download_url=f'https://github.com/GDeLaurentis/py-pentagon-functions/archive/v{version}.tar.gz',
    project_urls={
#        'Documentation': 'https://gdelaurentis.github.io/py-pentagon-functions/',
        'Issues': 'https://github.com/GDeLaurentis/py-pentagon-functions/issues',
    },
    keywords=['Scattering Amplitudes', 'Feynman Integrals', 'Pentagon Functions'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=['numpy',
                      'mpmath',
                      'lips',
                      'whichcraft'],
    extras_require={
        'with-cpp': ['meson', 'ninja']
    },
    cmdclass=cmdclass,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
