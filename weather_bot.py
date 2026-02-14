from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import os
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from sklearn.linear_model import LinearRegression
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory="templates")

app = FastAPI()

import pandas as pd # Make sure to run 'pip install pandas' in your terminal first

def initialize_brain():
    # 1. Start with your original "Seed" data
    X = [[30, 29], [35, 33], [25, 24], [20, 19], [15, 14]]
    y = [31, 36, 26, 21, 16]

    # 2. Try to learn from history.txt
    if os.path.exists("history.txt"):
        try:
            history_list = []
            with open("history.txt", "r") as f:
                for line in f:
                    # Logic to extract the numbers from your specific text format
                    # Format: Input: 32.0C | Forecast: 33.0C | Tip: ...
                    today = float(line.split("Input: ")[1].split("C |")[0])
                    forecast = float(line.split("Forecast: ")[1].split("C |")[0])
                    history_list.append([today, forecast])
            
            # If we have at least 5 records, let's use them to train!
            if len(history_list) >= 5:
                df = pd.DataFrame(history_list, columns=['today', 'target'])
                # Using 1-day lag: Today predicts tomorrow
                X = df[['today']].values[:-1]
                y = df['target'].values[1:]
                print("--- SUCCESS: AI Brain updated with real history data! ---")
        except Exception as e:
            print(f"--- NOTICE: Using default brain (History format is new): {e} ---")

    return LinearRegression().fit(X, y)

# This line now creates a "Living" model
model = initialize_brain()

class ForecastInput(BaseModel):
    temp_today: float
    temp_yesterday: float

# 1. Initialize the template engine
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home_ui(request: Request, city: str = "Hyderabad"):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        # FIX: Instead of a white screen, send the error to index.html
        if response.status_code != 200:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "city_name": "Not Found",
                "live_temp": "--", 
                "forecast": "--",
                "error_msg": f"City '{city}' not found. Check the spelling!"
            })
            
        live_temp = data["main"]["temp"]
        prediction = model.predict([[live_temp]]) 
        forecast = round(float(prediction[0]), 2)
        
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "city_name": city,
            "live_temp": live_temp, 
            "forecast": forecast,
            "error_msg": None 
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "city_name": "System Error",
            "live_temp": "Error", 
            "forecast": "Error",
            "error_msg": "Weather service is currently unavailable."
        })
@app.post("/predict")
def predict(data: ForecastInput):
    # FIX: Feed only ONE number
    prediction = model.predict([[data.temp_today]])
    forecast = round(float(prediction[0]), 2)
    # ... rest of your code ...
    
    # 2. Decide on the advice
    tip = "It's hot!" if forecast > 30 else "It's pleasant."

    # 3. THE NEW PART: Write to the diary
    # 'a' means 'Append' (add to the end of the file)
    with open("history.txt", "a") as f:
        f.write(f"Input: {data.temp_today}C | Forecast: {forecast}C | Tip: {tip}\n")

    return {
        "forecasted_temp": forecast,
        "advice": tip
    }
@app.get("/history")
def get_history():
    # This opens the diary and reads all the lines
    try:
        with open("history.txt", "r") as f:
            lines = f.readlines()
        return {"past_predictions": lines}
    except FileNotFoundError:
        return {"error": "No history found yet. Make a prediction first!"}



import matplotlib.pyplot as plt
from fastapi.responses import FileResponse
import os

@app.get("/graph")
def get_graph():
    # 1. Read the data from history.txt
    if not os.path.exists("history.txt"):
        return {"error": "No history file found."}
    
    with open("history.txt", "r") as f:
        lines = f.readlines()

    # 2. Extract the forecast numbers
    # We look for the text after 'Forecast: ' and before 'C |'
    forecasts = []
    for line in lines:
        try:
            temp_part = line.split("Forecast: ")[1].split("C |")[0]
            forecasts.append(float(temp_part))
        except:
            continue

    # 3. Create the Plot
    plt.figure(figsize=(10, 5))
    plt.plot(forecasts, marker='o', color='orange', linestyle='-')
    plt.title("Temperature Forecast Trend")
    plt.xlabel("Prediction Count")
    plt.ylabel("Temperature (°C)")
    plt.grid(True)
    
    # 4. Save the plot as an image
    graph_path = "temp_plot.png"
    plt.savefig(graph_path)
    plt.close() # Close the plot to free memory

    return FileResponse(graph_path)



import requests

API_KEY = "73ab8cb2dd612a8589c9c059713ed76f"  # Paste your key here
CITY = "Hyderabad" # Or your city

@app.get("/current-weather")
def get_real_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url).json()
    
    if response.get("main"):
        temp = response["main"]["temp"]
        return {"city": CITY, "current_temp": temp, "unit": "Celsius"}
    else:
        return {"error": "Could not fetch weather data"}


@app.post("/smart-predict")
def smart_predict():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    weather_data = response.json()
    
    # NEW: Better Error Checking
    if response.status_code == 401:
        return {"error": "Invalid API Key. Please check your key in weather_bot.py"}
    if response.status_code != 200:
        return {"error": f"Weather service error: {weather_data.get('message', 'Unknown')}"}
    
    current_temp = weather_data["main"]["temp"]
    prediction = model.predict([[current_temp]])
    forecast = round(float(prediction[0]), 2)
    
    return {
        "city": CITY,
        "live_temp": current_temp,
        "tomorrow_prediction": forecast,
        "status": "Operational"
    }
