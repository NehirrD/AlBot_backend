# Creates the FastAPI app, registers the feature routers and exception handlers, and serves as the application entry point.
from fastapi import FastAPI

app=FastAPI()

@app.get("/")
async def root():
    return {"message": "api"}

"""albot kaldır src içinde olsun hepsi
machine fsm olarak değiştir
context objesi olmalı neler yaptığını yazmalı adam ne yaşadığınnı anlatabilmeli bize yolcu geldiğinde anlatabilmeli. Herkesin ulaşabildiği bir obje olmalı her aşamada - isteğe göre -  oraya veri yazılabilmeli veya veri okunabilmeli. 
chat olayı tamamen agent a ait bir şey

context window görünebilmeli
eventlere bak
authantication kısmı hallededilsin bir kullancıyı kaydedebilellim rol yapısı entegre edilsin rolü görebilelim
jwt  yi sökebilmemiz lazım 
zitadeli sisteme komple entegre et bir çalıştır
admin var user var
"""