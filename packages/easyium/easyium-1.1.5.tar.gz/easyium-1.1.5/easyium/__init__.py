try:
    import appium
    appium_installed = True
except ImportError:
    appium_installed = False

from .config import default_config
from .exceptions import EasyiumException, TimeoutException, ElementTimeoutException, WebDriverTimeoutException, \
    NoSuchElementException, NotPersistException, LatePersistException, UnsupportedWebDriverTypeException, \
    InvalidLocatorException, UnsupportedOperationException
from .identifier import Identifier
from .staticelement import StaticElement
from .waiter import Waiter
from .webdriver import WebDriver, WebDriverType, Browser, BrowserType

__author__ = 'karl.gong'
