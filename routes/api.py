from flask import Blueprint, request, jsonify, abort
from flask_login import login_required, current_user
from models.models import db, PedalSession
from datetime import datetime, timedelta
import sqlalchemy as sa

api = Blueprint('api', __name__)

@api.before_request
@login_required
def check_auth():
    pass

@api.route('/api/session/start', methods=['POST'])
def start_session():
    session = PedalSession(user_id=current_user.id, start_time=datetime.utcnow())
    db.session.add(session)
    db.session.commit()
    return jsonify({
        'session_id': session.id,
        'started_at': session.start_time.isoformat()
    })

@api.route('/api/session/data', methods=['POST'])
def session_data():
    data = request.json
    session_id = data.get('session_id')
    rpm = float(data.get('rpm', 0))
    voltage = float(data.get('voltage', 0))
    current = float(data.get('current', 0))
    
    session = PedalSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(403)
        
    session._rpm_sum += rpm
    session._voltage_sum += voltage
    session._current_sum += current
    session._data_points += 1
    
    session.avg_rpm = session._rpm_sum / session._data_points
    session.avg_voltage = session._voltage_sum / session._data_points
    session.avg_current = session._current_sum / session._data_points
    session.last_updated = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'status': 'ok'})

@api.route('/api/session/end', methods=['POST'])
def end_session():
    data = request.json
    session_id = data.get('session_id')
    
    session = PedalSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(403)
        
    session.end_time = datetime.utcnow()
    duration = (session.end_time - session.start_time).total_seconds()
    session.duration_seconds = int(duration)
    
    # energy_wh = avg_voltage * avg_current * (duration_seconds / 3600)
    session.energy_wh = session.avg_voltage * session.avg_current * (session.duration_seconds / 3600.0)
    # calories_burned = duration_seconds * 0.1
    session.calories_burned = session.duration_seconds * 0.1
    # co2_saved_g = energy_wh * 400
    session.co2_saved_g = session.energy_wh * 400
    
    db.session.commit()
    return jsonify(session.to_dict())

@api.route('/api/sessions', methods=['GET'])
def get_sessions():
    sessions = PedalSession.query.filter_by(user_id=current_user.id).order_by(PedalSession.start_time.desc()).all()
    return jsonify([s.to_dict() for s in sessions])

@api.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    session = PedalSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        abort(404)
    return jsonify(session.to_dict())

@api.route('/api/live', methods=['GET'])
def get_live():
    session = PedalSession.query.filter_by(user_id=current_user.id, end_time=None).order_by(PedalSession.start_time.desc()).first()
    if not session:
        return jsonify({'active': False})
    
    # Check connection status (received data in last 10 seconds)
    is_connected = False
    if session.last_updated:
        is_connected = (datetime.utcnow() - session.last_updated).total_seconds() < 10
    
    # Calculate current metrics (most recent average)
    return jsonify({
        'active': True,
        'session_id': session.id,
        'is_connected': is_connected,
        'metrics': {
            'rpm': session.avg_rpm,
            'voltage': session.avg_voltage,
            'current': session.avg_current
        },
        'totals': {
            'energy_wh': session.avg_voltage * session.avg_current * ((datetime.utcnow() - session.start_time).total_seconds() / 3600.0),
            'duration': int((datetime.utcnow() - session.start_time).total_seconds()),
            'calories': (datetime.utcnow() - session.start_time).total_seconds() * 0.1
        }
    })

@api.route('/api/stats/summary', methods=['GET'])
def get_summary():
    sessions = PedalSession.query.filter(PedalSession.user_id == current_user.id, PedalSession.end_time != None).all()
    
    total_energy = sum(s.energy_wh for s in sessions)
    total_calories = sum(s.calories_burned for s in sessions)
    total_co2 = sum(s.co2_saved_g for s in sessions)
    
    # Calculate streak
    today = datetime.utcnow().date()
    streak = 0
    current_date = today
    
    while True:
        has_session = PedalSession.query.filter(
            PedalSession.user_id == current_user.id,
            PedalSession.end_time != None,
            sa.func.date(PedalSession.start_time) == current_date
        ).first()
        
        if has_session:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
            
    return jsonify({
        'total_sessions': len(sessions),
        'total_energy_wh': total_energy,
        'total_calories': total_calories,
        'total_co2_saved_g': total_co2,
        'streak_days': streak
    })
