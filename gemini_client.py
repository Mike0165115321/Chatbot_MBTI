import google.generativeai as genai
import config

if not config.GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the .env file.")

genai.configure(api_key=config.GEMINI_API_KEY)

generation_config = {
    "temperature": 0.6,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(model_name="gemini-2.5-flash",
                              generation_config=generation_config,
                              safety_settings=safety_settings)


def get_gemini_response(full_prompt: str) -> str:
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred while calling the Gemini API: {e}")
        return "ขออภัย, เกิดข้อผิดพลาดในการประมวลผล โปรดลองอีกครั้ง"






    