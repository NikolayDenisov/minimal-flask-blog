from flaskext.markdown import Markdown

from app import app, register_blueprints, init_logger, db
from app.base import error_handlers


@app.template_filter('strftime')
def _jinja2_filter_datetime(date):
    month = int(date.strftime('%m'))
    month_ru_locale = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                       'июля', 'августа', 'сентября', 'октября', 'ноября',
                       'декабря']
    date_locale_format = '%d {} %Y'.format(month_ru_locale[month % 12 - 1])
    return date.strftime(date_locale_format)


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
    app.register_error_handler(401, error_handlers.unauthorized)
    app.register_error_handler(403, error_handlers.forbidden)
    app.register_error_handler(404, error_handlers.page_not_found)
    app.register_error_handler(500, error_handlers.internal_server_error)
    app.run(host='0.0.0.0', debug=True)
    db.create_all()
    db.session.commit()
