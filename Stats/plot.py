import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from mpldatacursor import datacursor

# Read CSV file with only KM and Dplus columns
df = pd.read_csv('9igf-gac.csv', usecols=['KM', 'Dplus'])

# Remove null or empty values
df.dropna(inplace=True)

# Remove KM values greater than 40
df = df[df['KM'] <= 40]

# Draw chart of points
plt.scatter(df['KM'], df['Dplus'])

# Draw linear regression line
model = LinearRegression().fit(df[['KM']], df[['Dplus']])
plt.plot(df['KM'], model.predict(df[['KM']]), color='red')

# Add tooltip to chart
datacursor(formatter='{label}'.format)

# Make plot interactive
#plt.ion()

# Show chart
plt.show()