import os
from flask import Flask, request, Response
import requests
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='/app/logs/queries.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

ELASTICSEARCH_URL = 'http://elasticsearch:9200'

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    url = f'{ELASTICSEARCH_URL}/{path}'

    # Log the incoming request
    logging.info(f'Method: {request.method}, Path: {path}, Data: {request.get_data(as_text=True)}')

    # Forward the request to Elasticsearch
    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )

    # Create the response and forward it back to the client
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)