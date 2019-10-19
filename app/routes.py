import os
from flask import abort, request, jsonify
from app import app
from app.tasks import generate_report


def is_request_valid(request):
    is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
    is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']

    return is_token_valid and is_team_id_valid


@app.route('/slash-command', methods=['POST'])
def slash_command():
    if not is_request_valid(request):
        abort(400)

    generate_report(request.form.get('response_url'))

    return jsonify(
        response_type='in_channel',
        text='Test 123',
    )
