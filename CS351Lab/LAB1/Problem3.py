import random

def generate_random_numbers(num):
    li = random.sample(range(1, 26), num)
    return li

num = (int (input("Enter how many random numbers you want to generate: ")))
print(generate_random_numbers(num))
