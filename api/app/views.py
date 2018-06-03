"""Module for endpoints."""
from flask_restplus import fields, Resource
from app.models.request import CreateRequest
from app.models.user import User
from app import api
from flask import request, jsonify, abort, make_response, g
from flask_bcrypt import Bcrypt
from functools import wraps

import re
import json

bcrypt = Bcrypt()

current_user = []


def login_required(f):
    """Check if user is logged in."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        """Wrap the function."""

        if len(current_user) == 0:
            return make_response(
                jsonify({
                    'message': 'Unauthorized access. Please login!.'
                }), 401)

        return f(*args, **kwargs)

    return wrapper


# Namespaces
auth_namespace = api.namespace(
    'auth', description='Authentication Related Operation')

request_namespace = api.namespace(
    'users', description='Request Related Operation')

registration_model = api.model(
    'Registration', {
        "username":
        fields.String(
            required=True, description='Username', example="Joe_doe"),
        "email":
        fields.String(
            requires=True,
            description='email account',
            example="joe_doe@example.com"),
        "password":
        fields.String(
            requires=True,
            description="Your password account",
            example="U#76pJr3r")
    })

login_model = api.model(
    'Login', {
        "email":
        fields.String(
            requires=True,
            description='email account',
            example="joe_doe@example.com"),
        "password":
        fields.String(
            requires=True,
            description="Your password account",
            example="U#76pJr3r")
    })

Request_model = api.model(
    'Request', {
        "user_request":
        fields.String(
            requires=True, description='Request made', example="Plumbering"),
        "category":
        fields.String(
            requires=True,
            description="Is it maintenance or repair services",
            example="Repaire"),
        "location":
        fields.String(
            requires=True,
            description="Location",
            example="Westland st 12235 House: 345E")
    })

# User registration validation
email_regex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")


@auth_namespace.route('/register')
@api.doc(
    {
        201: 'user created successfully',
        400: 'No Input data provided',
        422: 'Invalid input data provided'
    },
    security=None)
class Registration(Resource):
    """Handles registration Routes."""

    @api.expect(registration_model)
    def post(self):
        """Register new user."""
        data = request.get_json()
        try:
            email = data['email']
            username = data['username']
            password = data['password']
        except KeyError:
            return {'Message': 'All input data required!'}, 400
        if len(email) > 5:
            if not re.match(email_regex, email):
                return {
                    'message': '{} is not a valid email address'.format(email)
                }, 400
        else:
            return {
                'message': 'Email address must be 6 characters or more'
            }, 411

        if [
                duplicate_email for duplicate_email in User.user_info
                if duplicate_email['email'] == email
        ]:
            return {'message': 'Email already Exist'}, 406
        else:
            if len(password) <= 8:
                return {'Message': "Password must be greater than 8"}, 411
            else:
                user = User(username, email, password)
                return {
                    'Account': user.create_user(),
                    'Message': 'Successfully Registered'
                }, 201


@auth_namespace.route('/login')
class login(Resource):
    """Handle /login route."""

    @api.expect(login_model)
    def post(self):
        """Login a registered user."""
        data = request.get_json()
        try:
            email = data['email']
            password = data['password']
        except KeyError:
            return {'Message': 'Invalid, all input data required!'}, 400
        else:
            if [
                    user for user in User.user_info if user['email'] == email
                    and bcrypt.check_password_hash(user['password'], password)
            ]:
                global current_user
                current_user = [email]
                return {
                    "current_user": current_user,
                    'Message': 'Successfully logged in'
                }, 200
            else:
                return {"Message": "Incorrect Email or Password "}, 411


@request_namespace.route('/requests')
class RequestList(Resource):
    """Handle users/requests routes."""

    @login_required
    def get(self):
        """Handle [Endpoint] GET."""
        if CreateRequest.all_requests:
            return {"Requests": CreateRequest.all_requests}, 200

    @login_required
    @api.expect(Request_model)
    def post(self):
        """Handle [Endpoint] GET."""
        data = request.get_json()
        try:
            user_request = data['user_request']
            category = data['category']
            location = data['location']
        except KeyError:
            return {'Message': "All input data required"}, 400
        else:
            create = CreateRequest(user_request, category, location)
            create.save_request()
            return {"message": "Request Successfully created"}, 201


@request_namespace.route('/requests/<int:id>')
class Request(Resource):
    """Handle  users/requests routes."""

    @api.expect(Request_model)
    def put(self, id):
        """Handle [endpoint] PUT."""
        for req in CreateRequest.all_requests:
            if req == id:
                request_data = CreateRequest.all_requests[id]

        if len(request_data) == 0:
            return {"Message": "Not found"}, 404
        data = request.get_json()
        try:
            request_data['category'] = data['category']
            request_data['req'] = data['req']
            request_data['location'] = data['location']

        except KeyError:
            return {'Message': "All data required"}
        else:

            return {"message": "successfully updated"}

    def get(self, id):
        """Get one request by ID."""
        for req in CreateRequest.all_requests:
            if req == id:
                request_data = CreateRequest.all_requests[id]
        return {'request': request_data}

    def delete(self, id):
        """Delete a request."""
        for req in CreateRequest.all_requests:
            if req == id:
                request_data = CreateRequest.all_requests[id]
        return {"message": "Deleted {} successfully".format(request_data)}
