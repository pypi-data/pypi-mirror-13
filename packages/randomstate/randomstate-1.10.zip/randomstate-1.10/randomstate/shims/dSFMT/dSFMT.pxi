DEF RNG_NAME = 'dSFMT'
DEF RNG_ADVANCEABLE = 0
DEF RNG_SEED = 1
DEF RNG_JUMPABLE = 0
DEF RNG_STATE_LEN = 4
DEF NORMAL_METHOD = 'zig'
DEF DSFMT_MEXP = 19937
DEF DSFMT_N = 191 # ((DSFMT_MEXP - 128) / 104 + 1)
DEF DSFMT_N_PLUS_1 = 192 # DSFMT_N + 1

ctypedef uint32_t rng_state_t

cdef extern from "distributions.h":

    cdef union W128_T:
        uint64_t u[2];
        uint32_t u32[4];
        double d[2];

    ctypedef W128_T w128_t;

    cdef struct DSFMT_T:
        w128_t status[DSFMT_N_PLUS_1];
        int idx;

    ctypedef DSFMT_T dsfmt_t;

    cdef struct s_aug_state:
        dsfmt_t *rng
        binomial_t *binomial

        int has_gauss, shift_zig_random_int, has_uint32
        double gauss
        uint64_t zig_random_int
        uint32_t uinteger

        double *buffered_uniforms
        int buffer_loc

    ctypedef s_aug_state aug_state

    cdef void set_seed(aug_state* state, uint32_t seed)

    cdef void set_seed_by_array(aug_state* state, uint32_t init_key[], int key_length)

ctypedef dsfmt_t rng_t

cdef object _get_state(aug_state state):
    cdef uint32_t [::1] key = np.zeros(4 * DSFMT_N_PLUS_1, dtype=np.uint32)
    cdef double [::1] buf = np.zeros(2 * DSFMT_N, dtype=np.double)
    cdef Py_ssize_t i, j, key_loc = 0
    cdef w128_t state_val
    for i in range(DSFMT_N_PLUS_1):
        state_val = state.rng.status[i]
        for j in range(4):
            key[key_loc] = state_val.u32[j]
            key_loc += 1
    for i in range(2 * DSFMT_N):
        buf[i] = state.buffered_uniforms[i]

    return (np.asarray(key), state.rng.idx,
            np.asarray(buf), state.buffer_loc)

cdef object _set_state(aug_state *state, object state_info):
    cdef Py_ssize_t i, j, key_loc = 0
    cdef uint32_t [::1] key = state_info[0]
    state.rng.idx = state_info[1]


    for i in range(DSFMT_N_PLUS_1):
        for j in range(4):
            state.rng.status[i].u32[j] = key[key_loc]
            key_loc += 1

    state.buffer_loc = <int>state_info[3]
    for i in range(2 * DSFMT_N):
        state.buffered_uniforms[i] = state_info[2][i]




DEF CLASS_DOCSTRING = """
RandomState(seed=None)

Container for the SIMD-based Mersenne Twister pseudo-random number generator.

``dSFMT.RandomState`` exposes a number of methods for generating random
numbers drawn from a variety of probability distributions. In addition to the
distribution-specific arguments, each method takes a keyword argument
`size` that defaults to ``None``. If `size` is ``None``, then a single
value is generated and returned. If `size` is an integer, then a 1-D
array filled with generated values is returned. If `size` is a tuple,
then an array with that shape is filled and returned.

*No Compatibility Guarantee*
'dSFMT.RandomState' does not make a guarantee that a fixed seed and a
fixed series of calls to 'dSFMT.RandomState' methods using the same
parameters will always produce the same results. This is different from
'numpy.random.RandomState' guarantee. This is done to simplify improving
random number generators.  To ensure identical results, you must use the
same release version.

Parameters
----------
seed : {None, int}, optional
    Random seed initializing the pseudo-random number generator.
    Can be an integer in [0, 2**32] or ``None`` (the default).
    If `seed` is ``None``, then ``dSFMT.RandomState`` will try to read
    entropy from ``/dev/urandom`` (or the Windows analogue) if available to
    produce a 64-bit seed. If unavailable, the a 64-bit hash of the time
    and process ID is used.

Notes
-----
The Python stdlib module "random" also contains a Mersenne Twister
pseudo-random number generator with a number of methods that are similar
to the ones available in `RandomState`. `RandomState`, besides being
NumPy-aware, has the advantage that it provides a much larger number
of probability distributions to choose from.
"""
