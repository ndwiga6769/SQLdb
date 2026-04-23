import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = {
    "Customer": ["Alice", "Bob", "Charles", "Diana"],
    "Age": [25, 30, 22, 35],
    "Balance": [5000, 12000, 3000, 15000]
}

df = pd.DataFrame(data)
print(df)

# View first rows
print(df.head())

# Data types
print(df.dtypes)

# Summary statistics
print(df.describe())