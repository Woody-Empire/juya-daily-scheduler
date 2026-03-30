import sys
import logging

from dotenv import load_dotenv

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


def main():
    if "--schedule" in sys.argv:
        from apscheduler.schedulers.blocking import BlockingScheduler
        from apscheduler.triggers.cron import CronTrigger

        scheduler = BlockingScheduler()
        # 北京时间 09:30 = UTC 01:30
        scheduler.add_job(
            run,
            CronTrigger(hour=1, minute=30),
            id="daily_briefing",
        )
        logger.info("定时任务已启动，每天北京时间 09:30 执行")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("定时任务已停止")
    else:
        run()


if __name__ == "__main__":
    main()
