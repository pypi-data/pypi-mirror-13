NAME
    rest_api_basic_helpers

FUNCTIONS
    check_response_message(api_object, message)
        Verifies that the message is present in the api object
        :param api_object: The api object
        :param message: The message to check
        :return: Nothing, it throws an exception

    delete_method(context, url, check_response_code=True, check_message=None)
        Calls the method delete in the specified url
        :param context: The working context
        :param url: The url to delete
        :param check_response_code: Verifies with an assert that the response is 200 http (default:True)
        :param check_message: Checks for the specified message in the response (default: None)
        :return: It stores the response in the variable api context, it can be obtained with get_last response method

    erase_last_response(context)
        Erase the content of the env variable for api responses (used by API methods)
        :param context: The working context
        :return: Nothing, it sets the variable an empty string value

    get_last_response(context)
        Returns the last response stored in the variable (used by API methods)
        :param context: The working context
        :return: The last response

    get_method(context, url, check_response_code=True, check_message=None)
        Calls the get method in the specified url
        :param context: The working context
        :param url: The url to get
        :param check_response_code: Verifies with an assert that the response is 200 http (default:True)
        :param check_message: Checks for the specified message in the response (default: None)
        :return: It stores the response in the variable in the api context, it can be obtained with get_last_response method

    post_method(context, url, data, check_response_code=True, check_message=None)
        Calls the post method in the specified url with the specified payload
        :param context: The working context
        :param url: The url to post
        :param data: The payload
        :param check_response_code: Verifies with an assert that the response is 200 http (default:True)
        :param check_message: Checks for the specified message in the response (default: None)
        :return: It stores the response in the variable in the api context, it can be obtained with get_last_response method

    put_method(context, url, data, check_response_code=True, check_message=None)
        Calls the put method in the specified url with the specified payload
        :param context: The working context
        :param url: The url to put
        :param data: The payload
        :param check_response_code: Verifies with an assert that the response is 200 http (default:True)
        :param check_message: Checks for the specified message in the response (default: None)
        :return: It stores the response in the variable in the api context, it can be obtained with get_last_response method

    set_api_response(context, response)
        Set a value to the env variable for the last api response (used by API methods)
        :param context: The working context
        :param response: The last response
        :return: Nothing, it sets the response in the variable


NAME
    selenium_basic_helpers


FUNCTIONS
    find_element(context, element, identifier, timeout=5.0)
        Looks for a single web element in the page.
        :param context: the behave context variable.
        :param element: the element value to find.
        :param identifier: search by 'css_selector', 'id', 'name' or 'class_name'.
        :param timeout: optional parameter. Retries the search until n seconds (float).
        :return: selenium web element.

    find_elements(context, selector, timeout=10)
        Looks for a group of elements in the page.
        :param context: the behave context variable.
        :param selector: the css selector value to find.
        :param timeout: optional parameter. Retries the search until n seconds (float).
        :return: List of selenium web elements if found. If not elements found it will return an empty list.

    scroll_element_into_view(driver, element)
        Scrolls to an element.
        :param driver: the behave context.
        :param element: the web element object.
        :return: nothing.

    take_snapshot(context, output_format, text)
        Takes an snapshot. It will be stored in a html file if the format is base64 or in a separate png file. The output directory will be snapshots.
        :param context: The behave context.
        :param output:format (base64 will add it to html file, or file to create a png file)
        :param text:label for base64, part of the file name in the case of file

    wait_for_element_to_appear(context, selector, timeout)
        Wait the specified amount of time until the element appears.
        :param context: the behave context variable.
        :param selector: css_selector corresponding to the element.
        :param timeout: time to wait until the element appears.
        :return: Nothing, if the element does not appear in the specified time then an exception is raised.

    wait_for_element_to_disappear(context, selector, identifier, timeout=10.0)
        Wait n seconds until the specified element dissapears.
        :param context: the behave context variable.
        :param selector: the element value to find.
        :param identifier: search by 'css_selector', 'id', 'name' or 'class_name'.
        :param timeout: Optional. time to wait until the element dissapears.
        :return: True if the element dissapears. An exception is raised if the element does not dissapear.


SELENIUM BASE STEPS:
******************* WHEN STEPS *****************
when('take screenshot as {output_format} and show description {text}')

when('opening the url {url}')

when('I refresh the page')

when('I scroll down element {element_selector} {times} times')

when('hover on element {element} identified by {identifier}')

when('back to the previous page')

when('fill input field {field_name}, identified by {identifier} with the value {value}')

when('fill select field {field_name}, identified by {identifier} with the value {value}')

when('click on button {button_name} identified by {identifier}')

when('click in {section} identified by {identifier}')

when('move to element {element}, identified by {identifier}')

when('select option {option} in combobox {element}, identified by {identifier}')

when('hovering {selector}')

when('clicking {selector}')

when('click in link with text {text}')

when('uploading {image} to {selector}')

when('upload the video {video} to {selector}')

when('send key {key} to {selector}')

when('typing {value} in {selector}')

when('selecting {option} in {selector}')

when('drag element {source_element} into {target_element}')

when('drag element {source_element} to positions x {x} and y {y}')


******************* THEN STEPS *****************

then("wait for element {element} identified by {identifier}")

then("check that the element {element} disappears, identified by {identifier}")

then("the page contains the text {expected}")

then("the page title must be {expected}")

then("the login error message appears saying {error_message}")

then("check that the combo button {combo_button} is selected")

then("check that the element {selector} is not present")

then("the text {text} is present in the element {element} identified by {identifier}")

then("the input field {input_field_element} contains the value {value} identified by {identifier}")

then("check that the element {element} is displayed, identified by {identifier}")

then("wait until the element {element} is displayed, identified by {identifier}")

then("expect {selector} to contain {text}")

then("expect {selector} to have the value {text}")

then("expect {selector} to disappear within {timeout} seconds")

then("expect {selector} to disappear")

then("allow time to update the UI")

then("wait up to {timeout} seconds for {selector}")

then("expect {selector} to have {option} selected")

then("wait for element {selector} to be clickable")

then("check that the combobox element {selector} selected value is {value}")

then("expect {selector}")

then("wait for {selector}")