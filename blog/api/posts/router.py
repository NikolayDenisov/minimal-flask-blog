import os
from datetime import datetime

from app.dependencies import get_current_user
from fastapi import APIRouter, Depends
from fastapi import Request, status
from fastapi import UploadFile
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Query, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from app import app, db
from app.forms import NewPost
from app.models import Posts

router = APIRouter(prefix="", tags=["base"])
templates = Jinja2Templates(directory="templates")

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


@router.get("/", response_class=HTMLResponse)
@router.get("/page/{page}", response_class=HTMLResponse)
async def home(request: Request, page: int = 1):
    posts = Posts.query.with_entities(
        Posts.id, Posts.title, Posts.content, Posts.created_time, Posts.tags
    ).filter_by().order_by(Posts.created_time.desc()).paginate(
        page, Posts.PER_PAGE, False
    )
    current_page = posts.page
    user = await get_current_user(request)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "posts": posts,
            "max_page": posts.pages,
            "current_page": current_page,
            "user": user,
        },
    )


@router.get("/create_post", response_class=HTMLResponse)
async def show_create_post_form(request: Request):
    """Show the form for creating a new post."""
    user = await get_current_user(request)
    return templates.TemplateResponse(
        "new_post.html",
        {"request": request, "form": NewPost(), "user": user},
    )


@router.post("/create_post")
async def create_post(request: Request, form: NewPost = Depends(NewPost)):
    """Create a post."""
    title = form.title.strip()
    content = form.content
    new_post = Posts(title=title, content=content, user_id=1,
                     created_time=datetime.now())
    db.session.add(new_post)
    db.session.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/edit_post/{post_id}", response_class=HTMLResponse)
async def show_edit_post_form(request: Request, post_id: int):
    """Show the form for editing a post."""
    user = await get_current_user(request)
    post = Posts.query.filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    form = NewPost(title=post.title, content=post.content)
    return templates.TemplateResponse(
        "new_post.html",
        {"request": request, "form": form, "user": user, "post_id": post_id},
    )


@router.post("/edit_post/{post_id}")
async def edit_post(request: Request, post_id: int,
                    form: NewPost = Depends(NewPost)):
    """Edit a post."""
    post = Posts.query.filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    title = form.title.strip()
    content = form.content
    post.title = title
    post.content = content
    db.session.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


def previous_post_id(pid):
    pid = int(pid)
    count = Posts.query.filter_by().count()
    prev_post = None
    while count > 0:
        pid = pid - 1
        if db.session.query(Posts).get(pid) is not None:
            prev_post = db.session.query(Posts).get(pid)
            break
        else:
            count = count - 1
    return prev_post


def next_post_id(pid):
    pid = int(pid)
    count = Posts.query.filter_by().count()
    next_post = None
    while count > 0:
        pid = pid + 1
        if db.session.query(Posts).get(pid) is not None:
            next_post = db.session.query(Posts).get(pid)
            break
        else:
            count = count - 1
    return next_post


@router.route("/post/{post_id}", methods=["GET"])
async def post(request: Request, post_id: int):
    """Show a post."""
    post = Posts.query.filter(Posts.id == post_id).first_or_404()
    next_post = next_post_id(post_id)
    prev_post = previous_post_id(post_id)
    return templates.TemplateResponse(
        "post.html",
        {"request": request, "post": post, "prev_post": prev_post,
         "next_post": next_post},
    )


@router.route("/remove_post/{post_id}", methods=["GET"])
async def remove_post(request: Request, post_id: int):
    """Remove post."""
    post = Posts.query.get_or_404(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()  # Commits all changes
        return RedirectResponse(url="/")


def get_last_posts():
    """Show last posts."""
    posts = (
        Posts.query.with_entities(Posts.id, Posts.title, Posts.created_time)
        .order_by(desc(Posts.created_time))
        .limit(3)
        .all()
    )
    return posts


@router.on_event("startup")
def set_globals():
    templates.env.globals["last_posts"] = get_last_posts()


@router.route("/tag/{tag}", methods=["GET"])
async def posts_by_tag(request: Request, tag: str):
    """Show all posts by tag."""
    posts = (
        Posts.query.with_entities(Posts.id, Posts.title, Posts.content,
                                  Posts.created_time, Posts.tags)
        .filter_by(tags=tag)
        .order_by(Posts.created_time.desc())
        .paginate(page=None, per_page=None, error_out=True, max_per_page=None)
    )
    current_page = posts.page
    max_page = current_page
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "posts": posts, "max_page": max_page,
         "current_page": current_page},
    )


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@router.get('/search', response_class=JSONResponse)
async def search(what_you_need: str = Query(...)):
    print(what_you_need)
    results = []
    posts = db.session.query(Posts.id, Posts.title, Posts.content,
                             Posts.created_time, Posts.tags). \
        order_by(desc(Posts.created_time))
    for i in posts.all():
        results.append(
            {'id': i[0], 'title': i[1], 'plaintext': i[2], 'tags': i[4],
             'primary_tag': i[4],
             'excerpt': i[2][:100],
             'url': f"{request.url_for('static', path='')}/post/{i[0]}"})
    end_result = {'posts': results}
    return end_result


@router.post('/file-upload')
async def file_upload(request: Request, file: UploadFile = File(...)):
    # TODO add post name for file
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")
    contents = await file.read()
    filename = secure_filename(file.filename)
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'wb') as f:
        f.write(contents)
    return {"filename": filename}
