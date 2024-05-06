from flask import Flask
import os

app = Flask(__name__, template_folder='../templates', static_folder='../static')

app.secret_key = "key"
