from groq import Groq
from dotenv import load_dotenv
import json
import os 

load_dotenv()


def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()



def classify_mail(mail):

    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    chat_completion = client.chat.completions.create(
        messages=[

            {
                "role": "system",
                "content": read_file(file_path="context.txt"),
            },

            {
                "role": "user",
                "content": mail,
            }
        ],
        response_format={"type": "json_object"},
        model="llama-3.3-70b-versatile"
    )

    return json.loads(chat_completion.choices[0].message.content)


if __name__ == "__main__":
    example_mail = read_file("./example_mail.txt")
    response = classify_mail(mail=example_mail)
