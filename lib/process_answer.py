from pydantic import BaseModel
from openai import OpenAI
import os

class ProcessAnswer:

  correction_instructions = "Each correction must be wrapped in double square brackets with the original word(s) from the user's answer followed by the corrected word(s) which will be separated by a double forward slash. For example, [[mistake//correction]]."

  def process(self, question, user_answer, native_language, user_level):
    prompt = f"""
      QUESTION: {question}
      ANSWER: {user_answer}
      This is the question the user was given and the answer the user provided.
      The answer was provided via speech-to-text and may contain errors because of the transcription process. It does not contain any punctuation.
      corrected_answer:
      Your task is to add the necessary punctuation to the user's answer and correct the English. Do not change the answer itself. {self.correction_instructions}
      explanations:
      First of all, look for any mistakes in the user's answer. Only look for mistakes in the grammar and vocabulary, not in the punctuation.
      If you can't find any mistakes in the grammar or vocabulary, then just return an empty array for explanations.
      If you find any mistakes in the grammar and/or vocabulary in the user's answer, then your task is to explain them and correct the user's English.
      Explain a maximum of 3 mistakes in the user's answer. If there are more than 3 mistakes, then only explain the biggest 3 mistakes.
      Your explanations in English should be clear and not use any words beyond the {user_level} level of English to explain the concepts.
      Your explanations in {native_language} should be clear and can use language at any level and must quote the mistake in English and
      the correction in English within the {native_language}. {native_language} is the user's native language.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    class Mistake(BaseModel):
      mistake: str
      correction: str
      explanation_in_english: str
      explanation_in_user_native_language: str

    class Feedback(BaseModel):
      corrected_answer: str
      explanations: list[Mistake]

    completion = client.beta.chat.completions.parse(
      model="gpt-4o-mini-2024-07-18",
      messages=[
        {"role": "system", "content": "You are a helpful English language tutor. Explain the mistakes in the user's answer to the question and correct the user's English."},
        {"role": "user", "content": f"{prompt}"},
      ],
      response_format=Feedback,
      max_tokens=2000,
    )

    response = completion.choices[0].message.parsed

    response_dict = {
      "corrected_answer": response.corrected_answer,
      "explanations": [{"mistake": mistake.mistake, "correction": mistake.correction, "explanation_in_english": mistake.explanation_in_english, "explanation_in_user_native_language": mistake.explanation_in_user_native_language} for mistake in response.explanations]
    }

    tokens_dict = {
      "completion_tokens": completion.usage.completion_tokens,
      "prompt_tokens": completion.usage.prompt_tokens,
      "total_tokens": completion.usage.total_tokens
    }

    return {"response": response_dict, "tokens": tokens_dict}

process_answer = ProcessAnswer()
