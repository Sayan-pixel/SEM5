def generate_squares(n):
    return [i**2 for i in range(n + 1)]
    
n = (int (input("Enter a number: ")))
print(f"Output: {generate_squares(n)}")