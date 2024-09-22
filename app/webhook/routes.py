from flask import Flask, Blueprint, request, jsonify
from datetime import datetime
from app.extensions import collection
import logging

app = Flask(__name__)

# Define the blueprint for webhook
webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    
    # Handle push event
    if event_type == 'push':
        author = data['pusher']['name']
        to_branch = data['ref'].split('/')[-1]
        timestamp = datetime.fromisoformat(data['head_commit']['timestamp'])
        
        # Check if the push event is a result of a merge
        commit_message = data['head_commit']['message']
        if "Merge pull request" in commit_message:
            # Skip processing push event that is a result of a merge
            return jsonify({'message': 'Push event ignored (merge commit)'}), 200

        # Process a normal push event
        event_data = {
            "type": "push",
            "author": author,
            "to_branch": to_branch,
            "timestamp": timestamp,
        }
    
    # Handle pull request events (including merge)
    elif event_type == 'pull_request':
        action = data['action']  # Check the action on the pull request
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        created_timestamp = datetime.fromisoformat(data['pull_request']['created_at'])
        
        # For all pull requests, store basic PR data
        event_data = {
            "type": "pull_request",
            "action": action,
            "author": author,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": created_timestamp
        }
        
        # If the PR was closed and merged, capture additional merge data
        if action == 'closed' and data['pull_request']['merged']:
            event_data["type"] = "merge"
            event_data["merged_by"] = data['pull_request']['merged_by']['login']
            
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
