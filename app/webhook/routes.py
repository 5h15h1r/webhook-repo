from flask import Flask, Blueprint, request, jsonify
from datetime import datetime
from app.extensions import collection

app = Flask(__name__)

# Define the blueprint for webhook
webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/')
def hello():
    return 'hello'

@webhook.route('/receiver', methods=["POST"])
def receiver():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    
    if event_type == 'push':
        author = data['pusher']['name']
        to_branch = data['ref'].split('/')[-1]
        timestamp = datetime.strptime(data['head_commit']['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
        event_data = {
            "type": "push",
            "author": author,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
    elif event_type == 'pull_request':
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        timestamp = datetime.strptime(data['pull_request']['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        event_data = {
            "type": "pull_request",
            "author": author,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
    elif event_type == 'pull_request' and data['pull_request']['merged']:
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        timestamp = datetime.strptime(data['pull_request']['merged_at'], "%Y-%m-%dT%H:%M:%SZ")
        event_data = {
            "type": "merge",
            "author": author,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
    else:
        return jsonify({'message': 'Event not supported'}), 400

    collection.insert_one(event_data)
    return jsonify({'message': 'Event received'}), 200

@webhook.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find().sort("timestamp", -1).limit(10))
    for event in events:
        event['_id'] = str(event['_id'])
    return jsonify(events), 200

app.register_blueprint(webhook)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
