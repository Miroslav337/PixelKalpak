def find_min(list):
    min = list[0]
    for i in range(1, len(list)):
        if min > list[i]:
            min = list[i]
    return min
l = [100, 15, 22, 10, 99, 7]
print(find_min(l))