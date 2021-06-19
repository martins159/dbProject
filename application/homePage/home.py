from flask import Blueprint, render_template
from flask import current_app as app
from ..forms import LoginForm

from flask import request, make_response
from datetime import datetime as dt
from ..models import db, User

from flask import redirect, url_for
from flask_login import current_user, login_required


# Blueprint Configuration
home_bp = Blueprint(
    'home_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@home_bp.route('/home')
def home1():
	#print('--------------isadmin--------->',current_user.isAdmin)
	if current_user.is_authenticated:
		return render_template('home1.html', username = current_user.username, isAdmin = current_user.isAdmin)
	else:
		return render_template('home1.html')

@home_bp.route('/contact')
def contact1():
	if current_user.is_authenticated:
		return render_template('contact1.html', username = current_user.username, isAdmin = current_user.isAdmin)
	else:
		return render_template('contact1.html')


@home_bp.route('/')
@login_required
def home():
    """Homepage."""
    #products = fetch_products(app)
	
	
    return redirect("/home")
	
@home_bp.route('/newUser', methods=['GET'])
def user_records():
    """Create a user via query string parameters."""
    username = request.args.get('user')
    email = request.args.get('email')
    if username and email:
        existing_user = User.query.filter(
            User.username == username or User.email == email
        ).first()
        if existing_user:
            return make_response(f'{username} ({email}) already created!')
        new_user = User(
            username=username,
            email=email,
            created=dt.now(),
            bio="In West Philadelphia born and raised, \
            on the playground is where I spent most of my days",
            admin=False
        )  # Create an instance of the User class
        db.session.add(new_user)  # Adds new User record to database
        db.session.commit()  # Commits all changes
        redirect(url_for('user_records'))
    return render_template(
        'users.html',
        users=User.query.all(),
        title="Show Users"
    )