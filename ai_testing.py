from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

question = "What do you usually do at the weekend?"

user_answer = "well I usually go park and play my friends sometimes I go cinema and watch movie I also like go to beach and swim sea I love spend time with my friends and family"

mistake_instructions = "Wrap each mistake in a <b> tag with the class 'mis'. For example, <b class='mis'>mistake</b>."
correction_instructions = "Wrap each correction in a <b> tag with the class 'cor'. For example, <b class='cor'>correction</b>."

prompt = f"""
  QUESTION: {question}
  ANSWER: {user_answer}
  This is the question the user was given and the answer the user provided.
  The answer was provided via speech-to-text and may contain errors because of the transcription process. It does not contain any punctuation.
  original_answer_with_punctuation: Your task is to add the necessary punctuation to the user's answer. {mistake_instructions}
  corrected_answer_with_punctuation: Your task is to correct the English in the answer. Do not change the answer itself. {correction_instructions}
  explanations: Your task is to explain the mistakes in the user's answer and correct the user's English. Only correct a maximum of 3 mistakes in the user's answer. Your explanations in English should be clear and don't use any language beyond A2 level. Your explanations in Chinese should be clear and this is the user's native language.
"""

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

class Mistake(BaseModel):
  mistake: str
  correction: str
  explanation_in_english: str
  explanation_in_chinese: str

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

reponse = completion.choices[0].message.parsed

print('\n')

print(reponse)

print('\n')

print(completion)

print('\n')

response_dict = {
  "original_answer_with_punctuation": reponse.original_answer_with_punctuation,
  "corrected_answer_with_punctuation": reponse.corrected_answer_with_punctuation,
  "explanations": reponse.explanations
}

print(response_dict.get('original_answer_with_punctuation'))
print('\n')
print(response_dict.get('corrected_answer_with_punctuation'))
print('\n')

for explanation in response_dict['explanations']:
  print(f"Mistake: {explanation.mistake}")
  print(f"Correction: {explanation.correction}")
  print(f"Explanation in English: {explanation.explanation_in_english}")
  print(f"Explanation in Chinese: {explanation.explanation_in_chinese}")
  print('\n')
