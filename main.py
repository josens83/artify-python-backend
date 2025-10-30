# backend-python/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import random
import os
from dotenv import load_dotenv
import openai
from openai import OpenAI
import requests
from io import BytesIO
from pathlib import Path

# 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화 ✨
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기존 Pydantic 모델들...
class AITextRequest(BaseModel):
    brand_name: str
    product: str
    purpose: str = "promotion"
    tone: str = "friendly"
    platform: str = "instagram"

class PredictionRequest(BaseModel):
    text: str
    has_image: bool = False
    hashtags: List[str] = []
    platform: str = "instagram"

# AI 이미지 생성 요청 모델 ✨
class AIImageRequest(BaseModel):
    prompt: str
    style: str = "vivid"  # vivid or natural
    size: str = "1024x1024"  # 1024x1024, 1792x1024, 1024x1792
    quality: str = "standard"  # standard or hd

@app.get("/")
async def root():
    return {
        "message": "Canva Clone AI Backend", 
        "version": "2.0",
        "features": ["AI Text Generation", "Analytics", "Image Generation"]
    }

@app.post("/api/ai/generate-text")
async def generate_text(request: AITextRequest):
    """AI 텍스트 생성 (Mock)"""
    templates = {
        "promotion": [
            f"🎉 {request.brand_name}의 새로운 {request.product}! 지금 바로 만나보세요!",
            f"✨ 특별한 순간을 위한 {request.product} - {request.brand_name}에서만!",
            f"💝 {request.brand_name} {request.product}로 당신의 하루를 특별하게!"
        ],
        "announcement": [
            f"📢 {request.brand_name}에서 {request.product}를 출시합니다!",
            f"🆕 새로운 {request.product}가 찾아왔습니다 - {request.brand_name}",
            f"🎊 {request.brand_name}의 {request.product}, 드디어 공개!"
        ],
        "engagement": [
            f"💬 {request.product}에 대한 여러분의 생각은? - {request.brand_name}",
            f"❤️ {request.brand_name} {request.product}, 어떻게 생각하시나요?",
            f"🙋 {request.product} 좋아하시는 분? - {request.brand_name}"
        ]
    }
    
    hashtags_pool = [
        f"#{request.brand_name.replace(' ', '')}",
        f"#{request.product.replace(' ', '')}",
        "#신제품", "#한정판", "#특별한날", "#데일리", "#추천"
    ]
    
    base_texts = templates.get(request.purpose, templates["promotion"])
    
    copies = []
    for i, text in enumerate(base_texts):
        selected_hashtags = random.sample(hashtags_pool, k=3)
        copies.append({
            "text": text,
            "hashtags": selected_hashtags,
            "score": random.randint(75, 95),
            "reasoning": f"{request.tone} 톤으로 {request.platform}에 최적화"
        })
    
    return {
        "copies": copies,
        "metadata": {
            "brand": request.brand_name,
            "product": request.product,
            "platform": request.platform
        }
    }

@app.get("/api/data/trending")
async def get_trending():
    """트렌딩 데이터 (Mock)"""
    return {
        "trending_topics": [
            {"keyword": "여름시즌", "volume": 125000, "growth_rate": 45},
            {"keyword": "한정판", "volume": 98000, "growth_rate": 32},
            {"keyword": "신메뉴", "volume": 87000, "growth_rate": 28},
            {"keyword": "이벤트", "volume": 76000, "growth_rate": 25},
            {"keyword": "특가", "volume": 65000, "growth_rate": 18}
        ],
        "timestamp": "2025-10-27T12:00:00Z"
    }

@app.post("/api/analytics/predict")
async def predict_performance(request: PredictionRequest):
    """성과 예측 (Mock)"""
    base_engagement = 3.5
    
    # 간단한 계산
    if request.has_image:
        base_engagement += 1.2
    if len(request.hashtags) >= 3:
        base_engagement += 0.8
    if len(request.text) > 50:
        base_engagement += 0.5
        
    followers = 10000
    estimated_reach = int(followers * (base_engagement / 100) * random.uniform(8, 12))
    estimated_likes = int(estimated_reach * random.uniform(0.05, 0.08))
    
    return {
        "predictions": {
            "engagement_rate": {
                "value": round(base_engagement, 1),
                "confidence": 0.85
            },
            "estimated_reach": estimated_reach,
            "estimated_likes": estimated_likes,
            "estimated_comments": int(estimated_likes * 0.1),
            "estimated_shares": int(estimated_likes * 0.05)
        },
        "recommendations": [
            {
                "suggestion": "해시태그를 3-5개 사용하세요",
                "impact": "참여율 +0.8%"
            },
            {
                "suggestion": "이미지를 추가하세요",
                "impact": "참여율 +1.2%"
            },
            {
                "suggestion": "질문형 문장을 포함하세요",
                "impact": "댓글 +25%"
            }
        ]
    }

# ✨ DALL-E 3 이미지 생성 (실제 API 연동)
@app.post("/api/ai/generate-image")
async def generate_image(request: AIImageRequest):
    """
    DALL-E 3를 사용한 AI 이미지 생성
    """
    try:
        # API 키 확인
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="OpenAI API 키가 설정되지 않았습니다."
            )
        
        # 프롬프트 최적화 (영어로 변환 - 더 나은 결과)
        # 실제로는 번역 API 사용하거나 영어 프롬프트 권장
        optimized_prompt = request.prompt
        
        # DALL-E 3 API 호출 ✨
        print(f"🎨 이미지 생성 시작: {optimized_prompt[:50]}...")
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=optimized_prompt,
            size=request.size,
            quality=request.quality,  # "standard" or "hd"
            style=request.style,  # "vivid" or "natural"
            n=1  # DALL-E 3는 1개만 생성 가능
        )
        
        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt
        
        print(f"✅ 이미지 생성 완료: {image_url}")
        
        return {
            "success": True,
            "image_url": image_url,
            "prompt": request.prompt,
            "revised_prompt": revised_prompt,  # DALL-E가 최적화한 프롬프트
            "style": request.style,
            "size": request.size,
            "quality": request.quality,
            "meta": {
                "model": "dall-e-3",
                "cost": 0.04 if request.quality == "standard" else 0.08,
                "currency": "USD"
            }
        }
        
    except openai.APIError as e:
        print(f"❌ OpenAI API 에러: {e}")
        raise HTTPException(status_code=500, detail=f"OpenAI API 에러: {str(e)}")
    
    except openai.RateLimitError as e:
        print(f"❌ Rate Limit 초과: {e}")
        raise HTTPException(status_code=429, detail="API 호출 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
    
    except openai.AuthenticationError as e:
        print(f"❌ 인증 실패: {e}")
        raise HTTPException(status_code=401, detail="OpenAI API 키가 유효하지 않습니다.")
    
    except Exception as e:
        print(f"❌ 예상치 못한 에러: {e}")
        raise HTTPException(status_code=500, detail=f"이미지 생성 실패: {str(e)}")


        # Health check endpoint 추가 (기존 코드 아래에)
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "artify-python-backend"
    }


# ✨ 이미지 다운로드 및 저장 (선택사항)
@app.post("/api/ai/save-generated-image")
async def save_generated_image(image_url: str, filename: str):
    """
    생성된 이미지를 로컬에 저장
    (선택사항 - 영구 저장이 필요한 경우)
    """
    try:
        # 이미지 다운로드
        response = requests.get(image_url)
        response.raise_for_status()
        
        # 저장 경로 설정
        save_dir = Path("generated_images")
        save_dir.mkdir(exist_ok=True)
        
        save_path = save_dir / filename
        
        # 이미지 저장
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        return {
            "success": True,
            "saved_path": str(save_path),
            "filename": filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 저장 실패: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


