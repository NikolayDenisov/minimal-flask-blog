from fastapi.templating import Jinja2Templates
from app import app

templates = Jinja2Templates(directory="templates")


@app.exception_handler(401)
async def unauthorized(request, exc):
    return templates.TemplateResponse("errors/401.html", {"request": request},
                                      status_code=401)


@app.exception_handler(403)
async def forbidden(request, exc):
    return templates.TemplateResponse("errors/403.html", {"request": request},
                                      status_code=403)


@app.exception_handler(404)
async def not_found(request, exc):
    return templates.TemplateResponse("errors/404.html", {"request": request},
                                      status_code=404)


@app.exception_handler(500)
async def internal_server_error(request, exc):
    return templates.TemplateResponse("errors/500.html", {"request": request},
                                      status_code=500)
