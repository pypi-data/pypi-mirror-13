'''
Provide a series Element Expected Condition Functors

@date 2015-08-03
@author Hong-She Liang <starofrainnight@gmail.com>
'''

# Import all expected conditions from selenium 
from selenium.webdriver.support.expected_conditions import *

class eecf_stale_of(object):
    def __init__(self, check_status):
        self.__check_status = check_status
    
    def __call__(self, element):
        try:
            # Calling any method forces a staleness check
            element.is_enabled()
            return self.__check_status 
        except StaleElementReferenceException:
            return not self.__check_status 
                    
class eecf_visible_of(object):
    def __init__(self, check_status):
        self.__check_status = check_status
    
    def __call__(self, element):    
        try:
            return element.is_displayed() == self.__check_status
        except (NoSuchElementException, StaleElementReferenceException):
            # In the case of NoSuchElement, returns true because the element is
            # not present in DOM. The try block checks if the element is present
            # but is invisible.
            # In the case of StaleElementReference, returns true because stale
            # element reference implies that element is no longer visible.
            return not self.__check_status 
    
class eecf_select_of(object):
    def __init__(self, check_status):
        self.__check_status = check_status
        
    def __call__(self, element):
        return element.is_selected() == self.__check_status
       
class eecf_enable_of(object):
    def __init__(self, check_status):
        self.__check_status = check_status
        
    def __call__(self, element):
        """ Wait until an element is enabled
        returns False otherwise.
        """
        # Calling any method forces a staleness check
        return element.is_enabled() == self.__check_status
    
class MatchedResult(object):
    pass

class match(object):
    """
    Use for wait a series conditions and store them to a named dict.
    
    @code
    matched_elements = WebDriverWait(driver, 10).until(EC.match({
        "checkcode":{"condition":EC.xpath_find("//input[@id='fm-login-checkcode']")},
    }))
    matched_elements.checkcode.clear()
    @endcode
    """
    
    def __init__(self, condition_dict={}, matched_at_least=1):
        self.__condition_dict = condition_dict
        self.__matched_at_least = matched_at_least

    def __call__(self, driver):
        elements = {}
        for k, v in self.__condition_dict.items():
            value = v["condition"](driver)
            if False != value:
                elements[k] = value
            elif ("optional" not in v) or (not v["optional"]):               
                # If optional flag is True and value is False, we return False                
                return False
            
        if len(elements) < self.__matched_at_least:
            return False
        
        result = MatchedResult()
        for k, v in elements.items():
            result.__dict__[k] = v
        
        return result
  
class xpath_find(object):
    def __init__(self, xpath_expr, conditions=[]):
        self.__xpath_expr = xpath_expr
        self.__conditions = conditions

    def __call__(self, driver):
        try:
            return driver.xpath_find(self.__xpath_expr, 
                conditions=self.__conditions)
        except NoSuchElementException:
            # Because wait method will invoke xpath_find() multi-times, 
            # can't find the element is a normal state, so we must not 
            # scare.
            return False        
        except WebDriverException as e:
            if "element is not attached to the page document" in str(e):
                return False
            
            raise
        
class xpath_find_all(object):
    """
    Easily to wait until find all elements recursively.
    
    Example : 
    
    @code
    elements = WebDriverWait(driver, 10).until(EC.xpath_find(
        "//input[@id='fm-login-id']",
        conditions=[eecf_visible_of(True)]))
    @endcode 
    """
    def __init__(self, xpath_expr, conditions=[]):
        self.__xpath_expr = xpath_expr
        self.__conditions = conditions

    def __call__(self, driver):
        elements = driver.xpath_find_all(self.__xpath_expr, 
            conditions=self.__conditions)
        if len(elements) > 0:
            return elements
        else:
            return False

class url_changed(object):
    """
    Wait until webdriver's current url changed
    
    @param url: Original webdriver's current url, normally you should 
    pass the webdriver.current_url.
    """
    def __init__(self, url):
        self.__url = url

    def __call__(self, driver):
        return driver.current_url != self.__url
    
class url_changed_to(object):
    """
    Wait until webdriver's current url changed to specific url
    
    @param url: The target url we need to change to
    """
    def __init__(self, url):
        self.__url = url

    def __call__(self, driver):
        return driver.current_url == self.__url