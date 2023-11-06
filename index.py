from flask import Flask, jsonify, request, make_response
from functools import wraps
import json
import time

app = Flask(__name__)

# Dummy data storage for example purposes
resources = {}

# Dummy function for authentication (to be replaced with real authentication logic)
def authenticate(auth_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if auth_type == 'null':
                # Skip auth for testing (Do not use in production!)
                return f(*args, **kwargs)
            elif auth_type == 'bearer':
                # Implement Bearer Auth logic here
                auth_header = request.headers.get('Authorization')
                if not auth_header or 'Bearer YOUR_SOLID_API_KEY' not in auth_header:
                    return make_response('Unauthorized', 401)
                return f(*args, **kwargs)
            elif auth_type == 'pki':
                # Implement PKI Auth logic here
                auth_header = request.headers.get('Auth')
                if not auth_header or not validate_pki(auth_header):
                    return make_response('Unauthorized', 401)
                return f(*args, **kwargs)
            else:
                return make_response('Authentication type not supported', 400)
        return decorated_function
    return decorator

# Dummy function for PKI validation (to be replaced with real PKI validation logic)
def validate_pki(auth_header):
    # For example, check if the timestamp in the header is within 60s of the current time
    timestamp = int(auth_header.split(' ')[-1])
    return abs(time.time() - timestamp) < 60

# Enable CORS on all routes
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/<path:resource>', methods=['GET', 'HEAD', 'OPTIONS'])
@authenticate('null')  # Replace 'null' with 'bearer' or 'pki' for other auth types
def read_resource(resource):
    if request.method in ['GET', 'HEAD']:
        data = resources.get(resource)
        if data:
            return jsonify(data), 200
        else:
            return jsonify({"message": "Resource not found"}), 404
    else:
        # OPTIONS request
        return '', 204

@app.route('/<path:resource>', methods=['PUT', 'DELETE'])
@authenticate('null')  # Replace 'null' with 'bearer' or 'pki' for other auth types
def write_resource(resource):
    if request.method == 'PUT':
        resources[resource] = request.json
        return jsonify({"message": "Resource created"}), 201
    elif request.method == 'DELETE':
        if resource in resources:
            del resources[resource]
            return '', 204
        else:
            return jsonify({"message": "Resource not found"}), 404

# Serve the JSON profile at the root
@app.route('/')
def index():
    profile_json = {
      "@context": [
        "https://www.w3.org/ns/activitystreams",
        "http://w3id.org/webid"
      ],
      "@id": "",
      "primaryTopic": {
        "@id": "#me",
        "@type": ["Person", "Actor"],
        "name": "Will Smith",
        "img": "avatar.png",
        "storage": "/",
        "knows": "http://alice.example/#me",
        "followers": "followers",
        "following": "following",
        "inbox": "inbox",
        "outbox": "outbox",
        "pubkey": "1234abc"
      }
    }
    return jsonify(profile_json)

if __name__ == '__main__':
    app.run(debug=True)
