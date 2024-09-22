from flask import Flask, Blueprint, request, jsonify
from datetime import datetime
from app.extensions import collection
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    
    if event_type == 'push':
        author = data['pusher']['name']
        to_branch = data['ref'].split('/')[-1]
        timestamp = datetime.fromisoformat(data['head_commit']['timestamp'])
        
        commit_message = data['head_commit']['message']
        if "Merge pull request" in commit_message:
            return jsonify({'message': 'Push event ignored (merge commit)'}), 200

        event_data = {
            "action": "push",
            "author": author,
            "to_branch": to_branch,
            "timestamp": timestamp,
        }
    
    elif event_type == 'pull_request':
        typeof = data['action']  
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        created_timestamp = datetime.fromisoformat(data['pull_request']['created_at'])
        
        event_data = {
            "action": "pull_request",
            "author": author,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": created_timestamp
        }
        
        if typeof == 'closed' and data['pull_request']['merged']:
            event_data["action"] = "merge"
            event_data["merged_by"] = data['pull_request']['merged_by']['login']
            
    else:
        return jsonify({'message': 'Event not supported'}), 400

    collection.insert_one(event_data)
    return jsonify({'message': 'Event received'}), 200

@webhook.route('/events', methods=['GET'])
@cross_origin()
def get_events():
    events = list(collection.find().sort("timestamp", -1).limit(10))
    for event in events:
        event['_id'] = str(event['_id'])
    return jsonify(events), 200

app.register_blueprint(webhook)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
