from flask import request, render_template

def pozabljenogeslo():
    return render_template("auth.forgot_password")