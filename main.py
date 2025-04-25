from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import os

app = FastAPI()

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Mount the static files directory
app.mount("/static", StaticFiles(directory=current_dir), name="static")

# Configure CORS to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the index.html file at the root URL
@app.get("/")
async def read_root():
    return FileResponse(os.path.join(current_dir, 'index.html'))

# Example model for request/response
class Message(BaseModel):
    text: str
    user_id: Optional[str] = None

@app.get("/api/keyword-gaps")
async def get_keyword_gaps():
    data = {
        "keywords": ["Business Laptops", "Gaming Laptops", "Workstation", "Convertible"],
        "lenovo_performance": [85, 60, 75, 80],
        "competitor_avg": [70, 75, 65, 70]
    }
    return {
        "question": "Identify keywords where competitors (Dell/HP) dominate but Lenovo underperforms",
        "answer": {
            "title": "Keyword Performance Gaps",
            "subtitle": "Comparison of Lenovo vs Competitor Keyword Performance",
            "insights": [
                "Lenovo shows strong performance in business laptop keywords",
                "Opportunity for improvement in gaming laptop keywords"
            ]
        },
        "chart_name": "grouped_bar_chart",
        "x-axis": {
            "name": "keywords",
            "values": data["keywords"]
        },
        "y-axis": {
            "name": "Performance scores (0-100)",
            "values": {
                "lenovo_performance": data["lenovo_performance"],
                "competitor_avg": data["competitor_avg"]
            }
        }
    }

@app.get("/api/ad-spend-efficiency")
async def get_ad_spend_efficiency():
    return {
        "question": "Compare ad spend efficiency across competitors in critical markets",
        "answer": {
            "title": "Ad Spend Efficiency Analysis",
            "subtitle": "Channel-wise Comparison of Ad Spend",
            "insights": [
                "Social media shows highest ROI with lower spend",
                "Video advertising needs optimization with high spend"
            ]
        },
        "chart_name": "grouped_bar_chart",
        "x-axis": {
            "name": "channels",
            "values": ["Social", "Video", "Display", "Search"]
        },
        "y-axis": {
            "name": "Ad Spend ($)",
            "values": {
                "lenovo_spend": [158.83, 6500000, 120000, 450000],
                "competitor_avg": [120.50, 6700000, 150000, 500000]
            }
        }
    }

@app.get("/api/youtube-trends")
async def get_youtube_trends():
    return {
        "question": "Identify untapped YouTube search trends where Lenovo's content is underrepresented",
        "answer": {
            "title": "YouTube Content Gap Analysis",
            "subtitle": "Search Interest vs Content Coverage",
            "insights": [
                "High search interest in gaming content with low coverage",
                "Business solutions content needs expansion"
            ]
        },
        "chart_name": "grouped_bar_chart",
        "x-axis": {
            "name": "categories",
            "values": ["Laptops", "Gaming", "Business", "Workstation"]
        },
        "y-axis": {
            "name": "Content Coverage Score",
            "values": {
                "lenovo_content": [0, 0, 0, 0],
                "competitor_avg": [1270.5, 850.2, 720.8, 450.3]
            }
        }
    }

@app.get("/api/competitor-impact")
async def get_competitor_impact():
    return {
        "question": "Analyze correlation between competitor ad spend and Lenovo's visibility",
        "answer": {
            "title": "Competitor Impact Analysis",
            "subtitle": "Correlation between Ad Spend and Visibility",
            "insights": [
                "Strong correlation with HP's ad spend in social media",
                "Dell's impact is minimal across channels"
            ]
        },
        "chart_name": "line_chart",
        "x-axis": {
            "name": "time_periods",
            "values": ["0 days", "7 days", "14 days", "30 days"]
        },
        "y-axis": {
            "name": "Correlation Score",
            "values": {
                "social_impact": [0.3, 0.4, 0.2, 0.1],
                "video_impact": [0.2, 0.3, 0.1, 0.0],
                "display_impact": [0.1, 0.2, 0.0, -0.1]
            }
        }
    }

@app.get("/api/opportunity-keywords")
async def get_opportunity_keywords():
    return {
        "question": "Identify low-CPC, high-opportunity keywords",
        "answer": {
            "title": "Keyword Opportunities",
            "subtitle": "High-Value Keywords with Growth Potential",
            "insights": [
                "ThinkPad keywords show highest opportunity score",
                "Gaming laptop keywords show high potential"
            ]
        },
        "chart_name": "scatter_chart",
        "x-axis": {
            "name": "search_volume",
            "values": [10000, 8000, 6000, 4000]
        },
        "y-axis": {
            "name": "Opportunity Score",
            "values": {
                "keywords": ["ThinkPad", "Legion", "Yoga", "IdeaPad"],
                "scores": [85, 75, 65, 55]
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info") 