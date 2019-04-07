import pandas as pd

df = pd.read_csv('test_predict.csv')

series =  pd.DataFrame(df['category'])
clean_data = series.drop_duplicates()
clean_data.to_csv('category.csv', sep=',', encoding='utf-8',index = False)

