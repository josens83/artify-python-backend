from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from openai import OpenAI
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Artify Python Backend")

# CORS 설정 - Vercel 도메인 명시적으로 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://artify-ruddy.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI 클라이언트
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ImagePrompt(BaseModel):
    prompt: str
    size: str = "1024x1024"
    quality: str = "standard"

@app.get("/")
async def root():
    return {
        "message": "Artify Python Backend - AI Image Generation",
        "status": "running",
        "endpoints": ["/health", "/api/generate-image"]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "artify-python-backend",
        "ai": "OpenAI DALL-E 3"
    }

@app.post("/api/generate-image")
async def generate_image(prompt: ImagePrompt):
    try:
        # OpenAI DALL-E 3로 이미지 생성
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt.prompt,
            size=prompt.size,
            quality=prompt.quality,
            n=1
        )
        
        image_url = response.data[0].url
        
        # 이미지 URL을 Base64로 변환
        async with httpx.AsyncClient() as http_client:
            image_response = await http_client.get(image_url)
            image_data = image_response.content
            
            import base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
        return {
            "success": True,
            "imageUrl": image_url,
            "imageData": f"data:image/png;base64,{base64_image}",
            "prompt": prompt.prompt
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)