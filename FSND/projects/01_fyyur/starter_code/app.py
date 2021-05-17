#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://siwenwang@localhost:5432/fyyur'
db = SQLAlchemy(app)


migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref = 'Venue', lazy = True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref = 'Artist', lazy = True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable = False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  data = []
  venue_state_and_city = ''
  venues = Venue.query.group_by(Venue.id, Venue.city, Venue.state).all()
  for venue in venues:
    if venue_state_and_city == venue.city + venue.state:
      data[len(data)-1]["venues"].append({
      "id": venue.id,
      "name": venue.name
      })
    else:
      venue_state_and_city = venue.city + venue.state
      data.append({
        "city": venue.city,
        "state": venue.state,
        "venues":[{
        "id": venue.id,
        "name":venue.name
        }]
      })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

  venue_query = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%'))
  print(venue_query)
  
  venue_list = []

  for venue in venue_query:
    venue_list.append({
      "id": venue.id,
      "name": venue.name,
    })

  response = {
    "count": len(venue_list),
    "data": venue_list
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id


  venue = Venue.query.get(venue_id)

  if not venue:
    return render_template('errors/404.html')

  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()
  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  
  upcoming_shows = []
  past_shows = []

  for show in past_shows_query:
    past_shows.append({
    "artist_id": show.artist_id,
    "artist_name": show.Artist.name,
    "artist_image_link":show.Artist.image_link,
    "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  for show in upcoming_shows_query:
    upcoming_shows.append({
    "artist_id": show.artist_id,
    "artist_name": show.Artist.name,
    "artist_image_link": show.Artist.image_link,
    "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")    
    })


    
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    if 'seeking_talent' in request.form:
      seeking_talent = request.form['seeking_talent'] == 'y'
    else:
      seeking_talent = False
    #seeking_talent = True if request.form['seeking_talent'] in ('y', True, 't', 'True') else False,
    new_venue = Venue(
      name = request.form['name'],
      genres = request.form.getlist('genres'),
      address = request.form['address'],
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      website = request.form['website_link'],
      facebook_link = request.form['facebook_link'],
      image_link = request.form['image_link'],
      seeking_talent = seeking_talent,
      seeking_description = request.form['seeking_description']
    )
    db.session.add(new_venue)
    db.session.commit() 
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
    
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    Venue.query.filter_by(id = venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  
  return None



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  artists = Artist.query.all()

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  artist_query = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%'))
  print(artist_query)
  
  artist_list = []

  for artist in artist_query:
    artist_list.append({
      "id": artist.id,
      "name": artist.name,
    })

  response = {
    "count": len(artist_list),
    "data": artist_list
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given artist_id
  # TODO: replace with real venue data from the venue table, using artist_id

  artist = Artist.query.get(artist_id)

  if not artist:
    return render_template('errors/404.html')

  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
  
  upcoming_shows = []
  past_shows = []

  for show in past_shows_query:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "venue_image_link":show.Venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  for show in upcoming_shows_query:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "venue_image_link": show.Venue.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")    
    })


    
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  
  return render_template('pages/show_artist.html', artist=data)





#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from venue with ID <artist_id>
  if artist:
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <artist_id> using the new attributes

  artist = Artist.query.get(artist_id)

  try: 
    if artist:
      if 'seeking_venue' in request.form:
        seeking_venue = True
      else:
        seeking_venue = False
    artist.name = request.form['name']
    artist.genres = request.form.getlist('genres')
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.website = request.form['website_link']
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = request.form['image_link']
    artist.seeking_venue = seeking_venue
    artist.seeking_description = request.form['seeking_description']
    db.session.commit()

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
    
  finally:
    db.session.close()
    flash('Artist ' + request.form['name'] + ' was successfully edited!')

  return redirect(url_for('show_artist', artist_id=artist_id))





@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue:
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.website_link.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description

  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue = venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  venue = Venue.query.get(venue_id)

  try: 
    if venue:
      if 'seeking_talent' in request.form:
        seeking_talent = True
      else:
        seeking_talent = False
    venue.name = request.form['name']
    venue.genres = request.form.getlist('genres')
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.website = request.form['website_link']
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.seeking_talent = seeking_talent
    venue.seeking_description = request.form['seeking_description']
    db.session.commit()

  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
    
  finally:
    db.session.close()
    flash('Venue ' + request.form['name'] + ' was successfully edited!')

  return redirect(url_for('show_venue', venue_id=venue_id))







#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new venue listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error = False
  try:
    if 'seeking_venue' in request.form:
      seeking_venue = request.form['seeking_venue'] in ['y',True]
    else:
      seeking_venue = False

    new_artist = Artist(
      name = request.form['name'],
      genres = request.form.getlist('genres'),
      city = request.form['city'],
      state = request.form['state'],
      phone = request.form['phone'],
      website = request.form['website_link'],
      facebook_link = request.form['facebook_link'],
      image_link = request.form['image_link'],
      seeking_venue = seeking_venue,
      seeking_description = request.form['seeking_description']
    )
    db.session.add(new_artist)
    db.session.commit() 
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')







#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]

  shows_query = db.session.query(Show).join(Artist).join(Venue).all()
  data = []
  for show in shows_query:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "artist_id":show.artist_id,
      "artist_name": show.Artist.name,
      "artist_image_link":show.Artist.image_link,
      "start_time":show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    new_show = Show(
    venue_id = request.form['venue_id'],
    artist_id = request.form['artist_id'],
    start_time = request.form['start_time']
    )
    db.session.add(new_show)
    db.session.commit() 
    flash('Show was successfully listed!')

  except: 
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  
  finally:
    db.session.close()




  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:

if __name__ == '__main__':
    app.run()


# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
