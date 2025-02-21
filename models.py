from datetime import datetime
from app import db

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    destination = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    ride_offers = db.relationship('RideOffer', backref='event', lazy=True)
    ride_requests = db.relationship('RideRequest', backref='event', lazy=True)

class RideOffer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    driver_name = db.Column(db.String(100), nullable=False)
    seats_available = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RideRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    passenger_name = db.Column(db.String(100), nullable=False)
    matched_offer_id = db.Column(db.Integer, db.ForeignKey('ride_offer.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
