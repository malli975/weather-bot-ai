# 🌦️ AI Weather Bot - Hyderabad

A Full-Stack AI application that provides live weather updates and uses Machine Learning to predict tomorrow's temperature.

## 🚀 Features
* **Live Data**: Fetches real-time weather from OpenWeatherMap API.
* **AI Predictions**: Uses a Scikit-Learn Linear Regression model to forecast temperatures.
* **Self-Learning**: The model automatically re-trains itself using data stored in `history.txt`.
* **Interactive UI**: A clean, responsive dashboard built with Bootstrap and FastAPI.
* **Search**: Check weather and predictions for any city in the world.

## 🛠️ Tech Stack
* **Backend**: Python, FastAPI
* **Machine Learning**: Scikit-Learn, NumPy, Pandas
* **Frontend**: HTML5, Bootstrap 5, Jinja2 Templates
* **Deployment**: Render

## 📈 How it Works
The app follows a complete data pipeline:
1. **Fetch**: Gets current data (Temp, Humidity, Wind) from a live API.
2. **Predict**: Feeds data into the trained model to get a forecast.
3. **Log**: Saves every interaction to a history file.
4. **Learn**: Re-optimizes the model coefficients upon server restart based on history.
