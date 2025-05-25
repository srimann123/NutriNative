import pathlib
import textwrap
import google.generativeai as genai
import os

import markdown2

def get_response(user_elements):
	condition, culture, preferences, restrictions = user_elements[0], user_elements[1], user_elements[2], user_elements[3]
	query = f"Suppose an individual has {condition}. Can you first provide them with a general overview of nutritional advice on specifically {culture} food to incorporate/avoid and the reasoning in relation to the condition. Separately, can you also suggest specific {culture} dishes beneficial for their condition. When suggesting dishes, please tailor them to my specific preferences/provide reasoning: {preferences} and  restrictions: {restrictions}"
	response = model.generate_content(query)
	response = markdown2.markdown(response.text)
	return response



GOOGLE_API_KEY = "AIzaSyBgQc9_LtjYQW0LOjKKeblx_o5FEUhYYvQ"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')




