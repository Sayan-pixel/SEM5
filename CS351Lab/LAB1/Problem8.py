def square_and_cube_dict(n):
    return {i: [i**2, i**3] for i in range(n + 1)}

n = (int (input ("Enter a number: ")))
print("O/P: ")
print(square_and_cube_dict(n))