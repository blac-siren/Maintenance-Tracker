"""Module for endpoints."""
from flask_restplus import fields, Resource
from app.models.request import CreateRequest
from app.models.user import User
from app import api
from flask import request
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


@api.route('/register')
@api.doc(
    {
        201: 'user created successfully',
        400: 'No Input data provided',
        422: 'Invalid input data provided'
    },
    security=None)
class Registration(Resource):
    """Handles registration Routes."""

    def post(self):
        """Register new user."""
        data = request.get_json()
        try:
            email = data['email']
            username = data['username']
            password = data['password']
        except KeyError:
            return {'Message': 'Fill up all the fields!'}, 400

        if email in User.user_info:
            return {'message': 'Email already Exist'}
        if len(password) <= 8:
            return {'Message': "Password must be greater than 8"}
        else:
            user = User(username, email, password)
            user.create_user()
            return {
                'Account': user.create_user(),
                'Message': 'Successfully Registered'
            }, 201


@api.route('/login')
class login(Resource):
    """Handle /login route."""

    def post(self):
        """Login a registered user."""
        data = request.get_json()
        try:
            email = data['email']
            password = data['password']
        except KeyError:
            return {'Message': 'Invalid, all fields required!'}
        else:
            password_hash = User.user_info[email]['password']
            if email in User.user_info and bcrypt.check_password_hash(
                    password_hash, password):
                return {'Message': 'Successfully logged in'}, 200
            else:
                return {"Message": "Incorrect Email or Password "}


@api.route('/users/requests')
class RequestList(Resource):
    """Handle users/requests routes."""

    def get(self):
        """Handle [Endpoint] GET."""
        return {"Requests": CreateRequest.all_requests}, 200

    def post(self):
        """Handle [Endpoint] GET."""
        data = request.get_json()
        try:
            req = data['req']
            category = data['category']
            location = data['location']
        except KeyError:
            return {'Message': "All data required"}
        else:
            create = CreateRequest(req, category, location)
            create.save_request()
            return {"message": "successfully created"}, 201


@api.route('/users/requests/<int:id>')
class Request(Resource):
    def put(self, id):
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
