from pydantic import BaseModel
from openai import OpenAI
import os

class ProcessAnswer:

  mistake_instructions = "Wrap each mistake in a <b> tag with the class 'mis'. For example, <b class='mis'>mistake</b>. Make sure the wrapped part of the text for the mistake matches the wrapped part of the text for the correction."
  correction_instructions = "Wrap each correction in a <b> tag with the class 'cor'. For example, <b class='cor'>correction</b>. Make sure the wrapped part of the text for the correction matches the wrapped part of the text for the mistake."

  def process(self, question, user_answer, native_language, user_level):
    prompt = f"""
      QUESTION: {question}
      ANSWER: {user_answer}
      This is the question the user was given and the answer the user provided.
      The answer was provided via speech-to-text and may contain errors because of the transcription process. It does not contain any punctuation.
      original_answer_with_punctuation: Your task is to add the necessary punctuation to the user's answer. Do not correct the English in this part. {self.mistake_instructions}
      corrected_answer_with_punctuation: Your task is to correct the English in the answer. Do not change the answer itself. {self.correction_instructions}
      explanations: Your task is to explain the mistakes in the user's answer and correct the user's English. Only correct a maximum of 3 mistakes in the user's answer. Your explanations in English should be clear and not use any language beyond {user_level} level to explain the concepts or the user might not understand. Your explanations in {native_language} should be clear and can use language at any level and must quote the mistake in English and the correction in English within the {native_language}. {native_language} is the user's native language.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    class Mistake(BaseModel):
      mistake: str
      correction: str
      explanation_in_english: str
      explanation_in_user_native_language: str

    class Feedback(BaseModel):
      original_answer_with_punctuation: str
      corrected_answer_with_punctuation: str
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
      "original_answer_with_punctuation": response.original_answer_with_punctuation,
      "corrected_answer_with_punctuation": response.corrected_answer_with_punctuation,
      "explanations": [{"mistake": mistake.mistake, "correction": mistake.correction, "explanation_in_english": mistake.explanation_in_english, "explanation_in_user_native_language": mistake.explanation_in_user_native_language} for mistake in response.explanations]
    }

    tokens_dict = {
      "completion_tokens": completion.usage.completion_tokens,
      "prompt_tokens": completion.usage.prompt_tokens,
      "total_tokens": completion.usage.total_tokens
    }

    return {"response": response_dict, "tokens": tokens_dict}

process_answer = ProcessAnswer()
