import google.generativeai as genai
import json
genai.configure(api_key="AIzaSyCZ8UXzF6YCtaX20_aE_XjIjxt3N2sDVA4")

def classify_ticket_gemini(description: str) -> str:
    
    prompt = (
        "You are an expert IT support assistant. Based on the following ticket description, "
        "determine the most appropriate category that best describes the issue. "
        "Return only the category name as your final answer with no additional text.\n\n"
        f"Ticket Description: {description}"
    )
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")  
        
        response = model.generate_content(prompt)
        
        category = response.text.strip()
        return category
    except Exception as e:
        print("Gemini classification error:", e)
        return "General Inquiry"
    
def get_dynamic_resolution_gemini(ticket_description: str) -> str:
    
    prompt = (
    "You are a seasoned IT support assistant. Based on the following ticket description, "
    "provide a concise and actionable resolution suggestion in one or two sentences. "
    "Return only the resolution text with no extra commentary.\n\n"
    f"Ticket Description: {ticket_description}"
    )
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        resolution = response.text.strip()
        return resolution
    except Exception as e:
        print("Gemini resolution error:", e)
        return "Please consult with a support engineer for further assistance."
def summarize_text_gemini(text: str) -> str:
    
    if len(text.split()) < 20:
        return text

    prompt = (
        "You are an expert summarization assistant. Please generate a concise summary of what user is facing in short word of the following ticket description. "
        "Return only the summary text without any additional commentary.\n\n"
        f"Ticket Description: {text}"
    )
    
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")  
        response = model.generate_content(prompt)
        summary = response.text.strip()
        print("faiz"+summary)
        return summary
    except Exception as e:
        print("Gemini summarization error:", e)
        return text  
    
def summarize_document(document_text: str) -> str:
    """
    Uses Google Gemini's API to generate a concise summary of the provided document text.
    """
    prompt = (
        "You are a summarization expert. Summarize the following document in a clear and concise manner, "
        "capturing its key points and main ideas. Provide the summary in a few sentences.\n\n"
        f"Document:\n{document_text}"
    )

    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")

        response = model.generate_content(prompt)

        summary = response.text.strip()
        return summary

    except Exception as e:
        print("Document summarization error:", e)
        return "Unable to summarize the document at this time."
    
def analyze_sentiment_gemini(ticket_description: str) -> tuple:
    """
    Uses Google Gemini's API to analyze the sentiment of a ticket.
    Returns a tuple of (sentiment_label, priority_score).
    """
    prompt = (
        "You are an expert IT support sentiment analyzer. "
        "Analyze the following ticket description and return a JSON object with two keys: "
        "'sentiment' and 'priority'. The 'sentiment' should be one of 'Very Negative', 'Negative', 'Neutral', or 'Positive'. "
        "The 'priority' should be an integer where 1 represents highest priority (for very negative sentiment) "
        "and 4 represents lowest priority (for positive sentiment). "
        "Return the response in JSON format without any extra text.\n\n"
        f"Ticket: {ticket_description}"
    )

    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")

        response = model.generate_content(prompt)

        result = json.loads(response.text.strip())

        sentiment = result.get("sentiment", "Neutral")
        priority = result.get("priority", 3)

        return sentiment, priority

    except Exception as e:
        print("Gemini sentiment analysis error:", e)
        return "Neutral", 3
