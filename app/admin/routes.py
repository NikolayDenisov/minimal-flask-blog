from app.utils import authenticate_user, create_access_token
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get('/login', response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request,
                form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password",
                            headers={"WWW-Authenticate": "Bearer"})

    access_token = create_access_token(data={"sub": user.email},
                                       expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    response = RedirectResponse(url="/home")
    response.set_cookie(key="access_token", value=f"Bearer {access_token}")

    return response


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="access_token")

    return response
