import re
import subprocess
import functools
import pathlib
import mpmath
import whichcraft
import warnings

from copy import deepcopy

# Author: Giuseppe

script_directory = None
if whichcraft.which("pentagon_functions_evaluator_python") is None:
    if pathlib.Path("~/local/bin/pentagon_functions_evaluator_python").expanduser().exists():
        script_directory = str(pathlib.Path("~/local/bin").expanduser())
    else:
        warnings.warn("Couldn't locate pentagon_functions_evaluator_python! Won't be able to evaluate pentagon functions")    


# Constant data

constants = {
    'tci[1,1]': 1j * mpmath.pi,
    'tci[1,2]': 1j * mpmath.pi,
    'tci[2,1]': mpmath.mpmathify('1.01494160640965362502120255427452028594168930753029979201748910677659747625824j'),
    'tci[3,1]': mpmath.mpmathify('0.57068163536563662179769055067238392601963107788880633412884021759219376534843j'),
    'tci[3,2]': mpmath.mpmathify('1.95805792209958948875223725953776226311620663441329003133540714588177706642244j'),
    'tci[4,1]': mpmath.mpmathify('0.9158468848305221005784557354615554066325218024536092822321305122909406032199j'),
    'tci[4,2]': mpmath.mpmathify('0.57506902367961493370903615395302608738483177035427241988595161280872934244094j'),
    'tci[4,3]': mpmath.mpmathify('7.63587387430075836809558431362434791200091165900221605545744819859116757903429j'),
    'tcr[1,1]': mpmath.mpmathify('1.09861228866810969139524523692252570464749055782274945173469433363749429321861'),
    'tcr[1,2]': mpmath.mpmathify('0.6931471805599453094172321214581765680755001343602552541206800094933936219697'),
    'tcr[2,1]': mpmath.mpmathify('0.83327188647738995744101246196890039744072476234026111025888050483590803187341'),
    'tcr[3,1]': mpmath.mpmathify('0.73806064483085791066377614636565032547367306985351329858054523307043380943959'),
    'tcr[3,2]': mpmath.mpmathify('0.25846139579657330528800012987367261202162535352798804747584081415085729951564'),
    'tcr[3,3]': mpmath.mpmathify('1.20205690315959428539973816151144999076498629234049888179227155534183820558957'),
    'tcr[4,1]': mpmath.mpmathify('0.34079113085625075247764094401220231521228085828689962786864627412151691807202'),
    'tcr[4,2]': mpmath.mpmathify('0.51747906167389938633075816189886294562237747514137925824431934797700828158186'),
    'tcr[4,3]': mpmath.mpmathify('0.2541161907463435340596737131535205829398478245574739638781062235368841219817'),
    'tcr[4,4]': mpmath.mpmathify('0.69919359449299809540702260849718121951534934751545290997293176683694496096964'),
    'tcr[4,5]': mpmath.mpmathify('0.79222102797282777952948578955735741116739480858778316087280447831968760156385')
}

oddFs = [[[3, 1], [3, 2], [3, 3], [3, 4], [3, 5]],
         [[2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7], [2, 8], [2, 9]],
         [[23], [25], [26], [43], [45], [46], [62], [63], [64], [70], [71], [72], [78], [80], [81], [82], [83], [88], [93], [98], [103]],
         [[25], [28], [39], [41], [45], [49], [51], [54], [61], [63], [64], [80], [83], [91], [93], [96], [100], [102], [105], [111], [113],
          [114], [129], [132], [139], [141], [142], [146], [148], [151], [156], [158], [159], [171], [174], [182], [184], [188], [190], [192],
          [195], [199], [201], [202], [213], [215], [219], [221], [225], [229], [233], [234], [235], [244], [246], [250], [252], [255], [259],
          [262], [263], [271], [273], [277], [279], [282], [286], [289], [290], [291], [293], [295], [299], [302], [303], [309], [313], [315],
          [316], [317], [325], [330], [331], [332], [333], [334], [335], [336], [337], [338], [339], [340], [343], [346], [348], [349], [350],
          [353], [356], [358], [359], [360], [363], [366], [368], [369], [371], [372], [373], [375], [376], [377], [378], [379], [380], [381],
          [382], [383], [384], [385], [386], [387], [388], [389], [390], [393], [396], [398], [399], [400], [403], [406], [408], [409], [411],
          [412], [413], [414], [415], [416], [417], [418], [419], [420], [421], [422], [425], [428], [429], [430], [431], [432], [433], [434],
          [435], [436]]]
oddtcis = [[1], [1], [1, 2], [1, 2, 3]]


# Functions

def make_hashable(func):
    """Turns the first argument from list to tuple so it can be hashed."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(tuple(args[0]), *args[1:], **kwargs)
    return wrapper


@make_hashable
@functools.lru_cache(maxsize=256)
def evaluate_pentagon_functions(pentagon_monomials, phase_space_point,
                                pentagon_function_set=["m0", "m1"][0], precision=["d", "q", "o"][0],
                                number_of_cores=8, verbose=False):
    """Calls PentagonFunctions++ via pyInterface.cpp"""
    assert precision in ["d", "q", "o"]
    assert pentagon_function_set in ["m0", "m1"]
    assert isinstance(number_of_cores, int)
    # set precision in mpmath
    if precision == "d":
        mpmath.mp.dps = 16
    elif precision == "q":
        mpmath.mp.dps = 32
    elif precision == "o":
        mpmath.mp.dps = 64
    # build pentagon string of indices, eg: 1 1 1;1 1 2;E
    pentagon_monomials = [monomial for monomial in pentagon_monomials if "F" in monomial]
    pentagon_monomials_as_indices = ["{" + ",".join(re.findall(r"(\d+)", entry)) + "}" for entry in pentagon_monomials]
    pentagon_input_string = ";".join(pentagon_monomials_as_indices).replace("{", "").replace("}", "").replace(",", " ") + ";E"
    # build mandelstams - drop imaginary part, it should be numerically small, if at all present
    if pentagon_function_set == "m0":
        s12, s23, s34, s45, s15 = phase_space_point("s12"), phase_space_point("s23"), phase_space_point("s34"), phase_space_point("s45"), phase_space_point("s15")
        s12, s23, s34, s45, s15 = [mpmath.mpf(mandel.real) for mandel in [s12, s23, s34, s45, s15]]
    elif pentagon_function_set == "m1":
        # LHV: five point 1-mass notation with p1^2 != 0, RHS: six-point massless notation with p1 -> p1 + p2, p2 -> p3, etc..
        p1s, s12, s23, s34, s45, s15 = (
            phase_space_point("s12"), phase_space_point("s123"), phase_space_point("s34"),
            phase_space_point("s45"), phase_space_point("s56"), phase_space_point("s126")
        )
        p1s, s12, s23, s34, s45, s15 = [mpmath.mpf(mandel.real) for mandel in [p1s, s12, s23, s34, s45, s15]]
    # call PentagonFunctions++ via pyInterface.cpp
    args = (
        [("" if script_directory is None else "./") + "pentagon_functions_evaluator_python"] +
        [pentagon_function_set, precision, str(number_of_cores)]
    )
    if verbose:
        print("Calling PentagonFunctions-cpp with args:", [
            ("" if script_directory is None else "./") + "pentagon_functions_evaluator_python"] +
            [pentagon_function_set, precision, str(number_of_cores)],
            )
    PentagonFunctions_cppInterface = subprocess.Popen(
        args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=script_directory)
    PentagonFunctions_cppInterface.stdin.write(pentagon_input_string.encode())
    if pentagon_function_set == "m0":
        if verbose:
            print(f"Passing kin info: {s12} {s23} {s34} {s45} {s15}")
        PentagonFunctions_cppInterface.stdin.write(f"{s12} {s23} {s34} {s45} {s15}".encode())
    elif pentagon_function_set == "m1":
        if verbose:
            print(f"Passing kin info: {p1s} {s12} {s23} {s34} {s45} {s15}")
        PentagonFunctions_cppInterface.stdin.write(f"{p1s} {s12} {s23} {s34} {s45} {s15}".encode())
    stdout, stderr = PentagonFunctions_cppInterface.communicate()
    stdout, stderr = stdout.decode(), stderr.decode()
    if verbose:
        print("Output received from PentagonFunctions-cpp:")
        print(stdout)
        print("Error received from PentagonFunctions-cpp:")
        print(stderr)
    if "Kinematical point is not in the physical region! Delta is >0" in stderr:
        raise ValueError("Kinematical point is not in the physical region! Delta is >0")
    # do some light parsing
    content = re.sub(r"`\d+(\.\d*){0,1}", "", stdout)
    content = content.replace("*I", "j").replace("I*", "1j*").replace("*^", "e").replace("^", "**").replace("{", "").replace("}", "")
    content = re.sub(r"1j\*([\-\+\d\.e]*)", r"\1j", content).replace(" ", "").replace("+-", "-").replace("\n", "")
    numerical_result = [mpmath.mpmathify(entry) for entry in content.split(",")]
    numerical_pentagon_dict = dict(zip(pentagon_monomials, numerical_result))
    if pentagon_function_set == "m0":
        numerical_pentagon_dict = {**numerical_pentagon_dict, **constants, **{'1': 1}}
    elif pentagon_function_set == "m1":
        numerical_pentagon_dict = {**numerical_pentagon_dict, **{
            "im[1,1]": 1j * mpmath.pi, "re[3,1]": mpmath.zeta(3)}, **{'1': 1}, **{
            "one_over_sqrtG3[1]": 1 / mpmath.sqrt(p1s ** 2 + (s23 - s45) ** 2 - 2 * p1s * (s23 + s45)),
            "one_over_sqrtG3[2]": 1 / mpmath.sqrt(p1s ** 2 + (s12 - s15 + s23 - s45) ** 2 - 2 * p1s * (s12 + s15 - s23 - 2 * s34 - s45)),
            "one_over_sqrtG3[3]": 1 / mpmath.sqrt(s12 ** 2 + 2 * s12 * s15 + s15 ** 2 - 4 * p1s * s34),
            "-str5": -mpmath.sign(phase_space_point("tr5_3456").imag)}
        }
    return numerical_pentagon_dict


def fix_parity_odd(numerical_pentagon_dict, phase_space_point, verbose=False):
    """
    Fixes the sign of some functions depending on the sign of the imaginary part of tr5.
    If the pentagon functions basis already implements this with explicit factors of -str5 then this function should NOT be called.
    """
    numerical_pentagon_dict = deepcopy(numerical_pentagon_dict)  # Better return a copy, else this is passed by reference
    if (1j * phase_space_point("tr5_1234")).real < 0:
        if verbose:
            print("Flipping F's")
        # flip odd F's
        for weight, l_odd_pentagon_indices in enumerate(oddFs):
            for odd_pentagon_indices in l_odd_pentagon_indices:
                function_name = f'F[{weight+1},' + ','.join(map(str, odd_pentagon_indices)) + ']'
                if function_name in numerical_pentagon_dict.keys():
                    numerical_pentagon_dict[function_name] = -numerical_pentagon_dict[function_name]
        # flip odd tci's
        if verbose:
            print("Flipping tci's")
        for weight, l_odd_pentagon_indices in enumerate(oddtcis):
            for odd_pentagon_index in l_odd_pentagon_indices:
                function_name = f'tci[{weight+1},{odd_pentagon_index}]'
                if function_name in numerical_pentagon_dict.keys():
                    numerical_pentagon_dict[function_name] = -numerical_pentagon_dict[function_name]
    return numerical_pentagon_dict
