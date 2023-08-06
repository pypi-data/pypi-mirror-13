*** Settings ***
Library  Selenium2Library

Documentation  GP robot framework common keywords.

*** Keywords ***
elements should be visible
    [Documentation]  Waits for visibility of first element, then checks visibility of all elements found by xpath.
    ...  DO NOT use xpath= as an argument for this keyword.
    ...  Waits 8 seconds by default and can be changed by time_to_wait.
    ...
    ...  Usage:
    ...  | elements should be visible | //div[@class='data'] |

    [Arguments]  ${xpath}  ${time_to_wait}=8

    wait until element is visible  ${xpath}  ${time_to_wait}
    ${amount_of_items}  get matching xpath count  ${xpath}
    should not be equal as integers  0  ${amount_of_items}

    :FOR  ${number}  IN RANGE  1  ${amount_of_items}+1
    \    element should be visible  xpath=(${xpath})[${number}]

click visible element
    [Documentation]  Waits for an element to be visible, then clicks on it.
    ...  Waits 8 seconds for visibility of element by default. Can be changed by time_to_wait.
    ...
    ...  Usage:
    ...  | click visible element | //div[@class='test-class'] |

    [Arguments]  ${xpath}  ${time_to_wait}=8
    wait until element is visible  ${xpath}  ${time_to_wait}
    click element  ${xpath}

click element via javascript
    [Documentation]  Clicks an element with use of javascript instead of Robot Framework's built in keyword.
    ...  DO NOT USE #some_id as a selector, rather use [id=some_id].
    ...
    ...  Usage:
    ...  | click element via javascript | .article:first |

    [Arguments]  ${css_selector}
    execute javascript  var clickEvent = new MouseEvent("click",{"view":window,"bubbles":true,"cancelable":false});$("${css_selector}")[0].dispatchEvent(clickEvent);

click
    [Documentation]  Wait for visibility of element and then focus it, after that click on it.
    ...  Waits 8 seconds for visibility of element by default. Can be changed by time_to_wait.
    ...
    ...  Usage:
    ...  | click | //div[@class='test']

    [Arguments]  ${element}  ${time_to_wait}=8
    wait until element is visible  ${element}  ${time_to_wait}
    focus  ${element}
    click element  ${element}

close and select window
    [Documentation]  Close current window and then select previous window.
    ...  You can optionally pass variable to select different window.
    ...
    ...  Usage:
    ...  | close and select window | url=http://google.com |
    ...  | close and select window | title=My Document |

    [Arguments]  ${window}=None
    ${rawNone}  evaluate  None
    ${window}  set variable if  '${window}'=='None'  ${rawNone}
    close window
    select window  ${window}

get xpath element index
    [Documentation]  Get index of an xpath element within it's parent node.
    ...  Say we have the following structure:
    ...
    ...  <div class="main_section">
    ...     <div class="data">Some text</div>
    ...     <div class="data">Some other text</div>
    ...     <div class="data">Even different text</div>
    ...  </div>
    ...
    ...  div with "Some text" has the index of 1
    ...  div with "Some other text" has the index of 2
    ...  etc.
    ...
    ...  xpath argument is xpath of element you want to find out index of.
    ...  sibling_nodes argument is sibling nodes of your xpath element (in this case it's div)
    ...
    ...  Usage:
    ...  | get xpath element index | //div[@class='main_section']/div[contains(text(), 'Some text')] | div |

    [Arguments]  ${xpath}  ${sibling_nodes}
    wait until page contains element  ${xpath}
    ${precedingSiblings}  get matching xpath count  ${xpath}/preceding-sibling::${sibling_nodes}
    [Return]  ${precedingSiblings}+1
