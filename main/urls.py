from django.urls import path
from . import views
import pyodbc

urlpatterns = [
    path("", views.loginpage, name="loginpage"),
    path("userpage", views.userpage, name="userpage"),
    path("dbmanagerpage", views.dbmanagerpage, name="dbmanagerpage"),
    path("errorpage", views.errorpage, name="errorpage"),
    path("basicQuestions", views.basicQuestions, name="basicqs"),
    path("specificQuestions", views.specificQuestions, name="specificq"),
    path("matchingQuestions", views.matchingQuestions, name="matchinq"),
]


conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-G6VG2DU\SQLEXPRESS;'
                      'Database=Cmpe321Proje3;'
                      'Trusted_Connection=yes;')

print("Database is connected!")
