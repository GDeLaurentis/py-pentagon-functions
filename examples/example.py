import numpy

from lips import Particles
from pentagon_functions import evaluate_pentagon_functions, fix_parity_odd

# Example usage

if __name__ == "__main__":
    # Phase space point given in 2010.15834, defined using github.com/GDeLaurentis/lips
    oPsBenchmark = Particles(5, real_momenta=True)
    oPsBenchmark[1].four_mom = numpy.array([(-0.575 + 0j), (-0.575 + 0j), 0j, 0j])
    oPsBenchmark[2].four_mom = numpy.array([(-0.575 + 0j), (0.575 + 0j), 0j, 0j])
    oPsBenchmark[3].four_mom = numpy.array([(0.4588582395652173 + 0j), (0.405584802173913 + 0j), (0.20777834301052356 + 0j), (-0.05366574734632376 + 0j)])
    oPsBenchmark[4].four_mom = numpy.array([(0.23112940869565216 + 0j), (-0.09707956260869566 + 0j), (0.009377939347234585 + 0j), (-0.20954335193774518 + 0j)])
    oPsBenchmark[5].four_mom = numpy.array([(0.46001235173913047 + 0j), (-0.3085052395652174 + 0j), (-0.2171562823577582 + 0j), (0.263209099284069 + 0j)])

    numerical_pentagon_dict = evaluate_pentagon_functions(
        ['F[3,25]', 'F[4,347]', 'F[3,22]', 'F[4,115]', 'F[3,1]', 'F[4,122]', 'F[4,365]'],
        oPsBenchmark, precision="d", verbose=False)

    numerical_pentagon_dict = fix_parity_odd(numerical_pentagon_dict, oPsBenchmark)

    print(numerical_pentagon_dict)
