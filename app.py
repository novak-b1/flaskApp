from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from wtforms.fields import EmailField, DateField, DateTimeLocalField, IntegerField
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, text
from flask_wtf import CSRFProtect
import os


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://flask_app_bot:flaskApp@LENOVO/Production ?driver=ODBC Driver 17 for SQL Server'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# need for Intake form specifically to use CSRF (https://stackoverflow.com/questions/47687307/how-do-you-solve-the-error-keyerror-a-secret-key-is-required-to-use-csrf-whe)
SECRET_KEY = os.urandom(32) 
app.config['SECRET_KEY'] = SECRET_KEY
csrf = CSRFProtect(app)

db = SQLAlchemy(app)

# prodEntries Table Model
class prodEntries(db.Model):
    __tablename__ = 'prodEntries'
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Cell = db.Column(db.String, nullable=False)
    Operator = db.Column(db.String, nullable=False)
    Item = db.Column(db.String, nullable=False)
    DateWorked = db.Column(db.Date, nullable=False)
    Line = db.Column(db.String, nullable=False)
    TimeShift = db.Column(db.Float, nullable=False)
    NumberPeople = db.Column(db.Integer, nullable=False)
    NumberHours = db.Column(db.Float, nullable=False)
    NumberProduced = db.Column(db.Float, nullable=False)
    NumberDefects = db.Column(db.Float, nullable=False)
    Notes = db.Column(db.String, nullable=True)

# NewEntry.html Intake Form model
class IntakeForm(FlaskForm):
    cell = StringField('Cell')
    operator = StringField('Operator')
    item = StringField('Item')
    date = DateField('Date')
    line = StringField('Line')
    shift = IntegerField('Shift')
    numberPeople = IntegerField('NumberPeople')
    numberHours = IntegerField('NumberHours')
    numberProduced = IntegerField('NumberProduced')
    numberDefects = IntegerField('NumberDefects')
    notes = TextAreaField('Notes')
    submit = SubmitField('Submit')
                         

@app.route("/")
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 25
    pagination = prodEntries.query.order_by(prodEntries.DateWorked.desc()).paginate(page=page, per_page=per_page, error_out=False)
    data = pagination.items
    return render_template("index.html", rows = data, pagination=pagination)

# get the form to the user
@app.route("/NewEntry", methods = ['GET'])
def NewEntry():
    form = IntakeForm() 
    return render_template("NewEntry.html", form = form)

# get the information from the user and store in a database
@app.route('/submit-NewEntry', methods=['POST'])
def submit_NewEntry():
    form = IntakeForm()
    if form.validate_on_submit():
        new_entry = prodEntries(
            Cell = form.cell.data,
            Item = form.item.data,
            DateWorked = form.date.data,
            Line = form.line.data,
            TimeShift = form.shift.data,
            NumberPeople = form.numberPeople.data,
            NumberHours = form.numberHours.data,
            NumberProduced = form.numberProduced.data,
            NumberDefects = form.numberDefects.data,
            Notes = form.notes.data,
            Operator = form.operator.data
        )
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('thank_you'))
    return render_template('NewEntry.html', form = form)

@app.route("/ViewRecords", methods = ['GET'])
def ViewRecords():
    form = IntakeForm() 
    return render_template("ViewRecords.html", rows = [], form = form)

@app.route("/RetrieveRecords", methods = ['POST'])
def RetrieveRecords():
    form = IntakeForm()
    cell = form.cell.data
    operator = form.operator.data
    item = form.item.data
    date = form.date.data
    needAnd = 0

    query = "SELECT * FROM [Production ].[dbo].[prodEntries]"
    if cell != "":
        cellQuery = f" WHERE Cell = '{cell}'"
        query = ''.join((query, cellQuery))
        needAnd = 1
    
    if operator != "":
        operatorQuery = f"  Operator = '{operator}'"
        if needAnd == 1: 
            operatorQuery = ''.join((" AND", operatorQuery))
        else:
            operatorQuery = ''.join((" WHERE", operatorQuery))
        query = ''.join((query, operatorQuery))
        needAnd = 1
    
    if item != "":
        itemQuery = f" Item = '{item}'"
        if needAnd == 1: 
            itemQuery = ''.join((" AND", itemQuery))
        else:
            itemQuery = ''.join((" WHERE", itemQuery))
        query = ''.join((query, itemQuery))
        needAnd = 1
    
    if date != "" and date != None:
        dateQuery = f" DateWorked = '{date}'"
        if needAnd == 1: 
            dateQuery = ''.join((" AND", dateQuery))
        else:
            dateQuery = ''.join((" WHERE", dateQuery))
        query = ''.join((query, dateQuery))
        needAnd = 1
    

    result = db.session.execute(text(query))
    rows= []
    [rows.append(row) for row in result]

    return render_template("ViewRecords.html", rows = rows, form = form)

@app.route('/thank-you')
def thank_you():
    return '<h1>Thank you for your submission!</h1>'

if __name__ == "__main__":
    app.run(debug=True)