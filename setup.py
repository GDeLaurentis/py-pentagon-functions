import subprocess
import warnings

from pathlib import Path

from setuptools import setup, find_packages
from setuptools.command.build_ext import build_ext

this_directory = Path(__file__).parent


class MesonBuildExt(build_ext):
    def run(self):

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
        ninja_cmd = ['ninja', '-C', str(build_dir)]
        subprocess.run(ninja_cmd, check=True, capture_output=False, text=True, cwd=build_dir)

        # Run Ninja install inside build_dir
        print("\nRunning Ninja install:")
        install_cmd = ['ninja', '-C', str(build_dir), 'install']
        subprocess.run(install_cmd, check=True, capture_output=False, text=True, cwd=build_dir)


# Check if 'with-cpp' was explicitly requested in the last pip call
result = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE, text=True)
result = result.stdout.splitlines()[:]
# print("Last invocations:",result)
result = [entry for entry in result if 'pip install' in entry]
if len(result) > 0:
    with_cpp = 'with-cpp' in result
else:
    warnings.warn("Could not determine if with-cpp was requested, defaulting to False unless directly invoked.")
    with_cpp = True if __name__ == "__main__" else False
print("With cpp:", with_cpp)

# Conditionally set cmdclass
cmdclass = {'build_ext': MesonBuildExt} if with_cpp else {}


setup(
    name='pentagon_functions',
    version='v0.0.1',
    author='Giuseppe De Laurentis, and the Pentagon Functions authors',
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
)
