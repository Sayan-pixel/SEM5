class CustomListOperator:
    def __init__(self, values):
        self.values = values
    
    def apply(self, func):
        try:
            return [func(x) for x in self.values]
        except Exception as e:
            raise Exception(f"Failed to apply function: {e}")

if __name__ == "__main__":
    obj = CustomListOperator([1, 2, 3])
    print(f"Original list: {obj.values}")
    
    # Lambda function
    result = obj.apply(lambda x: x * 2)
    print(f"After applying lambda x: x * 2 -> {result}")
    
    # exception
    try:
        zero = 0
        obj.apply(lambda x: x / zero)
    except Exception as e:
        print(f"Caught exception: {e}")
