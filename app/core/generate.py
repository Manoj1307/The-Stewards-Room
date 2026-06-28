import os
from anthropic import Anthropic
from dotenv import load_dotenv
from app.core.retrieve import Retrieve

load_dotenv()

client = Anthropic()
def generate_answer(ques):
    retrieve_ans = []
    blocks = []
    retrieve_pair = Retrieve(ques)
    for i in range(len(retrieve_pair)):
        retrieve_ans.append(retrieve_pair[i][0])
    for i, chunk in enumerate(retrieve_ans, start=1):
        blocks.append(f"[Source {i}]\n{chunk}")
    context = "\n\n".join(blocks)

    system_prompt="""
        You are an F1 Sporting regulation assisstant.
        answer using the natural F1 terminology fans and broadcasters use, while keeping the meaning strictly faithful to the sources and using precise regulatory terms where they matter.
        Answer only using the provided sources, which are numbered (Source 1, Source 2, etc.) and sent with the question.
        Give direct answer in clear, natural language.Be conversational ans concise like a knowledgable assistant and not formal or robotic
        If source does not contain an answer, answer that you are not sure and not give random answer
        Be very clear and straight forward with the answer
    """
    user_message=f"""
        Source: {context}
        Question: {ques}
    """
    response = client.messages.create(
        model= "claude-haiku-4-5",
        max_tokens= 1024,
        temperature= 0.1,
        system= system_prompt,
        messages =[
            {
                "role":"user",
                "content":user_message
            }
        ]
    )
    answer = response.content[0].text
    print(response.usage)
    return answer


if __name__ == "__main__":
    ans = generate_answer("How many different compunds of tyre should be used in a dry race")
    print(ans)
