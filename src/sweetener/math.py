
import math

def count_digits(n: int) -> int:
    return 1 \
        if n == 0 or n == 1 \
        else math.ceil(math.log10(n+1))

