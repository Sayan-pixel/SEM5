def get_frequency(numbers):
    frequency = {}
    for num in numbers:
        if num in frequency:
            frequency[num] += 1
        else:
            frequency[num] = 1
    return frequency

li = list(map(int, input("Enter a list of numbers: ").split()))
res = get_frequency(li)
print("Input:", li)
print("Output:", res)