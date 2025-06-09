# ChemicHull Checking

This repository contains the code used in the paper "Complete polyhedral description of chemical graphs of
maximum degree at most 3" to verify the list of points for each full-dimensional polytope.

The main file is `smt_check.py`. Description of the polytopes are located in file `families.py` and points are in `points.py`

## Usage

Install the required python libraries using `pip install -r requirements.txt`.

The computation can be run with the command `python smt_check.py [MIN] [MAX]`, where `MIN` is the minimum index of the family to consider and `MAX` is the maximum index of the family to consider. For example, the command `python smt_check.py 0 6` will compute the extremal points for the first 7 families.

Values default to 0 for `MIN` and $\infty$ for `MAX`.

```
usage: python smt_check.py [-h] [MIN] [MAX]

positional arguments:
  MIN
  MAX

options:
  -h, --help  show this help message and exit
```

### Timeouts

Because SMT solving is NP-Hard, runtimes can be long. In order to obtain as much information as possible, two timeout values are provided at the top of the file `smt_check.py`.

- `TIMEOUT`: if larger than zero, the computation for a polytope will stop after the given number of seconds. Computation will then start for the next polytope.
- `INTERSECTION_TIMEOUT`: if larger than zero, the computation for an intersection will stop after the given number of seconds. Computation will then start for the next intersection.

In case of a timeout, a `TIMEOUT` message will be shown.

## Requirements

Below are the requirements for the code. We use `sympy` and `z3-solver` to perform the verification and `mpmath` is a dependency of `sympy`.

```
mpmath==1.3.0
sympy==1.14.0
z3-solver==4.15.1.0
```

## Outputs

For each polytope, the system will compute the intersections for each triplet of facet. For each intersection, we check that it is always valid (for every order and size satisfying the existential constraints) and compute the list of points indentified in the paper that correspond to the intersection. Should none of them be valid, an error will be generated.

The output consist of the list, for each polytope, of the intersections as well as details about whether it is valid and the list of points corresponding to the intersection.

A list of the points of the polytope will be outputed as a summary after each polytope is computed.
