

def ssum(list, sum):
    current = ""
    ssum_h(list, len(list), current, sum)

def ssum_h(list, n, subset, sum):
    if sum == 0:
        print (subset)
        return
      
    if n == 0:
        return
      
    if list[n-1] <= sum:
        ssum_h(list, n-1, subset, sum)
        ssum_h(list, n-1, subset+str(list[n-1])+" ", sum-list[n-1])
    else:
        ssum_h(list, n-1, subset, sum)


lst=[280072,14676,286875,1690,762,1148,4815,7704,15408,14445,8828,8581,54021,50021,18329,7338,890894,45645]
sum=328519
ssum(lst, sum)
