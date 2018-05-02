from flask import Flask, render_template, json, request, redirect, url_for
from flask.ext.mysql import MySQL

app = Flask(__name__)

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'samiam5678'
app.config['MYSQL_DATABASE_DB'] = 'TravelAgency'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

curID = 0
source = 'New York City'
dest = 'Boston'
departureFlight = 0
returnFlight = 0
cardNumber = 0

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/home")
def home():
    return render_template('index.html')

@app.route('/showLoc')
def getLoc():
    cursor.execute('SELECT city, state, country FROM location')
    data = cursor.fetchall() # returns list of tuples
    return render_template('loc.html',data = data)

@app.route('/srcdst', methods=['POST'])
def setSourceDest():
    source = request.form['source']
    dest = request.form['dest']
    return render_template('srcdst.html',src=source, dst=dest)

@app.route("/transportation")
def transportation():
    return render_template('transportation.html')

@app.route("/bookTrip")
def book():
    return render_template('bookTrip.html')

@app.route("/payment")
def payment():
    return render_template('payment.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/signUp', methods=['POST'])
def signUp():
    # create user code will be here !!
    # read the posted values from the UI
    _FName = request.form['inputFName']
    _LName = request.form['inputLName']
    _ID = request.form['inputID']
    global curID
    curID = _ID
    _password = request.form['inputPassword']
    _Age = request.form['inputAge']
    query = ('INSERT INTO Passenger (Id, Age, FName, LName, pWord)' 'VALUES (%s,%s,%s,%s,%s)')
    data = (_ID, _Age, _FName, _LName, _password);
    try:
        cursor.execute(query,data)
        conn.commit();
    except:
        return render_template('signup.html', error='Sign Up Error: ID# already in use')

    return render_template('index.html', nameNew=_FName)

@app.route('/signIn', methods=['POST'])
def signIn():
    _ID = request.form['ID']
    _password = request.form['Password']
    query = ('SELECT Passenger.Id FROM Passenger WHERE Passenger.Id = %s AND Passenger.pWord = %s')
    data = (_ID, _password);
    global curID
    curID = _ID

    cursor.execute(query,data)

    ID = cursor.fetchone();
    if ID is not None:
        query = ('SELECT Passenger.FName FROM Passenger WHERE Passenger.Id = %s')
        data = (_ID);
        cursor.execute(query, data)
        Name = cursor.fetchone()[0];
        return render_template('index.html', name=Name)

    return render_template('signup.html', error='Sign In Error: invalid ID or password')

@app.route('/signInFail')
def signInFail():
    return render_template('signupFail.html', error='true')

@app.route('/chooseFlight', methods=['POST'])
def selectTransportation():
    global departureFlight
    departureFlight = request.form['departureFlight']
    global returnFlight
    returnFlight = request.form['returnFlight']

    query = ('SELECT TransportationMethod.Id FROM TransportationMethod WHERE TransportationMethod.Id = %s')
    data = (departureFlight)

    cursor.execute(query, data)

    result = cursor.fetchone()

    if result is None:
        return json.dumps({'response':'bad'})

    query = ('SELECT TransportationMethod.Id FROM TransportationMethod WHERE TransportationMethod.Id = %s')
    data = (returnFlight)

    cursor.execute(query, data)

    result = cursor.fetchone()

    if result is None:
            return json.dumps({'response':'bad'})


    return json.dumps({'response':'ok'})

@app.route('/searchTransportation', methods=['POST'])
def searchTransportation():
    departDate = request.form['departureDate']
    returnDate = request.form['returnDate']

    query = ('SELECT Location.Id FROM Location WHERE Location.City = %s')
    data = (source);
    cursor.execute(query, data)
    sourceID = cursor.fetchone()[0];

    query = ('SELECT Location.Id FROM Location WHERE Location.City = %s')
    data = (dest);
    cursor.execute(query, data)
    destID = cursor.fetchone()[0];

    query = ('SELECT TransportationMethod.Id, TransportationMethod.Cost, Flight.Carrier, Flight.Class FROM TransportationMethod, TravelsTo, Flight WHERE TransportationMethod.Id = TravelsTo.TransportationId AND TravelsTo.SourceId = %s AND TravelsTo.DestinationId = %s AND Flight.Depart = %s AND Flight.Id = TransportationMethod.Id')
    data = (sourceID, destID, departDate)
    cursor.execute(query, data)

    departOptions = cursor.fetchall()

    query = ('SELECT TransportationMethod.Id, TransportationMethod.Cost, Flight.Carrier, Flight.Class FROM TransportationMethod, TravelsTo, Flight WHERE TransportationMethod.Id = TravelsTo.TransportationId AND TravelsTo.SourceId = %s AND TravelsTo.DestinationId = %s AND Flight.Depart = %s AND Flight.Id = TransportationMethod.Id')
    data = (destID, sourceID, returnDate)
    cursor.execute(query, data)

    returnOptions = cursor.fetchall()

    return json.dumps({'departOptions':departOptions, 'returnOptions':returnOptions, 'source':source, 'dest':dest, 'departDate':departDate, 'returnDate':returnDate})

@app.route('/addPaymentOptions', methods=['POST'])
def addPaymentOptions():
    cardNum = request.form['cardNumber']
    cardType = request.form['cardType']
    passengerId = curID
    query = ('INSERT INTO Payment (CardNumber, Type, PassengerId)' 'VALUES (%s,%s,%s)')
    data = (cardNum, cardType, passengerId)

    cursor.execute(query, data)
    conn.commit()

    return viewPaymentOptions()

@app.route('/viewPaymentOptions', methods=['POST'])
def viewPaymentOptions():
    query = ('SELECT Payment.CardNumber, Payment.Type FROM Payment WHERE Payment.PassengerId = %s')
    data = (curID)
    cursor.execute(query, data)

    options = cursor.fetchall()

    return json.dumps({'options':options, 'curID': curID})

@app.route('/choosePaymentMethod', methods=['POST'])
def choosePaymentMethod():
    global cardNumber
    cardNumber = request.form['cardNumberSelect']

    query = ('SELECT Payment.CardNumber FROM Payment WHERE Payment.PassengerId = %s AND Payment.CardNumber = %s')
    data = (curID, cardNumber)
    cursor.execute(query, data)

    result = cursor.fetchone()

    if result is None:
        return json.dumps({'response':'bad', 'curID':curID, 'cardNum':cardNumber})

    return json.dumps({'response':'ok'})

if __name__ == "__main__":
    app.run()
