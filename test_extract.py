import extract 
df = extract.load_raw_data()
print(df.shape)
print(df.columns.tolist())
print(df.dtypes)