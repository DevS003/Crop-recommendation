from flask import Flask,request,render_template
import numpy as np
import pandas
import sklearn
import pickle
from flask import request, render_template, current_app

def _parse_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

# importing model
model = pickle.load(open('model.pkl','rb'))
sc = pickle.load(open('standscaler.pkl','rb'))
ms = pickle.load(open('minmaxscaler.pkl','rb'))

# creating flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/predict",methods=['POST'])
def predict():
 

    expected = ['Nitrogen','Phosphorus','Potassium','Temperature','Humidity','Ph','Rainfall']
    parsed = {}
    for name in expected:
        raw = request.form.get(name)
        val = _parse_float(raw)
        if val is None:
            # return the same template with an error message (keeps UI simple)
            return render_template('index.html', result="Please enter valid numeric values for all fields.")
        parsed[name] = val

    # Build feature vector in the order your model expects
    features = [parsed['Nitrogen'], parsed['Phosphorus'], parsed['Potassium'],
                parsed['Temperature'], parsed['Humidity'], parsed['Ph'], parsed['Rainfall']]

  

    errors = []
    # sensible ranges (adjust if needed)
    if not (0 <= parsed['Nitrogen'] <= 200): errors.append("Nitrogen must be between 0 and 200.")
    if not (0 <= parsed['Phosphorus'] <= 200): errors.append("Phosphorus must be between 0 and 200.")
    if not (0 <= parsed['Potassium'] <= 200): errors.append("Potassium must be between 0 and 200.")
    if not (-10 <= parsed['Temperature'] <= 60): errors.append("Temperature must be between -10 and 60 °C.")
    if not (0 <= parsed['Humidity'] <= 100): errors.append("Humidity must be between 0 and 100%.")
    # per your request: treat pH > 10 as invalid
    if not (0 <= parsed['Ph'] <= 10): errors.append("pH must be between 0 and 10 (values >10 are invalid).")
    if not (0 <= parsed['Rainfall'] <= 1000): errors.append("Rainfall must be between 0 and 1000 mm.")

    if errors:
        result = "Invalid input: " + " ".join(errors)
        return render_template('index.html', result=result)

    single_pred = np.array(features, dtype=float).reshape(1, -1)

    try:
      
        final_features = ms.transform(single_pred)
        prediction = model.predict(final_features)
    except Exception as e:
        result = "Error during prediction: {}".format(str(e))
        return render_template('index.html', result=result)

    crop_dict = {1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
                 8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
                 14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean", 18: "Mothbeans",
                 19: "Pigeonpeas", 20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"}
    if prediction[0] in crop_dict:
        crop = crop_dict[prediction[0]]
        result = "{} is the best crop to be cultivated right there".format(crop)
    else:
        result = "Sorry, we could not determine the best crop to be cultivated with the provided data."
    return render_template('index.html',result = result)




# python main
if __name__ == "__main__":
    app.run()