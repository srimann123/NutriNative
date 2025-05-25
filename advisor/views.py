from django.shortcuts import render
from django.http import HttpResponse
from . import gemini_call
import json
import re


# Create your views here.
def index(request):
	return render(request, 'advisor/index.html')

def demo(request):
    if request.method == "GET":
        return render(request, 'advisor/demo.html', {"user_input": ""})
    elif request.method == "POST":
        conditions = request.POST.get("conditions")
        culture = request.POST.get("culture")
        dish = request.POST.get("dish")

        raw_response = gemini_call.get_nutrition_advice(conditions, culture, dish)

        cleaned_response = re.sub(r"^```json|^```|```$", "", raw_response.strip(), flags=re.MULTILINE).strip()


        try:
            print(cleaned_response)
            parsed_response = json.loads(cleaned_response)
        except json.JSONDecodeError:
            parsed_response = {"error": "Sorry, there was a problem with the AI response formatting."}

        #image = gemini_call.get_gpt_image(dish, parsed_response)
        image = gemini_call.get_google_image(dish)
        print("IMAGE URL", image)
        return render(request, 'advisor/demo.html', 
        {"conditions": conditions,
        "culture": culture,
        "dish": dish,
        "user_input": parsed_response,
        "image": image})