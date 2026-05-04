from groq import Groq
from dotenv import load_dotenv

import os 

load_dotenv()


def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()



def ask_llm(question):

    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    chat_completion = client.chat.completions.create(
        messages=[

            {
                "role": "system",
                "content": read_file(file_path="context.txt"),
            },

            {
                "role": "user",
                "content": question,
            }
        ],

        model="llama-3.3-70b-versatile"
    )

    return chat_completion.choices[0].message.content


if __name__ == "__main__":
    response = ask_llm(question="Quel la complexité minimal pour trier une liste ?")
    print(response)