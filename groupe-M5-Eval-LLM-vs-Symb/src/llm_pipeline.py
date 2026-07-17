import time
import os
try:
    from google import genai
except ImportError:
    genai = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class LLMEvaluator:
    def __init__(self):
        if genai is None:
            raise ImportError("Le SDK Google Gemini n'est pas installé. Veuillez exécuter `pip install google-genai` dans votre terminal.")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Veuillez définir GEMINI_API_KEY dans un fichier .env ou dans votre environnement")
        self.client = genai.Client(api_key=api_key)

    def _call_api(self, prompt):
        try:
            time.sleep(4)
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text.strip().lower()
        except Exception as e:
            return f"erreur api: {e}"

    def evaluate_zero_shot(self, context, question):
        prompt = f"Contexte: {context}\nQuestion: {question}\nRéponds uniquement par le lieu exact en un seul mot."
        return self._call_api(prompt)

    def evaluate_few_shot(self, context, question, examples):
        prompt = "Voici quelques exemples :\n"
        for ex in examples:
            prompt += f"Contexte: {ex['context']}\nQuestion: {ex['question']}\nRéponse: {ex['answer']}\n\n"
        prompt += f"À ton tour :\nContexte: {context}\nQuestion: {question}\nRéponds uniquement par le lieu exact en un seul mot.\nRéponse:"
        return self._call_api(prompt)

    def evaluate_chain_of_thought(self, context, question):
        prompt = f"Contexte: {context}\nQuestion: {question}\nRéfléchis étape par étape. À la fin, donne ta réponse sous le format 'Réponse finale : [lieu]'."
        raw_response = self._call_api(prompt)
        if "réponse finale :" in raw_response.lower():
            return raw_response.lower().split("réponse finale :")[-1].strip()
        return raw_response
