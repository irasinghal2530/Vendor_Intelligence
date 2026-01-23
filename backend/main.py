
# from fastapi import FastAPI, UploadFile, File, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import PlainTextResponse
# from dotenv import load_dotenv

# from backend.analyze import analyze_files
# from backend.llm import chat_reply

# load_dotenv()

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# LAST_CONTEXT = None


# @app.get("/")
# def health():
#     return {"status": "Backend running"}


# @app.post("/analyze")
# async def analyze(files: list[UploadFile] = File(...)):
#     global LAST_CONTEXT
#     result = await analyze_files(files)
#     LAST_CONTEXT = result
#     return result


# @app.post("/chat")
# async def chat(data: dict):
#     question = data.get("question", "")
#     reply = await chat_reply(question, LAST_CONTEXT)
#     return {"reply": reply}


# # 🔴 VERY IMPORTANT: show real errors instead of silent 500s
# @app.exception_handler(Exception)
# async def debug_exception_handler(request: Request, exc: Exception):
#     print("🔥 ERROR:", repr(exc))
#     return PlainTextResponse(str(exc), status_code=500)


from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

from backend.analyze import analyze_files
from backend.llm import chat_reply

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LAST_CONTEXT = None


@app.get("/")
def health():
    return {"status": "Backend running"}


@app.post("/analyze")
async def analyze(files: list[UploadFile] = File(...)):
    global LAST_CONTEXT
    result = await analyze_files(files)
    LAST_CONTEXT = result
    return result


@app.post("/chat")
async def chat(data: dict):
    question = data.get("question", "")

    if not LAST_CONTEXT:
        return {"reply": "No analysis context available yet."}

    context = {
        "facts": LAST_CONTEXT.get("facts", []),
        "analysis": LAST_CONTEXT.get("analysis", {}),
        "vendor_data": LAST_CONTEXT.get("vendor_data", [])
    }

    reply = await chat_reply(question, context)
    return {"reply": reply}


# 🔴 VERY IMPORTANT: show real errors instead of silent 500s
@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    print("🔥 ERROR:", repr(exc))
    return PlainTextResponse(str(exc), status_code=500)

