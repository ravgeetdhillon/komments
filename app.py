from flask import Flask, jsonify, request, escape, json, Response
from datetime import datetime
import dropbox
import requests
import os


SITE_NAME = '' # for example google.com
DROPBOX_ACCESS_TOKEN = os.environ.get('DROPBOX_ACCESS_TOKEN')
COMMENTS_FILE = '/comments.json'
COMMENTS_BACKUP_FILE = f'/comments_backup_{datetime.now().isoformat()}.json'


def createRequest(url):
    r = requests.get(url)
    data = r.json()
    return data


def addComment(name, content, blog):
    return {
        'name': name,
        'content': content,
        'blog': blog,
        'time': datetime.now().isoformat(),
    }


def getTempLink(dbx):
    link = dbx.files_get_temporary_link(COMMENTS_FILE).link
    return link


def saveAndSendComments(dbx, comments):
    with open('comments_local.json', 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=True, indent=2)

    with open('comments_local.json', 'rb') as f:
        dbx.files_upload(f=f.read(), path=COMMENTS_FILE, mode=dropbox.files.WriteMode.overwrite)
        return True


def sendResponse(data):
    return Response(
        json.dumps(data),
        mimetype="text/json",
        headers = {
            "Access-Control-Allow-Origin":"*"
        }
    )


def allowAccess():
    useragent = request.headers.get('User-Agent')
    referer = request.headers.get('Referer')
    if ( useragent.lower().__contains__('mozilla') or useragent.lower().__contains__('chrome') or useragent.lower().__contains__('safari') ) and referer.lower().__contains__(SITE_NAME):
        return True


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    return sendResponse( [request.headers.get('User-Agent'), request.headers.get('Referer'), 'hello.'] )


@app.route('/get', methods=['POST'])
def get():
    errors = []

    if not( allowAccess() ):
        errors.append('Stricted Access only.')
        return sendResponse(errors)
    
    try:
        dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
        dbx.users_get_current_account()
    except:
        errors.append('No access allowed.')
        return sendResponse(errors)

    if request.method == 'POST':
        if 'blog' in request.form:
            blog = escape( request.form['blog'].strip() )
            try:
                float(blog)
                errors.append('Not a valid blog attribute.')
            except:
                pass
        else:
            errors.append('No blog attribute available.')
        
        if len(errors) != 0:
            return sendResponse(errors)
        
        link = getTempLink(dbx)
        all_comments = createRequest(link)
        final_comments = [comment for comment in all_comments if comment['blog'] == blog]
        final_comments = sorted(final_comments, key=lambda k: (k['time']), reverse=True)

        return sendResponse(final_comments)
    else:
        errors.append('Not a valid request method. Only POST is accepted.')
    
    return sendResponse(errors)


@app.route('/add', methods=['POST'])
def add():
    errors = []

    if not( allowAccess() ):
        errors.append('Stricted Access only.')
        return sendResponse(errors)

    try:
        dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
        dbx.users_get_current_account()
    except:
        errors.append('No access allowed.')
        return sendResponse(errors)

    if request.method == 'POST':
        if 'name' in request.form:
            name = escape( request.form['name'].strip() )
            try:
                float(name)
                errors.append('Not a valid name attribute.')
            except:
                if len(name) > 20:
                    errors.append('Maximum size for name is 20 chars.')
        else:
            errors.append('No name attribute available.')
        
        if 'content' in request.form:
            content = escape( request.form['content'].strip() )
            if len(name) > 500:
                errors.append('Maximum size for a comment is 500 chars.')
        else:
            errors.append('No content attribute available.')

        if 'blog' in request.form:
            blog = escape( request.form['blog'].strip() )
            try:
                float(blog)
                errors.append('Not a valid blog attribute.')
            except:
                pass
        else:
            errors.append('No blog attribute available.')

        if len(errors) != 0:
            return sendResponse(errors)

        link = getTempLink(dbx)
        all_comments = createRequest(link)
        all_comments.append( addComment(name, content, blog) )

        try:
            with open('comments_local.json', 'w', encoding='utf-8') as f:
                json.dump(all_comments, f, ensure_ascii=True, indent=2)

            with open('comments_local.json', 'rb') as f:
                dbx.files_upload(f=f.read(), path=COMMENTS_FILE, mode=dropbox.files.WriteMode.overwrite)
        except:
            errors.append('Comments could\'nt be saved.')
        
        if len(errors) != 0:
            return sendResponse(errors)

        final_comments = [comment for comment in all_comments if comment['blog'] == blog]
        final_comments = sorted(final_comments, key=lambda k: (k['time']), reverse=True)

        return sendResponse(final_comments)
    else:
        errors.append('Not a valid request method. Only POST is accepted.')

    return sendResponse(errors)


if __name__ == '__main__':
    app.run()
