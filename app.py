from flask import Flask, request, render_template, redirect, url_for, session
import os
from itspylearning import *

app = Flask(__name__)
app.secret_key = os.urandom(24)

async def loginIntoItsLearning(email, password, organization_name) -> UserService:
    try:
        orgs_data = await Itslearning.search_organisations(organization_name)
        if not orgs_data:
            raise ValueError("No organizations found for the provided name")
        
        org = await Itslearning.fetch_organisation(orgs_data[0]["id"])
        return await org.login(email, password)
    except Exception as e:
        raise Exception("Failed to login to itsLearning: " + str(e))


async def get_authenticated_user():
    if 'email' in session and 'password' in session and 'organization_name' in session:
        email = session['email']
        password = session['password']
        organization_name = session['organization_name']
        userService = await loginIntoItsLearning(email, password, organization_name)
        return userService
    else:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_tasks', methods=['GET'])
async def get_tasks():
    try:
        userService = await get_authenticated_user()
        if userService:
            taskList = await userService.fetch_tasks()
            return render_template('tasks.html', taskList=taskList)
        else:
            return redirect(url_for('index'))
    except Exception as e:
        return redirect(url_for('error', message=str(e)))

@app.route('/login', methods=['POST'])
async def login():
    email = request.form.get('email')
    password = request.form.get('password')
    organization_name = request.form.get('organization_name')
    try:
        session['email'] = email
        session['password'] = password
        session['organization_name'] = organization_name
        return redirect(url_for('get_tasks'))
    except ValueError as e:
        return redirect(url_for('error', message=str(e)))

@app.route('/error')
def error():
    message = request.args.get('message', 'An error occurred.')
    return render_template('error.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
