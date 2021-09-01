#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.sql.expression import false
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app,db)
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
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120)) 
    website_link = db.Column(db.String(120))
    genres = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500), default='')
    shows = db.relationship('Show', backref='Venue', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500), default='')
    shows = db.relationship('Show', backref='Artist', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__='Show'

    id = db.Column(db.Integer, primary_key=True)
    starttime = db.Column(db.String(), nullable=False)
    venueid = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artistid = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  stateandvenue = Venue.query.distinct(Venue.state, Venue.city).all()
  data = []
  for venue in stateandvenue:
    filtervenues = Venue.query.filter_by(city=venue.city, state=venue.state).all()   
    venueforcitystate = []      
    for filtervenue in filtervenues:
      venueforcitystate.append({
      "id": filtervenue.id,
      "name": filtervenue.name,
      "num_upcoming_shows": 0
      })    
    data.append({
      "city": venue.city,
      "state":venue.state,
      "venues": venueforcitystate
    })  
  return render_template('pages/venues.html', areas=data) 

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
  response = {
    "count": len(venues),
    "data": []
  }
  for venue in venues:
    response["data"].append({
        'id': venue.id,
        'name': venue.name,
    })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  now =babel.dates.format_datetime(datetime.now(), "EE MM, dd, y h:mma", locale='en')
  venueforid = Venue.query.get(venue_id)
  pastshows = Show.query.filter(Show.venueid == venue_id, Show.starttime <= now)
  upcomingshows = Show.query.filter(Show.venueid == venue_id, Show.starttime > now)
  pastshowsdata = []
  for pastshow in pastshows:
    artist = Artist.query.get(pastshow.artistid)
    pastshowsdata.append({
      "venue_id": artist.id,
      "venue_name": artist.name,
      "venue_image_link": artist.image_link,
      "start_time": pastshow.starttime
    })
  upcominghowsdata = []
  for upcomingshow in upcomingshows:
    artist = Artist.query.get(upcomingshow.artistid)
    upcominghowsdata.append({
      "venue_id": artist.id,
      "venue_name": artist.name,
      "venue_image_link": artist.image_link,
      "start_time": upcomingshow.starttime
    })
  venudatawithshow={
    "id": venueforid.id,
    "name": venueforid.name,
    "genres": venueforid.genres,
    "address": venueforid.address,
    "city": venueforid.city,
    "state": venueforid.state,
    "phone": venueforid.phone,
    "website": venueforid.website_link,
    "facebook_link": venueforid.facebook_link,
    "seeking_talent": False,
    "seeking_description": venueforid.seeking_description,
    "image_link": venueforid.image_link,
    "past_shows": pastshowsdata,
    "upcoming_shows": upcominghowsdata,
    "past_shows_count": len(pastshowsdata),
    "upcoming_shows_count": len(upcominghowsdata),
  }  
  return render_template('pages/show_venue.html', venue=venudatawithshow)

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
  newvenue = Venue(
        name= request.form.get('name', ''),     
        address=request.form.get('address', ''),
        city=request.form.get('city', ''),
        state=request.form.get('state', ''),
        phone=request.form.get('phone', ''),
        facebook_link=request.form.get('facebook_link', ''),
        image_link=request.form.get('image_link', ''),
        website_link = request.form.get('website_link', ''),
        genres = request.form.get('genres', ''),
        #seeking_talent = request.form.get('seeking_talent'),
        seeking_description =request.form.get('seeking_description', ''))
  try:
    db.session.add(newvenue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + newvenue.name + ' could not be listed.')
  finally:
    db.session.close()
  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    db.session.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
    return False
  finally:
    db.session.close()
  return True
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = Artist.query.all()
  artistdata= []
  for artist in artists:
    artistdata.append(
      {
      "id": artist.id,
      "name": artist.name
      }
    )
  return render_template('pages/artists.html', artists=artistdata)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
  response = {
    "count": len(artists),
    "data": []
  }
  for artist in artists:
    response["data"].append({
        'id': artist.id,
        'name': artist.name,
    }) 
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  now =babel.dates.format_datetime(datetime.now(), "EE MM, dd, y h:mma", locale='en')
  artist = Artist.query.get(artist_id)
  pastshows = Show.query.filter(Show.artistid == artist_id, Show.starttime <= now)
  upcomingshows = Show.query.filter(Show.artistid == artist_id, Show.starttime > now)
  pastshowsdata = []
  for pastshow in pastshows:
    venue = Venue.query.get(pastshow.venueid)
    pastshowsdata.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": pastshow.starttime
    })
  upcominghowsdata = []
  for upcomingshow in upcomingshows:
    venue = Venue.query.get(upcomingshow.venueid)
    upcominghowsdata.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": upcomingshow.starttime
    })
  artiswithshow={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": False,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": pastshowsdata,
    "upcoming_shows": upcominghowsdata,
    "past_shows_count": len(pastshowsdata),
    "upcoming_shows_count": len(upcominghowsdata),
  }  
  return render_template('pages/show_artist.html', artist=artiswithshow)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm() 
  artist = Artist.query.get(artist_id)
  if artist:
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website_link
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    form = ArtistForm()
    artist = Artist.query.get(artist_id)     
    artist.name= request.form.get('name', ''), 
    artist.city=request.form.get('city', ''),
    artist.state=request.form.get('state', ''),
    artist.phone=request.form.get('phone', ''),
    artist.facebook_link=request.form.get('facebook_link', ''),
    artist.image_link=request.form.get('image_link', ''),
    artist.website_link = request.form.get('website_link', ''),
    artist.genres = request.form.get('genres', ''),
    #seeking_venue = request.form.get('seeking_venue'),
    artist.seeking_description =request.form.get('seeking_description', '')
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if venue:     
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website_link.data = venue.website_link
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    form = VenueForm()
    venue = Venue.query.get(venue_id)    
    venue.name= request.form.get('name', ''), 
    venue.city=request.form.get('city', ''),
    venue.state=request.form.get('state', ''),
    venue.phone=request.form.get('phone', ''),
    venue.address=request.form.get('address', ''),
    venue.facebook_link=request.form.get('facebook_link', ''),
    venue.image_link=request.form.get('image_link', ''),
    venue.website_link = request.form.get('website_link', ''),
    venue.genres = request.form.get('genres', ''),
    #seeking_talent = request.form.get('seeking_talent'),
    venue.seeking_description =request.form.get('seeking_description', '')
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  newartist = Artist(
      name= request.form.get('name', ''), 
      city=request.form.get('city', ''),
      state=request.form.get('state', ''),
      phone=request.form.get('phone', ''),
      facebook_link=request.form.get('facebook_link', ''),
      image_link=request.form.get('image_link', ''),
      website_link = request.form.get('website_link', ''),
      genres = request.form.get('genres', ''),
      #seeking_venue = request.form.get('seeking_venue'),
      seeking_description =request.form.get('seeking_description', ''))
  try:    
    db.session.add(newartist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback
    flash('An error occurred. Artist ' + newartist.name + ' could not be listed.')
  finally:
    db.session.close  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  data = []
  for show in shows:
    artist = Artist.query.get(show.artistid)
    venue = Venue.query.get(show.venueid)
    data.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.starttime  
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
  newshow = Show(
      venueid = request.form.get('artist_id', ''),     
      artistid = request.form.get('venue_id', ''),
      starttime =request.form.get('start_time')
  )  
  try:    
    db.session.add(newshow)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close

  # on successful db insert, flash success  
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
