from Problem1a import df
from sklearn.model_selection import train_test_split

print("Splitting dataset into X (Training) and Y (Testing) sets")
print("-" * 60)

# X goes from 10 to 90 in steps of 10
# Y is simply 100 - X
for x in range(10, 100, 10):
    y = 100 - x
    
    # train_size takes a fraction between 0.0 and 1.0
    x_fraction = x / 100.0
    
    # Randomly split the dataset
    train_data, test_data = train_test_split(df, train_size=x_fraction, random_state=42)
    
    print(f"Ratio X:Y = {x}:{y}")
    print(f"  -> X (Train) size: {len(train_data)} records")
    print(f"  -> Y (Test) size:  {len(test_data)} records\n")
