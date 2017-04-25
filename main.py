# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring, invalid-name, import-error

import os
import jinja2
import webapp2

from google.appengine.api import images
from google.appengine.ext import ndb

from model import *
import time

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class ImageHandler(webapp2.RequestHandler):
    def get(self):
        professor_key = ndb.Key(urlsafe=self.request.get('img_id'))
        professor = professor_key.get()
        if professor.foto:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(professor.foto)
        else:
            self.response.out.write('No image')

class MainHandler(Handler):
    def get(self):
        self.render("index.html")

class ProfessorHandler(Handler):
    def get(self):
        professores = Professor.query()

        self.render("professor.html", professores=professores)

    def post(self):
        nome   = self.request.get("nome")
        area   = self.request.get("area")
        perfil = self.request.get("perfil")
        email  = self.request.get("email")
        foto   = self.request.get("img")

        professor = Professor(nome=nome,area=area, perfil=perfil, email=email,foto=foto)
        professor.put()

        time.sleep(.1)
        self.redirect('/professor')

class CursoHandler(Handler):
    def get(self):
        cursos = Curso.query()
        self.render("curso.html", cursos=cursos)

    def post(self):
        nome      = self.request.get('nome')
        periodos  = int(self.request.get('periodos'))
        semestral = self.request.get('semestral')

        curso = Curso(nome=nome, periodos=periodos, semestral=semestral)
        curso.put()

        time.sleep(.1)
        self.redirect('/curso')

class DisciplinaHandler(Handler):
    def get(self):
        key_curso  = ndb.Key(urlsafe=self.request.get('key'))
        disciplina = Disciplina.query(Disciplina.curso == key_curso)
        self.render("disciplina.html", disciplina=disciplina, key_curso=key_curso)
    
    def post(self):
        key_curso  = ndb.Key(urlsafe=self.request.get('key'))
        nome       = self.request.get("nome")
        periodos   = int(self.request.get("periodos"))
        curso      = key_curso
        disciplina = Disciplina(nome=nome, periodos=periodos, curso=curso)
        disciplina.put()

        time.sleep(.1)
        self.redirect('/disciplina?key='+key_curso.urlsafe())

class DeleteProfessorHandler(Handler):
    def get(self):
        key_professor  = ndb.Key(urlsafe=self.request.get('key'))
        key_professor.delete()
        time.sleep(.1)
        self.redirect('/professor')

class DeleteCursoHandler(Handler):
    def get(self):
        key_curso  = ndb.Key(urlsafe=self.request.get('key'))
        key_curso.delete()
        time.sleep(.1)
        self.redirect('/curso')

class DeleteDisciplinaHandler(Handler):
    def get(self):
        key_disciplina = ndb.Key(urlsafe=self.request.get('key'))
        key_curso  = ndb.Key(urlsafe=self.request.get('key_curso'))
        key_disciplina.delete()
        time.sleep(.1)
        self.redirect('/disciplina?key='+key_curso.urlsafe())

class EditProfessorHandler(Handler):
    def post(self):
        key_professor    = ndb.Key(urlsafe=self.request.get('key'))
        professor        = key_professor.get()
        professor.nome   = self.request.get("nome")
        professor.area   = self.request.get("area")
        professor.perfil = self.request.get("perfil")
        professor.email  = self.request.get("email")
        professor.foto   = key_professor.get().foto
        
        professor.put()

        time.sleep(.1)
        self.redirect('/professor')

class EditCursoHandler(Handler):
    def post(self):
        key_curso       = ndb.Key(urlsafe=self.request.get('key'))
        curso           = key_curso.get()
        curso.nome      = self.request.get('nome')
        curso.periodos  = int(self.request.get('periodos'))
        curso.semestral = self.request.get('semestral')
        curso.put()

        time.sleep(.1)
        self.redirect('/curso')

class EditDisciplinaHandler(Handler):
    def post(self):
        key_disciplina = ndb.Key(urlsafe=self.request.get('key'))
        key_curso = ndb.Key(urlsafe=self.request.get('key_curso'))
        disciplina = key_disciplina.get()
        disciplina.nome = self.request.get('nome')
        disciplina.periodos = int(self.request.get('periodos'))
        disciplina.curso = key_curso
        
        time.sleep(.1)
        self.redirect('/disciplina?key='+key_curso.urlsafe())

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/professor', ProfessorHandler),
    ('/curso', CursoHandler),
    ('/disciplina', DisciplinaHandler),
    ('/deleteprofessor', DeleteProfessorHandler),
    ('/deletecurso', DeleteCursoHandler),
    ('/deletedisciplina', DeleteDisciplinaHandler), 
    ('/editprofessor', EditProfessorHandler),
    ('/editcurso', EditCursoHandler),
    ('/editdisciplina', EditDisciplinaHandler),
    ('/img', ImageHandler)
], debug=True)
