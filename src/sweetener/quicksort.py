
from .common import swap

def quicksort(arr, low=None, high=None, cmp=lambda a, b: a < b):

    if low is None:
        low = 0
    if high is None:
        high = len(arr)-1

    def partition(low, high):
        i = low-1
        pivot = arr[high]
        for j in range(low, high):
            if cmp(arr[j], pivot):
                i = i+1
                swap(arr, i, j)
        swap(arr, i+1, high)
        return i+1

    if low < high:
        pi = partition(low,high)
        quicksort(arr, low, pi-1, cmp=cmp)
        quicksort(arr, pi+1, high, cmp=cmp)

