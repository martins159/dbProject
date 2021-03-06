from flask import Blueprint, redirect, render_template, flash, request, session, url_for
from flask_login import login_required, logout_user, current_user, login_user
from ..forms import LoginForm, SignupForm
from ..models import db, User
from ..import login_manager
from datetime import datetime
from .. import customFunctions
from .. import dbconn
from flask_login import current_user, login_required
# Blueprint Configuration
auth_bp = Blueprint(
    'auth_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@auth_bp.route('/signup', methods=['GET', 'POST'])
@login_required
def signup():
    """
    User sign-up page.

    GET requests serve sign-up page.
    POST requests validate form & user creation.

    """

    if current_user.isAdmin == False:
        return render_template('notAdmin.html')

    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user is None:
            userConnected = dbconn.user()
            userConnected.connectToDB('userList')
            userConnected.cur.execute('SELECT COUNT(*) FROM flaskloginUsers')
            rows = userConnected.cur.fetchall()
            numberToAdd = 1
            currentEntryNr = rows[0][0] + numberToAdd
            stringsToJoin = ("user", str(currentEntryNr))
            databaseName = "".join(stringsToJoin)
            while userConnected.createDB(databaseName) == False:# try to generate db name with 'user' and generated number
                numberToAdd += 1
                currentEntryNr = rows[0][0] + numberToAdd
                stringsToJoin = ("user", str(currentEntryNr))
                databaseName = "".join(stringsToJoin)
                if numberToAdd > 1000: 
                    print('Error: Too much loops! Could not create database.')
                    break
			#need to activate table to avoid further problems - activised table will be recognised by createDB function as legit, so wont be overwritted
			#simply to activate need to create table in it, after it could be removed, it is done to set active variable to true
			#------------------not longer needed to create and delete test table, cause table for url data will be created for each user as seen below--------------------
			#userConnected.connectToDB(databaseName)
            #userConnected.cur.execute('CREATE TABLE  test(id INTEGER PRIMARY KEY,username STRING UNIQUE NOT NULL)')
            #userConnected.conn.commit()
            #userConnected.cur.execute('DROP TABLE test')
			#----------------------------------------------------------------------------------------------------------------------------------------------------
            userConnected.connectToDB(databaseName)
            userConnected.cur.execute('CREATE TABLE  usrUrl(tableName STRING, webUrl STRING)')
            userConnected.conn.commit()
            userConnected.conn.close()
            user = User(
                username=form.username.data,
                email=form.email.data,
                name=form.name.data,
                #created=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                created=datetime.now(),
		database=databaseName,
		isAdmin = 0,
		isActive = 1,
		language = 'latvian'
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()  # Create new user
            #login_user(user)  # Log in as newly created user
            return redirect(url_for('admin_bp.manageUsers'))
        flash('A user already exists with that email address.')
    #userConnected.conn.close()#close sqlite connection
    return render_template(
        'signup.html',
        title='Create an Account.',
        form=form,
        template='signup-page',
        body="Sign up for a user account."
    )

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log-in page for registered users.

    GET requests serve Log-in page.
    POST requests validate and redirect user to dashboard.
    """
    # Bypass if user is logged in
    if current_user.is_authenticated:
        current_user.lastLogin = datetime.now()#register login time
        db.session.commit()
        if current_user.isAdmin == True: return redirect(url_for('admin_bp.manageUsers'))
        else: return redirect(url_for('records_bp.recordsTab'))

    form = LoginForm()
    # Validate login attempt
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        #check if user account is active or it is admin
        if user.isActive == 0 and user.isAdmin == 0:
            flash('Your account is innactive, please conntact admin')
            return redirect(url_for('auth_bp.login'))
        if user and user.check_password(password=form.password.data):
            login_user(user)
            user.lastLogin = datetime.now()
            db.session.commit()
            next_page = request.args.get('next')
            dbconn.paralelUpdate(user.database)#perform table update
            if user.isAdmin == True: return redirect(url_for('admin_bp.manageUsers'))
            else: return redirect(next_page or url_for('records_bp.recordsTab'))
        flash('Invalid username/password combination')
        return redirect(url_for('auth_bp.login'))
    return render_template(
        'login.html',
        form=form,
        title='Log in.',
        template='login-page',
        body="Log in with your User account."
    )

@auth_bp.route("/logout")
@login_required
def logout():
    """User log-out logic."""
    logout_user()
    return redirect(url_for('auth_bp.login'))
	
@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth_bp.login'))
