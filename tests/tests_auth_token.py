from django.test import TestCase, Client
import os
# importing the requests library
import requests
import json
import jwt
from mentorq_main.settings.local import SECRET_KEY

'''
Once we receive test email and password information we will replace them within the respective
unit tests

Make sure the HackRU backend is running and the mentorQ backend is running in order to perform these tests
'''


def connect_to_lcs(email, password):
    # defining a params dict for the parameters to be sent to the API
    PARAMS = {'email': email,
              'password': password}

    # sending get request and saving the response as response object
    result = requests.post(url='http://api.hackru.org/dev/authorize', data=json.dumps(PARAMS))
    assert (result is not None)
    return result


def connect_to_mentorq(email, LCStoken):
    c = Client()
    # defining a params dict for the parameters to be sent to the API
    PARAMS = {'email': email,
              'lcs_token': LCStoken}

    # sending get request and saving the response as response object
    result = c.post(path='/api/auth/token/', data=PARAMS)
    assert (result is not None)
    return result


class AuthTestCase(TestCase):
    @staticmethod
    def setup():
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mentorq_main.settings.local')
    '''
     Tests if given a generic user that exists in LCS we will be able to correctly identify it they have
     valid token credentials
    '''

    @staticmethod
    def test_user_validity():
        print("Testing if we can correctly identify if someone is a user... 'testUserValidity' ")
        email = os.environ.setdefault("USER_EMAIL", '')
        password = os.environ.setdefault("USER_PASS", '')

        result = connect_to_lcs(email, password)
        result_json = result.json()

        # received the auth token from LCS
        auth_token = result_json['body']['token']

        # test the mentorq backend
        mentorq_result = connect_to_mentorq(email, auth_token)
        mentorq_json = mentorq_result.json()
        jwt_data = jwt.decode(mentorq_json["refresh"], SECRET_KEY)
        print("Successfully recognized user")

    '''
     Tests if we will be able to correctly identify someone as a mentor within LCS via mentorq
    '''

    @staticmethod
    def test_mentor_validity():
        print("Testing if we can correctly identify if someone is a mentor... 'testMentorValidity' ")
        email = os.environ.setdefault("MENTOR_EMAIL", '')
        password = os.environ.setdefault("MENTOR_PASS", '')

        result = connect_to_lcs(email, password)
        result_json = result.json()

        # received the auth token from LCS
        authToken = result_json['body']['token']

        # test the mentorq backend
        mentorq_result = connect_to_mentorq(email, authToken)
        mentorq_json = mentorq_result.json()
        jwt_data = jwt.decode(mentorq_json["refresh"], SECRET_KEY)
        assert jwt_data['mentor']
        print("Successfully recognized mentor")

    '''
     Tests if we will be able to correctly identify someone as a director within LCS via mentorq
    '''

    @staticmethod
    def test_director_validity():
        print("Testing if we can correctly identify if someone is a director... 'testDirectorValidity' ")
        email = os.environ.setdefault("DIRECTOR_EMAIL", '')
        password = os.environ.setdefault("DIRECTOR_PASS", '')

        result = connect_to_lcs(email, password)
        result_json = result.json()

        # received the auth token from LCS
        auth_token = result_json['body']['token']

        # test the mentorq backend
        mentorq_result = connect_to_mentorq(email, auth_token)
        mentorq_json = mentorq_result.json()
        jwt_data = jwt.decode(mentorq_json['refresh'], SECRET_KEY)
        assert jwt_data['director']
        print("Successfully recognized director")
