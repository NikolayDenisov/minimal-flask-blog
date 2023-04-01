from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from blog.app import models, schemas

app = FastAPI()

engine = create_engine('postgresql://user:password@host:port/db_name')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


models.Base.metadata.create_all(bind=engine)

@templates.env.filter('strftime')
def _jinja2_filter_datetime(date):
    month = int(date.strftime('%m'))
    month_ru_locale = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                       'июля', 'августа', 'сентября', 'октября', 'ноября',
                       'декабря']
    date_locale_format = '%d {} %Y'.format(month_ru_locale[month % 12 - 1])
    return date.strftime(date_locale_format)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(db.create_all)


if __name__ == "__main__":
    app.run()
