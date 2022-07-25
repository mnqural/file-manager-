import flask
from flask import Flask,Blueprint, render_template
from flask_login import current_user
import os, time

news = Blueprint('news', __name__, template_folder='templates')

@news.route('/')
def index():
    path = "D:\\coolder"
    filelist = []
    filedates = []
    for root, dirs, files in os.walk(path):
        for file in files:
            # append the file name to the list
            filelist.append(os.path.join(root, file))

    list_of_files = sorted(filelist,
                           key=os.path.getmtime, reverse=True)

    for file_path in list_of_files:
        timestamp_str = time.strftime('%d/%m/%Y :: %H:%M',
                                      time.gmtime(os.path.getmtime(file_path)))
        filedates.append((timestamp_str))
    listfile = [list(x) for x in zip(filedates, list_of_files)]
    return render_template('news/index.html', logged_in=current_user.is_authenticated,
                           itemList = listfile)

