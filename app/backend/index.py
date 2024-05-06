from config import app
from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from flask_login import login_user, current_user, logout_user, login_required
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from wtforms.fields import DateField
from cryptography.fernet import Fernet
import hashlib
from flask_script import Manager
from functools import wraps
from datetime import datetime
from itertools import chain
import re
import psycopg2
import secrets
import string
import os

key_length = os.getenv('KEY_LENGTH')
global_key = os.getenv('GLOBAL_KEY')

def getConnCur():
    conn = psycopg2.connect(user=os.getenv('PRIMARY_DB_USER'),
    host =os.getenv('PRIMARY_DB_HOST'),
    database = os.getenv('PRIMARY_DB'),
    port = os.getenv('PRIMARY_DB_PORT'),
    password = os.getenv('PRIMARY_DB_PASSWORD'))
    cur = conn.cursor()
    print("log: Connected to DB")
    return conn, cur

def closeCon(conn):
    if (conn != None):
        conn.commit()
        print("log: Commited changes to DB")
        conn.close()
        print("log: Disconnected from DB")

#def encrypt_(data):
#    # Generate a random key
#    encryption_key = Fernet.generate_key()
#    # Create a Fernet symmetric key cipher
#    cipher = Fernet(encryption_key)
#    encoded_data = data.encode()
#    # Encrypt the data
#    encrypted_data = cipher.encrypt(encoded_data)
#    return encryption_key, encrypted_data

#def decrypt_(encryption_key, encrypted_data):
#    encryption_key = Fernet.generate_key()
#    # Create a Fernet symmetric key cipher
#    cipher = Fernet(encryption_key)
#    decrypted_data = cipher.decrypt(encrypted_data)
#    # Convert bytes back to string
#    decoded_data = decrypted_data.decode()
#    return  decoded_data

def randomKeyGenerator(length):
    random_key=''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(length))
    return random_key

def hash_data(data):
    hashedPassword = hashlib.md5(data.encode())
    return hashedPassword.hexdigest()

def setSession(id, firstname, lastname, username, email):
    session['loggedin'] = True
    session['id'] = id
    session['firstname'] = firstname
    session['lastname'] = lastname
    session['username'] = username
    session['email'] = email

def clearSession():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('firstname', None)
    session.pop('lastname', None)
    session.pop('username', None)
    session.pop('email', None)
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    clearSession()
    return redirect(url_for('index'))


@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    try:
        if session['loggedin']:
            print("From Dashboard logged in user")
            if request.method == 'POST':
                form_id = request.form.get('form_id')
                if form_id == 'vaultentry':
                    masterkey = request.form.get("masterkey")
                    print("Vault Master Key:", masterkey)
                    conn, cur=getConnCur()
                    cur.execute('select convert_from(decrypt(CAST (encrypted_masterkey AS bytea), CAST ((convert_from(decrypt(CAST (encryption_key AS bytea), CAST (\'{}\' AS bytea), \'aes\'), \'SQL_ASCII\')) AS bytea), \'aes\'), \'SQL_ASCII\') from user_masterkey where user_id={};'.format(global_key,session['id']))
                    rows = cur.fetchone()
                    print(rows)  
                    retrieved_masterkey = rows[0]
                    print(retrieved_masterkey)
                    closeCon(conn)
                    if masterkey==retrieved_masterkey:
                        return redirect(url_for('vault'))
                    else: 
                        flash("Incorrect Master Key! Please try again.")
                        return redirect(url_for('dashboard'))
                
                elif form_id=='generatepassword':
                    gpappname=request.form.get('applicationname')
                    gpusername=request.form.get('usernamegp')
                    gpassword=request.form.get('gpasswordname')
                    conn,cur=getConnCur()
                    #cur.execute('INSERT INTO vault (user_id, vault_account_name, vault_user_name, vault_encrypted_passwords) VALUES  ({}, \'{}\', \'{}\', \'{}\');'.format(session['id'],gpappname, gpusername, gpassword))
                    
                    cur.execute('select convert_from(decrypt(CAST (encryption_key AS bytea), CAST (\'{}\' AS bytea), \'aes\'), \'SQL_ASCII\') from user_masterkey where user_id={};'.format(global_key,session['id']))
                    encrption=cur.fetchone()
                    print(encrption)  
                    retrieved_encryption_key = encrption[0]
                    print(retrieved_encryption_key)
                    
                    cur.execute('INSERT INTO vault (user_id, vault_account_name, vault_user_name, vault_encrypted_passwords) VALUES  ({}, \'{}\', \'{}\', encrypt(\'{}\',\'{}\',\'aes\'));'.format(session['id'],gpappname, gpusername, gpassword, retrieved_encryption_key))
                    closeCon(conn)
                    flash("Password Added To Vault")
                    return redirect(url_for('dashboard'))
                
                elif form_id=='changepassword':
                    current_password=request.form.get('currentpassword')
                    new_password=request.form.get('newpassword')
                    current_password_hashed=hash_data(current_password)
                    conn,cur=getConnCur()
                    cur.execute('SELECT id, hashed_password FROM user_credentials WHERE user_id =\'{}\''.format(session['id']))
                    cred = cur.fetchone()
                    credential=cred[1]
                    credential_id =cred[0]
                    if credential==current_password_hashed:   
                        new_password_hashed=hash_data(new_password)
                        cur.execute('UPDATE user_credentials SET hashed_password=\'{}\' WHERE id={} AND user_id={}'.format(new_password_hashed, credential_id, session['id']))
                        closeCon(conn)
                        flash("Password Updated")
                        return redirect(url_for('dashboard'))
                    else:
                        closeCon(conn)
                        flash("Current password is incorrect")
                        return redirect(url_for('dashboard'))
                    
                elif form_id=="changeusername":
                    current_username=request.form.get('currentusername')
                    new_username=request.form.get('manageusername')
                    if current_username==session['username']:
                        conn,cur=getConnCur()
                        cur.execute('UPDATE users SET username=\'{}\' WHERE id={}'.format(new_username, session['id']))
                        closeCon(conn)
                        flash("Username Updated")
                        return redirect(url_for('dashboard'))
                    else :
                        flash("Username does not match")
                        return redirect(url_for('dashboard'))

            else:
                return render_template("dashBoard.html")
    except:
        # User is not logged in
        print("Not Logged In")
        flash("You must be logged in to  view the dashboard.")
        return redirect(url_for('login'))
    

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        conn, cur=getConnCur()
        cur.execute('SELECT * FROM users WHERE username =\'{}\''.format(username))
        user = cur.fetchall()
        if user:
            user_id= user[0][0]
            hashedPassword=hash_data(password)
            cur.execute('SELECT id, hashed_password FROM user_credentials WHERE user_id =\'{}\''.format(user_id))
            credential = cur.fetchone()[1]
            print("User in DB to LOGIN -->", user)
            closeCon(conn)
            if credential==hashedPassword:
                setSession(int(user[0][0]),user[0][1], user[0][2], user[0][3], user[0][5])
                print("Log: Session INFO -->",session['loggedin'],session['id'], session['username'] )
                #msg="Hello! {} Logged in Successfully with Session: {}, Session Id: {}, Session Username: {}".format(session['username'], session['loggedin'],session['id'], session['username'] ) 
                print(msg)
                #flash(msg)
                return redirect(url_for('dashboard'))
              
            else:
                msg = 'Incorrect password !'
                print(msg)
                flash(msg)
                return render_template('loginPage.html')
        
        else:
            msg = 'No User Found, Please check the username or register !'
            print(msg)
            flash(msg)
            return render_template('loginPage.html')
    
    else:
        return render_template('loginPage.html')
    

@app.route('/register', methods =['GET','POST'])
def register():
    msg = ''
    if request.method == 'POST':
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        masterkey = request.form.get("masterkey")
        print("log:formInput:",(firstname, lastname, username, password, email, masterkey))
        conn, cur = getConnCur()
        
        #User check, to ensure new user

        print("log: Checking User in system")
        cur.execute('SELECT username, email FROM users WHERE username=\'{}\' AND email=\'{}\';'.format(username, email))
        usercheck=cur.fetchone()
        print("usercheck",usercheck)
        if usercheck:
            msg = "User already exists. Please login."
            print("log:", msg)
            closeCon(conn)
            flash(msg)
            return redirect(url_for('login'))  # If the user already exists
        
        else: #user does not exist
            msg="New User"
            print(msg)
            cur.execute('SELECT username from users')
            taken_usernames=cur.fetchall()
            flat_taken_usernames = list(chain.from_iterable(taken_usernames))
            if username in flat_taken_usernames:
                print("\nIN IF",taken_usernames)
                msg="Username is taken, Please use a different username"
                flash(msg)
                return redirect(url_for('register'))
            else:
                hashedPassword = hash_data(password)
                #encryption_key, encrypted_masterkey = encrypt_(masterkey)
                encryption_key = randomKeyGenerator(int(key_length))

                print("Inserting to DB")
                #cur.execute('INSERT INTO accounts (firstname, lastname, username, password, email, masterkey) VALUES (\'{}\', \'{}\', \'{}\',\'{}\', \'{}\', {})'.format(firstname, lastname, username, password, email, masterkey ))
                cur.execute('INSERT INTO users (firstname, lastname, username, email, creation_timestamp) VALUES (\'{}\', \'{}\', \'{}\',\'{}\', NOW())'.format(firstname, lastname, username, email ))   
                cur.execute('SELECT id FROM users WHERE username=\'{}\';' .format(username))
                user_id=cur.fetchone()[0]
                cur.execute('INSERT INTO user_credentials (user_id, hashed_password) VALUES  ({}, \'{}\');'.format(user_id, hashedPassword))
                
                cur.execute('INSERT INTO user_masterkey (user_id, encryption_key, encrypted_masterkey) VALUES  ({}, encrypt(\'{}\',\'{}\',\'aes\'), encrypt(\'{}\',\'{}\',\'aes\'));'.format(user_id, encryption_key, global_key, masterkey, encryption_key))
                #cur.execute('INSERT INTO user_masterkey (user_id, encrypted_masterkey) VALUES  ({}, \'{}\');'.format(user_id, masterkey))
                
                msg="Successfull Registration"
                print("db_log:", msg)
                closeCon(conn)
                flash(msg)
                return redirect(url_for('login'))
        
    
    return render_template('registrationPage.html')


@app.route("/vault", methods =['GET','POST'])    
def vault():
    try:
        if session['loggedin']:
            print("From Vault logged in user")
            
            conn,cur=getConnCur()
            cur.execute('select convert_from(decrypt(CAST (encryption_key AS bytea), CAST (\'{}\' AS bytea), \'aes\'), \'SQL_ASCII\') from user_masterkey where user_id={};'.format(global_key,session['id']))
            encrption=cur.fetchone()
            print(encrption)  
            retrieved_encryption_key = encrption[0]
            print(retrieved_encryption_key)
            closeCon(conn)
            
            if request.method == 'POST':
                form_id = request.form.get('form_id')
                if form_id=='addnewdata': 
                    newapplicationname=request.form.get('newapplicationname')
                    newusername=request.form.get('newusername')
                    newpassword=request.form.get('newpassword')                
                    conn,cur=getConnCur()
                    cur.execute('INSERT INTO vault (user_id, vault_account_name, vault_user_name, vault_encrypted_passwords) VALUES  ({}, \'{}\', \'{}\', encrypt(\'{}\',\'{}\',\'aes\'));'.format(session['id'],newapplicationname, newusername, newpassword, retrieved_encryption_key))
                    closeCon(conn)
                    flash("Data Added Successfully")
                    return redirect(url_for('vault'))
                
                elif form_id=="editdata":
                    applicationnameedit=request.form.get('applicationnameedit')
                    usernameedit=request.form.get('usernameedit')
                    passwordedit=request.form.get('passwordedit')
                    vault_id=request.form.get('update_vault_id')
                    print("vault_update", vault_id)
                    conn,cur=getConnCur()
                    cur.execute('UPDATE vault SET vault_account_name=\'{}\', vault_user_name=\'{}\', vault_encrypted_passwords=encrypt(\'{}\',\'{}\',\'aes\') where id ={} and user_id={};'.format(applicationnameedit, usernameedit, passwordedit, retrieved_encryption_key, vault_id, session['id']))
                    closeCon(conn)
                    flash("Data Updated Successfully!")
                    return redirect(url_for('vault'))
                
                elif form_id=="deletedata":
                    vault_id=request.form.get('delete_vault_id')
                    print("vault",vault_id)
                    conn,cur=getConnCur()
                    cur.execute('DELETE FROM vault WHERE id={} AND user_id={};'.format(vault_id, session['id']))
                    closeCon(conn)
                    flash("Data Deleted Successfully!")
                    return redirect(url_for('vault'))
                

            #cur.execute('select * from vault where user_id={}'.format(session['id']))
            conn,cur=getConnCur()
            cur.execute('select id, user_id, vault_account_name, vault_user_name, convert_from(decrypt(CAST (vault_encrypted_passwords AS bytea), CAST (%s AS bytea), \'aes\'), \'SQL_ASCII\') from vault where user_id=%s',( retrieved_encryption_key, session['id']))
            vault_data=cur.fetchall()  
            closeCon(conn)
    
            return render_template("vault.html",vaut_display=vault_data)
        
    except:
    # User is not logged in
        print("Not Logged In")
        flash("You must be logged in to  view the vault.")
        return redirect(url_for('login'))