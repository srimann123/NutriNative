from openai import OpenAI
import chromadb
import requests
import os
from dotenv import load_dotenv
load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
embedding_model = "text-embedding-3-small"

#condition_expert = {"Diabetes": "American Diabetes Association (ADA)", "Hypertension": "American Heart Association (AHA)"}

def load_collection(collection_name="guideline_chunks"): # db_path="/Users/srimannramachandruni/BNFOPython/NutriNativeRag/rag_outputs"
    db_path = "/tmp/chroma_db"
    chroma_client = chromadb.PersistentClient(path=db_path)
    return chroma_client.get_or_create_collection(name=collection_name)

def get_query_embedding(query_text):
    response = client.embeddings.create(
        model=embedding_model,
        input=query_text
    )
    return response.data[0].embedding

def query_chunks(query_text, n_results=5):
    query_embedding = get_query_embedding(query_text)
    collection = load_collection()
    retrieved_chunks = collection.query(
    query_embeddings=[query_embedding],
    n_results=n_results,
    include=["documents", "metadatas", "distances"]
    )
    return retrieved_chunks["documents"][0] # This specficially gets you a list of strings (chunks)

def get_nutrition_advice(condition, culture, dish):
   #expert = condition_expert[condition]

   query = f"{condition} {culture} {dish}"
   results = query_chunks(query)
   context_section = "\n\n".join(results)

   prompt = f"""
You are a culturally sensitive medical nutrition assistant.

Below are **evidence-based clinical guidelines**. These are the **only sources you are allowed to use** when answering the user's question:

--- BEGIN CONTEXT ---
{context_section}
--- END CONTEXT ---

The user has provided the following information:
- Medical condition: {condition}
- Cultural background: {culture}
- Dish of interest: {dish}

Your task:
1. Use the context to reason about dietary needs and culturally sensitive modifications.
2. Do not include generalizations or unsupported advice.
3. Respond ONLY with a valid JSON object in the following format — no commentary, no markdown, nothing else:

{{
  "condition_summary": "A specific summary of how the condition affects dietary needs.",
  "modification1": "An evidence-backed modification to the dish for this condition and culture.",
  "modification2": "Another evidence-backed change.",
  "modification3": "A third recommendation."
}}

Do not include explanations. Do not repeat this prompt. Return ONLY the JSON.
"""



   response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a culturally sensitive medical nutrition assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )


   return response.choices[0].message.content

def get_gpt_image(dish, parsed_response): # 35 seconds
   prompt = f"""

	   Generate an image of {dish} with the following changes:

	1. {parsed_response["modification1"]}
	2. {parsed_response["modification2"]}
	3. {parsed_response["modification3"]}
   """

   result = client.images.generate(
    model="gpt-image-1",
    prompt=prompt
   )

   image_base64 = result.data[0].b64_json
   return image_base64

def get_google_image(dish, num_results=1): # 5 seconds
   GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
   GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
   search_url = "https://www.googleapis.com/customsearch/v1"
   params = {
        "q": dish,
        "cx": GOOGLE_CSE_ID,
        "key": GOOGLE_API_KEY,
        "searchType": "image",
        "num": num_results
    }
   response = requests.get(search_url, params=params)
   data = response.json()

   image_urls = [item["link"] for item in data.get("items", [])]
   return image_urls[0]


# 1. Briefly explain how the condition affects diet.
# 2. Analyze how the dish impacts their condition.
# 3. Suggest culturally respectful modifications.
# 4. Give general tips aligned with their culture and condition.


