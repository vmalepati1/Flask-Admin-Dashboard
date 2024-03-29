import os
from urllib.parse import urlparse
import uuid
from dashboard import images
from flask import Markup
from werkzeug.utils import secure_filename
import datetime

def delete_img(mapper, connection, target):
    url = target.img_url
    
    if url is not None:
        a = urlparse(url)
        filename = os.path.basename(a.path)
        filepath = images.path(filename)
        
        try:
            os.remove(filepath)
        except OSError:
            pass
        
def list_thumbnail(view, context, model, name):
    if not model.img_url:
        return ''

    return Markup(
        '<img src="{0}" style="width: 50px;">'.format(images.url(model.img_url))
    )

def imagename_uuid1_gen(obj, file_data):
    _, ext = os.path.splitext(file_data.filename)
    uid = uuid.uuid1()
    return secure_filename('{}{}'.format(uid, ext))

def manage_updates(model, is_created):
    current_timestamp = datetime.datetime.utcnow()
        
    if is_created:
        model.Created_at = current_timestamp

    model.Modified_at = current_timestamp
