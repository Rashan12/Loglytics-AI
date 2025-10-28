import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import AsyncSessionLocal
from app.services.live_logs.ai_analyzer import LiveLogAIAnalyzer
import logging

logger = logging.getLogger(__name__)

class BackgroundTaskRunner:
    """Runs background tasks for live log analysis"""
    
    def __init__(self):
        self.running = False
    
    async def start(self):
        """Start background tasks"""
        self.running = True
        logger.info("🚀 Starting background tasks for live logs")
        
        # Run analysis loop
        asyncio.create_task(self.analysis_loop())
    
    async def stop(self):
        """Stop background tasks"""
        self.running = False
        logger.info("🛑 Stopping background tasks")
    
    async def analysis_loop(self):
        """Main analysis loop"""
        while self.running:
            try:
                async with AsyncSessionLocal() as db:
                    analyzer = LiveLogAIAnalyzer(db)
                    analyzed_count = await analyzer.analyze_recent_logs(batch_size=20)
                    
                    if analyzed_count > 0:
                        logger.info(f"✅ Analyzed {analyzed_count} logs")
                
            except Exception as e:
                logger.error(f"❌ Error in analysis loop: {e}")
            
            # Wait before next batch (analyze every 10 seconds)
            await asyncio.sleep(10)

# Global instance
background_runner = BackgroundTaskRunner()
