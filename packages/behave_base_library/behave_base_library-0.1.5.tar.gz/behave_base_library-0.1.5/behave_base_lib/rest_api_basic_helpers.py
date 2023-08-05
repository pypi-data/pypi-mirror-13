import requests

def erase_last_response(context):
    """
    Erase the content of the env variable for api responses (used by API methods)
    :param context: The working context
    :return: Nothing, it sets the variable an empty string value
    """
    context.config.userdata['last_response'] = ""

def set_api_response(context, response):
    """
    Set a value to the env variable for the last api response (used by API methods)
    :param context: The working context
    :param response: The last response
    :return: Nothing, it sets the response in the variable
    """
    context.config.userdata['last_response'] = response

def get_last_response(context):
    """
    Returns the last response stored in the variable (used by API methods)
    :param context: The working context
    :return: The last response
    """
    return context.config.userdata.get('last_response')

def get_method(context, url, check_response_code = True, check_message = None):
    """
    Calls the get method in the specified url
    :param context: The working context
    :param url: The url to get
    :param check_response_code: Verifies with an assert that the response is 200 http (default:True)
    :param check_message: Checks for the specified message in the response (default: None)
    :return: It stores the response in the variable in the api context, it can be obtained with get_last_response method
    """
    erase_last_response(context)
    response = requests.get(url)
    set_api_response(context, response)
    if check_response_code:
        assert response.status_code == 200, "Error, status code is {code}, expected 200. The error is {error}".format(code=response.status_code, error=response.text)
    if check_message != None:
        check_response_message(response, check_message)

def delete_method(context, url, check_response_code = True, check_message = None):
    """
    Calls the method delete in the specified url
    :param context: The working context
    :param url: The url to delete
    :param check_response_code: Verifies with an assert that the response is 200 http (default:True)
    :param check_message: Checks for the specified message in the response (default: None)
    :return: It stores the response in the variable api context, it can be obtained with get_last response method
    """
    erase_last_response(context)
    response = requests.delete(url)
    set_api_response(context, response)
    if check_response_code:
        assert response.status_code == 200, "Error, status code is {code}, expected 200. The error is {error}".format(code=response.status_code,  error=response.text)
    if check_message != None:
        check_response_message(response, check_message)

def post_method(context, url, data, check_response_code = True, check_message = None):
    """
    Calls the post method in the specified url with the specified payload
    :param context: The working context
    :param url: The url to post
    :param data: The payload
    :param check_response_code: Verifies with an assert that the response is 200 http (default:True)
    :param check_message: Checks for the specified message in the response (default: None)
    :return: It stores the response in the variable in the api context, it can be obtained with get_last_response method
    """
    erase_last_response(context)
    response = requests.post(url, data)
    set_api_response(context, response)
    if check_response_code:
        assert response.status_code == 200, "Error, status code is {code}, expected 200. The error is {error}".format(code=response.status_code, error=response.text)
    if check_message != None:
        check_response_message(response, check_message)

def put_method(context, url, data, check_response_code = True, check_message = None):
    """
    Calls the put method in the specified url with the specified payload
    :param context: The working context
    :param url: The url to put
    :param data: The payload
    :param check_response_code: Verifies with an assert that the response is 200 http (default:True)
    :param check_message: Checks for the specified message in the response (default: None)
    :return: It stores the response in the variable in the api context, it can be obtained with get_last_response method
    """
    erase_last_response(context)
    response = requests.put(url, data)
    set_api_response(context, response)
    if check_response_code:
        assert response.status_code == 200, "Error, status code is {code}, expected 200. The error is {error}".format(code=response.status_code, error=response.text)
    if check_message != None:
        check_response_message(response, check_message)

def check_response_message(api_object, message):
    """
    Verifies that the message is present in the api object
    :param api_object: The api object
    :param message: The message to check
    :return: Nothing, it throws an exception
    """
    if api_object.json()[message] != True:
        assert False, "ERROR, API error. Response {response}".format(response=api_object.json()['error'])