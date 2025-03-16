import google.generativeai as genai


model = genai.GenerativeModel("gemini-2.0-flash")

GOOGLE_API_KEY = "AIzaSyByoT2r9ZQFZvHQXrtjkruRH8w_VVWRNg0"

genai.configure(api_key=GOOGLE_API_KEY)

def prompt(input):
    response = model.generate_content(input)
    print(response.text)
    return response
