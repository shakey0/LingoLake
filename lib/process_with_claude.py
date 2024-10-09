from anthropic import Anthropic, BadRequestError
import os
from dotenv import load_dotenv

load_dotenv()

class ProcessWithClaude:
  
  def get_prompt(self, question, user_answer, native_language, user_level):
    prompt = f"""
      QUESTION: {question}
      ANSWER: {user_answer}
      This is the question the user was given and the answer the user provided.
      The answer was provided via speech-to-text and may contain errors because of the transcription process. It does not contain any punctuation.
      First, add punctuation to the user's answer but do not change any of the words.
      Second, look for any mistakes in the user's answer. Only look for mistakes in the grammar and vocabulary, not in the punctuation. Note the number of mistakes you find.
      If you can't find any mistakes in the grammar or vocabulary, then your job is done.
      If you find any mistakes in the grammar and/or vocabulary in the user's answer, then correct them.
      Explain a maximum of 3 mistakes in the user's answer. If there are more than 3 mistakes, then only explain the biggest 3 mistakes.
      Your explanations in English should be clear and not use any words beyond the {user_level} level of English to explain the concepts.
      Your explanations in {native_language} should be clear and can use language at any level and must quote the mistake in English and
      the correction in English within the {native_language}. {native_language} is the user's native language.
    """
    
    return prompt
  
  def get_tools(self, native_language):
    tools = [
      {
        "name": "get_feedback",
        "description": "Get feedback on a user's English language answer",
        "input_schema": {
          "type": "object",
          "properties": {
            "punctuation_answer": {"type": "string", "description": "The user's answer with punctuation added but no corrections"},
            "number_of_mistakes": {"type": "integer", "description": "The number of mistakes in the user's answer"},
            "corrected_answer": {"type": "string", "description": "The user's answer with punctuation added and corrections made if there were any mistakes"},
            "explanations": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "mistake": {"type": "string"},
                  "correction": {"type": "string"},
                  "explanation_in_english": {"type": "string"},
                  f"explanation_in_{native_language}": {"type": "string"}
                }
              },
              "maxItems": 3,
              "description": "An array of explanations for the mistakes in the user's answer with a maximum of 3 explanations if there were any mistakes"
            }
          },
          "required": ["punctuation_answer", "number_of_mistakes"]
        }
      }
    ]
    
    return tools

  def ProcessAnswer(self, question, user_answer, native_language, user_level):
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    try:
      response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4096,
        messages=[
          {
            "role": "user",
            "content": self.get_prompt(question, user_answer, native_language, user_level)
          }
        ],
        tools=self.get_tools(native_language)
      )
      
      return response
    except BadRequestError as e:
      print(f"Bad request error: {str(e)}")
      return None
    except Exception as e:
      print(f"An error occurred: {str(e)}")
      return None

# test it out
process_with_claude = ProcessWithClaude()
response = process_with_claude.ProcessAnswer("What do you usually do at the weekend?", "I usually go park my friends and play basketball on Sunday I go shopping mall my parents and we go shops to buy clothes we also eat many ice cream together", "Chinese", "A2")

if response:
  print("Response received:", response)
else:
  print("No response received. Please check the error messages above.")
