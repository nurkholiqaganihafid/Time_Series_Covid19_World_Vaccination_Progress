# -*- coding: utf-8 -*-
"""Time_Series_Covid19_World_Vaccination_Progress.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CrxtBh5UJGFmPej39biIIRzM50GyUBvP

# **Dataset**

Dataset: [COVID-19 World Vaccination Progress](https://www.kaggle.com/datasets/gpreda/covid-world-vaccination-progress?select=country_vaccinations.csv)

# **Description**

Analyze daily COVID-19 vaccination trends using a time series approach with the LSTM model

# **Data Preparation**

## Library Imports
"""

from google.colab import drive
drive.mount('/content/drive')

pip install dash

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler

import seaborn as sns
import matplotlib.ticker as ticker

import plotly.graph_objects as go
from dash import Dash, callback_context, dcc, html
from dash.dependencies import Input, Output

df = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/All datasets/country_vaccinations.csv')
df

df.info()

df.isnull().sum()

print(df.duplicated().sum())

cols_to_drop = ['iso_code', 'vaccines', 'source_name',
                'source_website', 'total_vaccinations_per_hundred',
                'people_vaccinated_per_hundred',
                'people_fully_vaccinated_per_hundred',
                'daily_vaccinations_per_million']
df = df.drop(cols_to_drop, axis=1)
df.head(3)

"""# **Data Preprocessing**"""

# Memisahkan kolom kategorikal dan numerik
categorical_cols = ['date', 'country']
numeric_df = df.drop(categorical_cols, axis=1)

# Membuat objek imputer dan mengisi missing values dengan metode KNN
imputer = KNNImputer(n_neighbors=5)
numeric_imputed = pd.DataFrame(imputer.fit_transform(numeric_df), columns=numeric_df.columns)

# numeric_imputed = numeric_df.fillna(numeric_df.mean())
# numeric_imputed['daily_vaccinations'] = numeric_df['daily_vaccinations'].fillna(numeric_df['daily_vaccinations'].mean())

df_imputed = pd.concat([df[categorical_cols], numeric_imputed], axis=1)

df_imputed.isnull().sum()

"""Convert 'date' column to datetime format"""

df_imputed['date'] = pd.to_datetime(df_imputed['date'])
df_imputed.set_index('date', inplace=True)

df_imputed.info()

"""There are 40_634 daily_vaccinations in total"""

df_imputed['daily_vaccinations'].nunique()

"""## **Multiple time series plots**"""

# Plot grafik tren jumlah dosis harian vaksinasi COVID-19
plt.figure(figsize=(10, 6))
plt.plot(df_imputed.index, df_imputed['daily_vaccinations'], color='blue')
plt.title('Graphic of Daily COVID-19 Vaccination Trends')
plt.xlabel('Date')
plt.ylabel('Number of Vaccination Daily Doses')
plt.xticks(rotation=45)
plt.show()

sns.set_style('darkgrid')
sns.set(rc={'figure.figsize':(14,8)})

ax = sns.lineplot(data=df_imputed, x=df_imputed.index, y='daily_vaccinations',
                  hue='country', palette='viridis',
                  legend='full', lw=3)

ax.xaxis.set_major_locator(ticker.MultipleLocator(30))
plt.legend(bbox_to_anchor=(1, 1))
plt.ylabel('Number of Vaccination Daily Doses')
plt.xlabel('Date')
plt.xticks(rotation=45)
plt.title('Daily COVID-19 Vaccination Trends')
plt.show()

"""## **Addressing overlapping plots**

Check the country list
"""

list_country = sorted(list(set(df_imputed['country'])))
print(list_country)

pal = list(sns.color_palette(palette='viridis', n_colors=len(list_country)).as_hex())

fig = go.Figure()
for d, p in zip(list_country, pal):
    fig.add_trace(go.Scatter(x=df_imputed.index[df_imputed['country'] == d],
                             y=df_imputed[df_imputed['country'] == d]['daily_vaccinations'],
                             name=d,
                             line_color=p,
                             fill=None))

fig.update_layout(title='Daily COVID-19 Vaccination Trends',
                  xaxis_title='Date',
                  yaxis_title='Number of Vaccination Daily Doses')
fig.show()

"""Membuat agar lebih interaktif dengan menambahkan 'tozeroy' pada atribut fill"""

for d,p in zip(list_country, pal):
    fig.add_trace(go.Scatter(x=df_imputed.index[df_imputed['country'] == d],
                             y=df_imputed[df_imputed['country'] == d]['daily_vaccinations'],
                             name=d,
                             line_color=p,
                             fill='tozeroy')) #tozeroy

fig.update_layout(title='Daily COVID-19 Vaccination Trends',
                  xaxis_title='Date',
                  yaxis_title='Number of Vaccination Daily Doses')

fig.show()

"""Mengatur agar plotnya di-reset ketika daftar list_country dipilih, dengan menggunakan fungsi callback pada library Plotly"""

app = Dash(__name__)

@app.callback(
    Output('graph', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_graph(selected_country):
    fig = go.Figure()

    for d, p in zip(list_country, pal):
        if selected_country is None or d == selected_country:
            fig.add_trace(go.Scatter(x=df_imputed.index[df_imputed['country'] == d],
                                     y=df_imputed[df_imputed['country'] == d]['daily_vaccinations'],
                                     name=d,
                                     line_color=p,
                                     fill='tozeroy'))

    fig.update_layout(title='Daily COVID-19 Vaccination Trends',
                      xaxis_title='Date',
                      yaxis_title='Number of Vaccination Daily Doses')

    return fig

app.layout = html.Div([
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country, 'value': country} for country in list_country],
        placeholder="Select a country",
        multi=False
    ),

    dcc.Graph(id='graph')
])

if __name__ == '__main__':
   app.run_server()

# features = ['total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated']
# X = df_imputed[features]

# y = df_imputed['daily_vaccinations_raw']

dates = df['date'].values
daily = df_imputed['daily_vaccinations'].values

scaler = MinMaxScaler()
scaled_daily = scaler.fit_transform(daily.reshape(-1, 1))

X_train, X_val, y_train, y_val = train_test_split(
    dates[:-int(len(dates)*0.2)], scaled_daily[:-int(len(scaled_daily)*0.2)],
    test_size=0.2,
    shuffle=False,
)

print('Total X_train:', len(X_train),'\nTotal X_test:', len(X_val))

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
  series = tf.expand_dims(series, axis=-1)
  ds = tf.data.Dataset.from_tensor_slices(series)
  ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
  ds = ds.flat_map(lambda w: w.batch(window_size + 1))
  ds = ds.shuffle(shuffle_buffer)
  ds = ds.map(lambda w: (w[:-1], w[-1:]))
  return ds.batch(batch_size).prefetch(1)

"""Menetapkan arsitektur dan pelatihan model"""

train_data = windowed_dataset(y_train.reshape(-1),
                              window_size=60, batch_size=100,
                              shuffle_buffer=1000)
val_data = windowed_dataset(y_val.reshape(-1),
                              window_size=60, batch_size=100,
                              shuffle_buffer=1000)

"""# **Time Series Modeling**

## Build the LSTM model
"""

model = tf.keras.models.Sequential([
    tf.keras.layers.LSTM(120, return_sequences=True),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.LSTM(120),
    tf.keras.layers.Dense(30, activation='relu'),
    tf.keras.layers.Dense(10, activation='relu'),
    tf.keras.layers.Dense(1)
])

optimizer = tf.keras.optimizers.SGD(learning_rate=1e-8, momentum=0.9)

model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=['mae', 'accuracy'])

"""## Callback"""

class CustomCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('mae')<0.10):
      self.model.stop_training = True
      print('\n\nCallback called --- Done training!')
      print(" MAE < 10% ".center(33, '-'), '\n\n')

custom_callback = CustomCallback()

"""## Models Training"""

history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=50,
    verbose=2,
    callbacks=[custom_callback]
)

"""# **Data Visualization**

## MAE (Mean Absolute Error) Graph
"""

plt.figure(figsize=(10, 6))
plt.plot(history.history['mae'], label='Training MAE')
plt.plot(history.history['val_mae'], label='Validation MAE')
plt.title('Model MAE')
plt.xlabel('Epochs')
plt.ylabel('MAE')
plt.legend()
plt.show()

"""## Accuracy Graph"""

plt.figure(figsize=(10, 6))
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

"""## Loss Graph"""

plt.figure(figsize=(10, 6))
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()