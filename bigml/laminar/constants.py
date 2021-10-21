NUMERIC = "numeric"
CATEGORICAL = "categorical"

TEST_MODEL = "test"
SINGLE_MODEL = "single"
MODEL_SEARCH = "search"
SHUTDOWN = "shutdown"

DEFAULT_PORT = 8042
DEFAULT_MAX_JOBS = 4

ERROR = "error"
QUEUED = "queued"
STARTED = "started"
IN_PROGRESS = "in-progress"
FINISHED = "finished"

# This can be any x where np.exp(x) + 1 == np.exp(x)  Going up to 512
# isn't strictly necessary, but hey, why not?
LARGE_EXP = 512

EPSILON = 1e-4

# Parameters that can appear in the layers of models
MATRIX_PARAMS = [
    'weights'
]

VEC_PARAMS = [
    'mean',
    'variance',
    'offset',
    'scale',
    'stdev'
]

# Model search parameters
VALIDATION_FRAC = 0.15
MAX_VALIDATION_ROWS = 4096
LEARN_INCREMENT = 8
MAX_QUEUE = LEARN_INCREMENT * 4
N_CANDIDATES = MAX_QUEUE * 64

# Activation constants
ALPHA = 1.6732632423543772848170429916717
LAMBDA = 1.0507009873554804934193349852946
LEAKY_RELU_CONST = 0.1
