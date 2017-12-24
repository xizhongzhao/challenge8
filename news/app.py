#!/usr/bin/env python3
#
from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/shiyanlou'
db = SQLAlchemy(app)
mdb = MongoClient('127.0.0.1',27017).shiyanlou

class File(db.Model):
    id = db.Column(db.Integer,primary_key=True,index=True)
    title = db.Column(db.String(80),unique=True)
    created_time = db.Column(db.DateTime,nullable=True)
    category_id = db.Column(db.Integer,db.ForeignKey('category.id'))
    category = db.relationship('Category',backref='files')
    content = db.Column(db.Text)
    
    def __init__(self,title,created_time,category_id,content):
        self.title = title
        self.created_time = created_time
        self.category_id = category_id
        self.content = content

    def add_tag(self,tag_name):
        mdb.files.insert_one({"title":self.title,"tag":tag_name})

    def remove_tag(self,tag_name):
        mdb.files.remove({"title":self.title,"tag":tag_name})

    @property
    def tags(self):
        _find_obj_list=mdb.files.find({"title":self.title})
        _tags = []
        for _find_obj in _find_obj_list:
            tags.append(_find_obj['tag'])
        return _tags    

    def __repr__(self):
        return '<File %r>' %self.title

class Category(db.Model):
    id = db.Column(db.Integer,primary_key=True,index=True)
    name = db.Column(db.String(80))
    
    def __init__(self,name):
       self.name = name

    def __repr__(self):
        return '<Category %r>' %self.name 


@app.route('/')
def index():
    db.create_all()
    file_instance_list = File.query.all()
    title_id_list = [(file_instance.title,file_instance.id) for \
            file_instance in file_instance_list ]
    
    return render_template('index.html',title_id_list=title_id_list)




@app.route('/files/<file_id>')
def file(file_id):
    db.create_all()
    file_instance = File.query.filter_by(id=file_id).first_or_404()
    _category_instance = Category.query.filter_by(id=file_instance.category_id).first_or_404()
    file_category = _category_instance.name
    file_dict = { 'created_time':datetime.strftime(file_instance.created_time,'%Y-%m-%d %H:%M:%S'),'category':file_category,'content':file_instance.content }
    return render_template('file.html',file_dict = file_dict)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'),404


if __name__ == '__main__':
    app.run()
