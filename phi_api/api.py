from fastapi import FastAPI, Query, Query, HTTPException
from fastapi_limiter import FastAPILimiter
from transformers import AutoModelForCausalLM, AutoTokenizer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
from dotenv import load_dotenv
import logging
from cachetools import LRUCache, cached
import torch
from datetime import datetime

# Variable to hold the start time
start_time = datetime.utcnow()

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
cache = LRUCache(maxsize=100)


class CodeResponse(BaseModel):
    generated_code: str

# Initialize FastAPI app
app = FastAPI()


FastAPILimiter.init("memory://", 50, 1)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize model and tokenizer
device = torch.device('cuda:0')
model = AutoModelForCausalLM.from_pretrained("microsoft/phi-1_5", trust_remote_code=True, torch_dtype="auto").to(device)
tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-1_5", trust_remote_code=True, torch_dtype="auto")


@app.get("/")
async def read_root():
    return {"message": "Welcome to phi-1.5 API. Testing is available at /docs."}


@app.get("/phi/")
async def generate_text(user_input: str, max_length: int = Query(200, ge=10, le=500)):
    # Tokenize the input
    inputs = tokenizer(user_input, return_tensors="pt", return_attention_mask=False).to(device)
    
    outputs = model.generate(**inputs, max_length=max_length)
    
    text = tokenizer.batch_decode(outputs)[0]

    return {"phi_response": text}


@app.get("/phi/codegen/", response_model=CodeResponse)
async def generate_code(prompt: str, max_length: int = Query(200, ge=10, le=500)):
    # Validate the prompt
    if not prompt or len(prompt) < 10:
        raise HTTPException(status_code=400, detail="Invalid prompt")

    try:
        # Wrap the user prompt in code format
        formatted_prompt = f"```python\n{prompt}\n```"

        # Assuming tokenizer and model are pre-loaded and device is defined
        # Tokenize the formatted prompt
        inputs = tokenizer(formatted_prompt, return_tensors="pt", return_attention_mask=False).to(device)

        # Generate output
        outputs = model.generate(**inputs, max_length=max_length)
        
        # Decode the generated code
        generated_code = tokenizer.batch_decode(outputs)[0]

        # Wrap the generated code in Python-formatted triple backticks
        formatted_generated_code = f"```python\n{generated_code}\n```"
        
        return {"generated_code": formatted_generated_code}

    except Exception as e:
        print(f"An error occurred: {e}")  # For debugging
        raise HTTPException(status_code=500, detail="Internal Server Error")


#Small health check for the API. Returns runtime stats
@app.get("/health/")
async def read_health():
    uptime = datetime.utcnow() - start_time
    return {
        "status": "UP",
        "uptime": str(uptime),
        "timestamp": datetime.utcnow().isoformat()
    }