import flask
from init import app, db
from models import Vendors

@app.route('/')
def homepage():
    return flask.render_template('home.html')

@app.route('/form')
def formpage():
    return flask.render_template('form.html')

@app.route('/edit')
def editpage():
    loggers = sorted(Vendors.query.all())
    return flask.render_template('edit.html', loggers=loggers)

@app.route('/submit', methods = ['POST'])
def submission():
    name = verify(flask.request.form['name'])
    lat = verify(flask.request.form['latitude'])
    lng = verify(flask.request.form['longitude'])
    mini = verify(flask.request.form['min'])
    maxi = verify(flask.request.form['max'])
    percentile = verify(flask.request.form['percentile'])
    deployer = "N/A"
    notes = verify(flask.request.form['notes'])
    submission = Vendors(name, lat, lng, mini, maxi, percentile, deployer, notes)
    db.session.add(submission)
    db.session.commit()
    return flask.redirect('/form')

@app.route('/update/<id>', methods=['POST'])
def edit(id):
    logger = Vendors.query.get(id);
    logger.longitude = verify(flask.request.form['longitude'])
    logger.latitude = verify(flask.request.form['latitude'])
    # logger.min = verify(flask.request.form['min'])
    # logger.max = verify(flask.request.form['max'])
    logger.percentile = verify(flask.request.form['percentile'])
    logger.previousPercentile = verify(flask.request.form['previous'])
    logger.deployer = "N/A"
    logger.notes = verify(flask.request.form['notes'])
    db.session.commit()
    return flask.redirect('/edit')

@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    Vendors.query.filter(Vendors.id == id).delete()
    db.session.commit()
    return flask.redirect('/edit')

@app.route('/data.geojson')
def makeGeoJson():
    vs = Vendors.query.all()
    features = []
    attrs = ['min', 'max', 'percentile', 'deployer', 'notes', 'previousPercentile']
    used = ['longitude', 'latitude', 'name']
    for i in vs:
        props = {}
        for attr in dir(i):
            if attr in attrs:
                props[attr] = getattr(i, attr)
        props['name'] = i.name
        info = {"geometry": {"coordinates": [i.longitude, i.latitude], "type": "Point"}, "properties": props, "type": "Feature"}
        features.append(info)
    out = {
        "features": features,
        "type": "FeatureCollection"
    }
    return out

@app.errorhandler(Exception)
def page404(e):
    eCode = 500
    message = "An unknown error occured!"
    try:
        app.log_exception(e)
        message = e.description
        eCode = e.code
    finally:
        return flask.render_template('error.html', error=eCode, message=message)

def verify(thing):
    if thing.replace(' ', '') == '' or thing == 'None':
        return None
    else:
        return thing

if __name__ == '__main__':
    app.run(host='localhost', debug=True)
