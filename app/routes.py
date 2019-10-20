import os
import time
from flask import abort, request, jsonify
from app import app
import hmac
import hashlib
from functools import wraps
from app.tasks import generate_report


# Create a decorator function with decorator arguments. If you're not familiar with python decorator, I recommend
# to check Corey Schafer's youtube videos on Decorators: https://www.youtube.com/watch?v=FsAPt_9Bf3U and also this page
# https://python-3-patterns-idioms-test.readthedocs.io/en/latest/PythonDecorators.html
def validate_request(max_content_length):
    def wrap(func):
        @wraps(func)
        def wrapped_f(*args, **kwargs):
            # Following the step-by-step walk through guide for validating a slack request
            # https://api.slack.com/docs/verifying-requests-from-slack

            # 1. Grab my Slack Signing Secret
            slack_signing_secret = os.environ['SLACK_SIGNING_SECRET']

            # 2. Extract the timestamp and signature header from the request:
            timestamp = request.headers.get('X-Slack-Request-Timestamp')
            slack_signature = request.headers.get('X-Slack-Signature')
            content_length = request.headers.get('Content-Length')
            if None in (timestamp, slack_signature, content_length):
                return abort(400)

            # 3. Concatenate the version number, the timestamp and the request body
            # Checking the content length first before calling request.get_data() as a client could send dozens of
            # megabytes or more to cause memory problems on the server
            if int(content_length) > max_content_length:
                return abort(400)
            sig_basestring = str.encode('v0:' + str(timestamp) + ':') + request.get_data()

            # 4. Hash the resulting string, using the signing secret as a key, and taking the hex digest of the hash
            my_signature = 'v0=' + hmac.new(key=str.encode(slack_signing_secret),
                                            msg=sig_basestring,
                                            digestmod=hashlib.sha256).hexdigest()

            # 5. Compare the resulting signature to the header on the request
            if not hmac.compare_digest(my_signature, slack_signature):
                return abort(400)

            # Adding a timestamp check as suggested in the slack documentation
            # If the request timestamp is more than five minutes from local time.
            # It could be a replay attack, so let's ignore it
            if abs(time.time() - int(timestamp)) > 60 * 5:
                return abort(400)

            return func(*args, **kwargs)
        return wrapped_f
    return wrap


@app.route('/generate-report', methods=['POST'])
@validate_request(max_content_length=1000)
def gen_report():

    generate_report(request.form.get('response_url'))

    return jsonify(
        response_type='in_channel',
        text='Report is being generated',
    )
