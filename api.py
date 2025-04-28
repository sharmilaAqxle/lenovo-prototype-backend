from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dashboard_analysis import LenovoDashboardAnalysis
import uvicorn

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize analyzer
analyzer = LenovoDashboardAnalysis()

@app.get("/api/keyword-gaps")
async def get_keyword_gaps():
    """Get keyword gaps analysis data"""
    df = analyzer.analyze_keyword_gaps()
    return analyzer.plot_keyword_gaps(df)

@app.get("/api/ad-spend-efficiency")
async def get_ad_spend_efficiency():
    """Get ad spend efficiency analysis data"""
    df = analyzer.analyze_ad_spend_efficiency()
    return analyzer.plot_ad_spend_efficiency(df)

@app.get("/api/youtube-trends")
async def get_youtube_trends():
    """Get YouTube trends analysis data"""
    df = analyzer.analyze_youtube_trends()
    return analyzer.plot_youtube_trends(df)

@app.get("/api/competitor-impact")
async def get_competitor_impact():
    """Get competitor impact analysis data"""
    df = analyzer.analyze_competitor_impact()
    return analyzer.plot_competitor_impact(df)

@app.get("/api/opportunity-keywords")
async def get_opportunity_keywords():
    """Get opportunity keywords analysis data"""
    df = analyzer.analyze_opportunity_keywords()
    return analyzer.plot_opportunity_keywords(df)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000) 