from flask import render_template, request, redirect, url_for, flash
from datetime import datetime
import random
from app import app, db
from models import Event, RideOffer, RideRequest

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events', methods=['GET', 'POST'])
def events():
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            date_str = request.form.get('date')
            destination = request.form.get('destination')

            if not all([title, date_str, destination]):
                flash('All fields are required', 'danger')
                return redirect(url_for('events'))

            date = datetime.strptime(date_str, '%Y-%m-%d')
            event = Event(title=title, date=date, destination=destination)
            db.session.add(event)
            db.session.commit()
            flash('Event created successfully!', 'success')
            return redirect(url_for('events'))

        except Exception as e:
            app.logger.error(f'Error creating event: {str(e)}')
            flash(f'Error creating event: {str(e)}', 'danger')
            db.session.rollback()

    events = Event.query.order_by(Event.date).all()
    return render_template('events.html', events=events)

@app.route('/event/<int:event_id>', methods=['GET', 'POST'])
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'offer':
            driver_name = request.form.get('driver_name')
            seats = int(request.form.get('seats'))
            offer = RideOffer(event_id=event_id, driver_name=driver_name, seats_available=seats)
            db.session.add(offer)

        elif action == 'request':
            passenger_name = request.form.get('passenger_name')
            request_ride = RideRequest(event_id=event_id, passenger_name=passenger_name)
            db.session.add(request_ride)

        db.session.commit()
        flash('Your submission has been recorded!', 'success')

    return render_template('event_detail.html', event=event)

@app.route('/matches/<int:event_id>')
def matches(event_id):
    event = Event.query.get_or_404(event_id)

    # Reset previous matches
    RideRequest.query.filter_by(event_id=event_id).update({RideRequest.matched_offer_id: None})
    db.session.commit()

    # Get all offers and requests
    offers = RideOffer.query.filter_by(event_id=event_id).all()
    requests = RideRequest.query.filter_by(event_id=event_id).all()

    # Shuffle requests for random matching
    random.shuffle(requests)

    # Match riders to drivers
    matches = []
    waiting_list = []

    for request in requests:
        matched = False
        for offer in offers:
            if offer.seats_available > 0:
                request.matched_offer_id = offer.id
                offer.seats_available -= 1
                matches.append({
                    'passenger': request.passenger_name,
                    'driver': offer.driver_name
                })
                matched = True
                break
        if not matched:
            waiting_list.append(request.passenger_name)

    db.session.commit()

    return render_template('matches.html', 
                         event=event, 
                         matches=matches, 
                         waiting_list=waiting_list)