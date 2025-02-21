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

        try:
            if action == 'offer':
                driver_name = request.form.get('driver_name')
                seats = int(request.form.get('seats'))
                offer = RideOffer(event_id=event_id, driver_name=driver_name, seats_available=seats)
                db.session.add(offer)
                flash('Ride offer added successfully!', 'success')

            elif action == 'request':
                passenger_name = request.form.get('passenger_name')
                request_ride = RideRequest(event_id=event_id, passenger_name=passenger_name)
                db.session.add(request_ride)
                flash('Ride request added successfully!', 'success')

            elif action == 'delete_offer':
                offer_id = request.form.get('offer_id')
                offer = RideOffer.query.get_or_404(offer_id)
                if offer.event_id != event_id:
                    flash('Invalid request', 'danger')
                    return redirect(url_for('event_detail', event_id=event_id))

                # Clear any matches for this offer
                RideRequest.query.filter_by(matched_offer_id=offer.id).update({RideRequest.matched_offer_id: None})
                db.session.delete(offer)
                flash('Ride offer deleted successfully!', 'success')

            elif action == 'delete_request':
                request_id = request.form.get('request_id')
                ride_request = RideRequest.query.get_or_404(request_id)
                if ride_request.event_id != event_id:
                    flash('Invalid request', 'danger')
                    return redirect(url_for('event_detail', event_id=event_id))

                db.session.delete(ride_request)
                flash('Ride request deleted successfully!', 'success')

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error processing request: {str(e)}')
            flash(f'Error processing request: {str(e)}', 'danger')

    return render_template('event_detail.html', event=event)

@app.route('/event/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)

        # Delete all associated ride offers and requests
        RideRequest.query.filter_by(event_id=event_id).delete()
        RideOffer.query.filter_by(event_id=event_id).delete()
        db.session.delete(event)
        db.session.commit()

        flash('Event deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting event: {str(e)}')
        flash(f'Error deleting event: {str(e)}', 'danger')

    return redirect(url_for('events'))

@app.route('/matches/<int:event_id>')
def matches(event_id):
    event = Event.query.get_or_404(event_id)

    # Get all offers and requests
    offers = RideOffer.query.filter_by(event_id=event_id).all()
    requests = RideRequest.query.filter_by(event_id=event_id).all()

    # Track matches and waiting list
    matches = []
    waiting_list = []

    # Process existing matches first
    for request in requests:
        if request.matched_offer_id:
            offer = next((o for o in offers if o.id == request.matched_offer_id), None)
            if offer:
                matches.append({
                    'passenger': request.passenger_name,
                    'driver': offer.driver_name
                })
                continue

    # Match unmatched requests
    unmatched_requests = [r for r in requests if not r.matched_offer_id]
    random.shuffle(unmatched_requests)

    for request in unmatched_requests:
        matched = False
        for offer in offers:
            # Count existing matches for this offer
            existing_matches = len([r for r in requests if r.matched_offer_id == offer.id])
            available_seats = offer.seats_available - existing_matches

            if available_seats > 0:
                request.matched_offer_id = offer.id
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