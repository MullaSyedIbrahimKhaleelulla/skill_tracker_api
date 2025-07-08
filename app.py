from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ibrahim1234@localhost:5432/skill_tracker_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(100), nullable=False)
    goal_hours = db.Column(db.Integer, nullable=False)
    hours_done = db.Column(db.Integer, default=0)
    is_completed = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return jsonify({"message": "Skill Tracker API Running!"})

@app.route('/skills', methods=['POST'])
def add_skill():
    data = request.get_json()
    skill = Skill(
        skill_name=data['skill_name'],
        goal_hours=data['goal_hours']
    )
    db.session.add(skill)
    db.session.commit()
    return jsonify({"message": "Skill added!"})


@app.route('/skills', methods=['GET'])
def get_skills():
    skills = Skill.query.all()
    result = []
    for s in skills:
        progress = (s.hours_done / s.goal_hours * 100) if s.goal_hours else 0
        result.append({
            "id": s.id,
            "skill_name": s.skill_name,
            "goal_hours": s.goal_hours,
            "hours_done": s.hours_done,
            "is_completed": s.is_completed,
            "progress": round(progress, 2)
        })
    return jsonify(result)


@app.route('/skills/<int:id>', methods=['PUT'])
def update_skill(id):
    skill = Skill.query.get(id)
    if not skill:
        return jsonify({"message": "Skill not found"}), 404

    data = request.get_json()
    skill.skill_name = data.get('skill_name', skill.skill_name)
    skill.goal_hours = data.get('goal_hours', skill.goal_hours)
    skill.hours_done = data.get('hours_done', skill.hours_done)

    if skill.hours_done >= skill.goal_hours:
        skill.is_completed = True
    else:
        skill.is_completed = data.get('is_completed', skill.is_completed)

    db.session.commit()
    return jsonify({"message": "Skill updated!"})

@app.route('/skills/<int:id>', methods=['DELETE'])
def delete_skill(id):
    skill = Skill.query.get(id)
    if not skill:
        return jsonify({"message": "Skill not found"}), 404

    db.session.delete(skill)
    db.session.commit()
    return jsonify({"message": "Skill deleted!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)

