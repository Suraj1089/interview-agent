from fastapi import FastAPI


app = FastAPI(
    title="Interview Agent",
    docs_url="/v1/docs",
    redoc_url="/v1/redoc"
)

@app.get('/')
def home():
    return {"data": "agent"}


@app.post('/start')
def start():
    pass


@app.post('/process')
def process():
    pass


@app.post('/evaluate')
def evaluate():
    pass


# if __name__ == '__main__':
#     import uvicorn
#     uvicorn.run(app, reload=True)
