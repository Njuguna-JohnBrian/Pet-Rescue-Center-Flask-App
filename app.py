"""Flask Application for Paws Rescue Center."""
from flask import Flask, render_template, abort
from forms import SignUpForm, LoginForm, EditPetForm
from flask import session, redirect, url_for

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SECRET_KEY'] = 'dfewfew123213rwdsgert34tgfd1234trgf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///paws.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Pets model
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    age = db.Column(db.String)
    bio = db.Column(db.String)
    posted_by = db.Column(db.String, db.ForeignKey('user.id'))

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    pets = db.relationship('Pet', backref = 'user')
    
db.create_all()
# Create "team" user and add it to session
team = User(full_name = "Pet Rescue Team", email = "team@petrescue.co", password = "adminpass")
db.session.add(team)

# Create all pets
nelly = Pet(name = "Nelly", age = "5 weeks", bio = "I am a tiny kitten rescued by the good people at Paws Rescue Center. I love squeaky toys and cuddles.")
yuki = Pet(name = "Yuki", age = "8 months", bio = "I am a handsome gentle-cat. I like to dress up in bow ties.")
basker = Pet(name = "Basker", age = "1 year", bio = "I love barking. But, I love my friends more.")
mrfurrkins = Pet(name = "Mr. Furrkins", age = "5 years", bio = "Probably napping.")

# Add all pets to the session
db.session.add(nelly)
db.session.add(yuki)
db.session.add(basker)
db.session.add(mrfurrkins) 

# Commit changes in the session
try:
    db.session.commit()
except Exception as e: 
    db.session.rollback()
finally:
    db.session.close()

@app.route("/")
def homepage():
    """View function for Home Page."""
    pets = Pet.query.all()
    return render_template("home.html" ,pets=pets)


@app.route("/about")
def about():
    """View function for About Page."""
    return render_template("about.html")

@app.route("/details/<int:pet_id>", methods=['GET', 'POST'])
def pet_details(pet_id):
    """View Function for showing details of each pet"""
    form = EditPetForm()
    pet = Pet.query.get(pet_id)
    
    if pet is None:
        abort(404, description=f"No Pet Was Found With Id {pet_id}")
    if form.validate_on_submit():
        pet.name = form.name.data
        pet.age = form.age.data 
        pet.bio = form.age.data 
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback(e)
            return render_template('details.html', pet = pet, form = form, message = "A Pet with this name already exists!")
    return render_template("details.html", pet=pet, form=form)

@app.route("/delete/<int:pet_id>", methods=["POST", "GET"])
def delete_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if pet is None: 
        abort(404, description="No Pet was Found with the given ID")
    db.session.delete(pet)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return redirect(url_for('homepage'))


@app.route("/signup", methods=["POST", "GET"])
def signup():
    """View function for Sign Up""" 
    form = SignUpForm()
    if form.validate_on_submit():
        # new_user =  {"id":len(users)+1, "full_name": form.full_name.data, "email":form.email.data, "password":form.password.data}
        # users.append(new_user)
        new_user = User(full_name = form.full_name.data, email = form.email.data, password = form.password.data)
        db.session.add(new_user)
        
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return render_template('signUp.html', form = form, message = 'This User Exists. \n Please consider Loggin In.')
        finally:
            db.session.close()
        return render_template("signUp.html", message="Successfully Signed Up")
    return render_template("signUp.html", form = form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """View Function for logging in"""
    form = LoginForm()
    if form.validate_on_submit():
        
       user = User.query.filter_by(email = form.email.data, password = form.password.data).first()
       if user is None:
           return render_template('login.html', form = form, message="Wrong Credentials Provided")
       else:
           session['user'] = user.id
           return render_template('login.html', message='Successfully Logged In')
    return render_template("login.html", form=form)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('homepage'))
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
