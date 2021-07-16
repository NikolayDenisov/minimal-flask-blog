from flaskext.markdown import Markdown

from app import app, register_blueprints, init_logger, db
from app.base import error_handlers


@app.template_filter('strftime')
def _jinja2_filter_datetime(date):
    month = int(date.strftime('%m'))
    month_ru_locale = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                       'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    date_locale_format = '%d {} %Y'.format(month_ru_locale[month % 12 - 1])
    return date.strftime(date_locale_format)


def error_handlers():
    error_handlers.forbidden
    error_handlers.internal_server_error
    error_handlers.page_not_found
    error_handlers.unauthorized

def create_app():
    init_logger()
    register_blueprints(app)
    Markdown(app)
    app.run(host='0.0.0.0', debug=True)
    db.create_all()
    db.session.commit()

init_logger()
register_blueprints(app)
Markdown(app)
db.create_all()
db.session.commit()


if __name__ == "__main__":
    init_logger()
    register_blueprints(app)
    Markdown(app)
    app.run(host='0.0.0.0', debug=True)
    db.create_all()
    db.session.commit()
    # error_handlers()
