# A Python Interface to [PentagonFunctions++](https://gitlab.com/pentagon-functions/PentagonFunctions-cpp)

## Requirements
The following Python packages are required (automatically installed by pip)
```
numpy, mpmath, lips, whichcraft
```
The following C++ library is required, pip will attempt to install it automatically if `pentagon_functions_evaluator_python` is not found. To attempt this automatic installation pass `[with-cpp]` to ensure `ninja` and `meson` are present
```
PentagonFunctions-cpp
```

##  How It Works
The interface communicates using string-based input/output via the terminal.
The script `pentagon_functions_evaluator_python` is searched for in the system path.
If it is not found, `~/local/bin/` is checked as an alternative location.

## Installation
In this folder do
```
pip install -e .[with-cpp]
```

## Quick Start

```python
import numpy
from lips import Particles
from pentagon_functions import evaluate_pentagon_functions, fix_parity_odd

# Phase space point given in 2010.15834, pass it to lips.Particles
oPsBenchmark = Particles(5, real_momenta=True)
oPsBenchmark[1].four_mom = numpy.array([(-0.575 + 0j), (-0.575 + 0j), 0j, 0j])
oPsBenchmark[2].four_mom = numpy.array([(-0.575 + 0j), (0.575 + 0j), 0j, 0j])
oPsBenchmark[3].four_mom = numpy.array([(0.4588582395652173 + 0j), (0.405584802173913 + 0j), (0.20777834301052356 + 0j), (-0.05366574734632376 + 0j)])
oPsBenchmark[4].four_mom = numpy.array([(0.23112940869565216 + 0j), (-0.09707956260869566 + 0j), (0.009377939347234585 + 0j), (-0.20954335193774518 + 0j)])
oPsBenchmark[5].four_mom = numpy.array([(0.46001235173913047 + 0j), (-0.3085052395652174 + 0j), (-0.2171562823577582 + 0j), (0.263209099284069 + 0j)])

numerical_pentagon_dict = evaluate_pentagon_functions(
    ['F[3,25]', 'F[4,347]', 'F[3,22]', 'F[4,115]', 'F[3,1]', 'F[4,122]', 'F[4,365]'],
    oPsBenchmark, precision="d", verbose=False)

# if 'str5' is explicitly given in the basis of pentagon functions skip this step
numerical_pentagon_dict = fix_parity_odd(numerical_pentagon_dict, oPsBenchmark)

print(numerical_pentagon_dict)
>> {'F[3,25]': mpc(real='-1.690898346368268995', imag='2.52880034356816602'), 
    'F[4,347]': mpc(real='29.09482723195550014', imag='110.0170381265092008'), 
    'F[3,22]': mpc(real='-14.08863918406784999', imag='14.47902381510688996'), 
    'F[4,115]': mpc(real='-2.971610560487019992', imag='-15.43365955947793999'), 
    'F[3,1]': ... }
```