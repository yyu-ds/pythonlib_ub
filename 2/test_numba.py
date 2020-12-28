import numpy as np
import time

@numba.jit
def sum2d_nb(arr):
    M, N = arr.shape
    result = 0.0
    for i in range(M):
        for j in range(N):
            result += arr[i,j]
    return result



def sum2d(arr):
    M, N = arr.shape
    result = 0.0
    for i in range(M):
        for j in range(N):
            result += arr[i,j]
    return result


a = np.random.rand(99999999).reshape(11111111,9)



start_time = time.time()
print(sum2d(a))
print("--- %s seconds ---" % (time.time() - start_time))


start_time = time.time()
print(sum2d_nb(a))
print("--- %s seconds ---" % (time.time() - start_time))
