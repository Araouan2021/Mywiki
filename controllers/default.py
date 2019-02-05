def index(): return auth.wiki()

#@auth.requires_login()
def create():
    form = SQLFORM(db.page).process(next=URL('index'))
    return dict(form=form)

def show():
    this_page = db.page(request.args(0, cast=int)) or redirect(URL('index'))
    db.post.page_id.default = this_page.id
    form = SQLFORM(db.post).process() if auth.user else None
    pagecomments = db(db.post.page_id ==  this_page.id).select(orderby=db.post.id)
    return dict(page=this_page, comments=pagecomments, form=form)

#@auth.requires_login()
def edit():
    this_page = db.page(request.args(0, cast=int)) or redirect(URL('index'))
    form = SQLFORM(db.page, this_page).process(
    next = URL('show', args=request.args))
    return dict(form=form)

#@auth.requires_login()
def documents():
    page = db.page(request.args(0, cast=int)) or redirect(URL('index'))
    db.document.page_id.default = page.id
    grid = SQLFORM.grid(db.document.page_id == page.id, args=[page.id])
    return dict(page=page, grid=grid)

def user():
    return dict(form=auth())

def download():
    return response.download(request, db)

def search():
    return dict(form=FORM(INPUT(_id='keyword',
                                _name='keyword',
                                _onkeyup="ajax('callback', ['keyword'], 'target');")),
                target_div=DIV(_id='target'))

def callback():
    query = db.page.title.contains(request.vars.keyword)
    pages = db(query).select(orderby=db.page.title)
    links = [A(p.title, _href=URL('show', args=p.id)) for p in pages]
    return UL(*links)

def news():
    response.generic_patterns = ['.rss']
    pages = db().select(db.page.ALL, orderby=db.page.title)
    return dict(title='mywiki rss feed', 
                link='http://127.0.0.1:8000/mywiki/default/index',
                description='mywiki news',
                created_on=request.now,
                items=[dict(title=row.title,
                            link=URL('show', args=row.id, scheme=True, host=True, extension=False),
                            description=MARKMIN(row.body).xml(),
                            created_on=row.created_on) for row in pages])

service = Service()

@service.xmlrpc
def find_by(keyword):
    return db(db.page.title.contains(keyword)).select().as_list()

def call():
    return service()

def wiki(self, slug=None, env=None, render='markmin',
         manage_permissions=False, force_prefix='',
         restrict_search=False, resolve=True,
         extra=None, menu_groups=None)
