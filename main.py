from openai import OpenAI
from fastapi import FastAPI, Form, Request, WebSocket
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv

load_dotenv()

openai = OpenAI(
    api_key = os.getenv('OPENAI_API_KEY')
)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

chat_responses = []

@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})


chat_log = [{'role': 'system',
             'content': 'You are highschool math teacher and you are the best this job.'
             }]


@app.websocket("/ws")
async def chat(websocket: WebSocket):

    await websocket.accept()

    while True:
        user_input = await websocket.receive_text()
        chat_log.append({'role': 'user', 'content': user_input})
        chat_responses.append(user_input)

        try:
            response = openai.chat.completions.create(
                model='gpt-4-turbo-2024-04-09',
                messages=chat_log,
                temperature=0.6,
                stream=True
            )

            ai_response = ''

            for chunk in response:      #Chunk is a response object maybe word or sentence
                if chunk.choices[0].delta.content is not None:
                    ai_response += chunk.choices[0].delta.content
                    await websocket.send_text(chunk.choices[0].delta.content)
            chat_responses.append(ai_response)

        except Exception as e:
            await websocket.send_text(f'Error: {str(e)}')
            break


@app.post("/", response_class=HTMLResponse)
async def chat(request: Request, user_input: Annotated[str, Form()]):

    chat_log.append({'role': 'user', 'content': user_input})
    chat_responses.append(user_input)

    response = openai.chat.completions.create(
        model='gpt-4',
        messages=chat_log,
        temperature=0.6
    )

    bot_response = response.choices[0].message.content
    chat_log.append({'role': 'assistant', 'content': bot_response})
    chat_responses.append(bot_response)

    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})









""" KOdun Açıklaması:
2. FastAPI Uygulamasının Oluşturulması:
app = FastAPI() satırı ile bir FastAPI uygulaması oluşturulur. Bu uygulama, daha sonra API endpoint'lerini ve chatbot mantığını barındıracaktır.
3. Chat Endpoint'inin Tanımlanması:
@app.post("/") dekoratörü ile bir POST endpoint'i tanımlanır. Bu endpoint, / adresine POST isteği gönderildiğinde çalışacak fonksiyonu belirtir. Bu fonksiyon, kullanıcının girdiği metni alacak ve chatbot'un cevabını üretecektir.
4. Kullanıcı Girdisinin Alınması:
async def chat(user_input: Annotated[str, Form(...)]) satırı, chat fonksiyonunu tanımlar. Bu fonksiyon, user_input adında bir parametre alır. Annotated ve Form(...) kullanımı, kullanıcının girdisinin bir form verisi olarak alınacağını ve string tipinde olacağını belirtir.
5. Chat Log'unun Güncellenmesi:
chat_log.append({"role": "user", "content": user_input}) satırı, kullanıcının girdisini chat_log adlı listeye ekler. Bu liste, chatbot ile kullanıcı arasındaki konuşmanın geçmişini tutar ve LLM'nin daha anlamlı cevaplar üretmesine yardımcı olur.
6. OpenAI API'sine İstek Gönderme:
response = client.chat.completions.create(...) satırı, OpenAI API'sine bir istek gönderir. Bu istekte:
model="gpt-3.5-turbo": Kullanılacak LLM modeli belirtilir.
messages=chat_log: Chatbot ile kullanıcı arasındaki konuşma geçmişi gönderilir.
temperature=0.6: Cevapların yaratıcılık seviyesi ayarlanır. Daha yüksek değerler daha yaratıcı ancak potansiyel olarak alakasız cevaplar üretirken, daha düşük değerler daha tutarlı ancak daha az yaratıcı cevaplar üretir.
7. Chatbot Cevabının Alınması:
bot_response = response.choices[0].message.content satırı, OpenAI API'sinden gelen cevap içerisinden chatbot'un cevabını ayıklar.
8. Chat Log'unun Güncellenmesi ve Cevabın Döndürülmesi:
chat_log.append({"role": "assistant", "content": bot_response}) satırı, chatbot'un cevabını chat log'una ekler. Son olarak, return bot_response satırı ile chatbot'un cevabı fonksiyondan döndürülür ve kullanıcıya gösterilir.
 """
""" openai=OpenAI(
    api_key='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',
)
 """
