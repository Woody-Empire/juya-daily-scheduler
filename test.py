import logging
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from graph import ai_daily_app

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run():
    ai_daily_app.invoke({})
    logger.info("流水线执行完成")


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(
        run,
        CronTrigger(hour=17, minute=56),
        id="test_daily_briefing",
    )
    logger.info("定时任务已启动，将在 15:00 执行")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("定时任务已停止")
