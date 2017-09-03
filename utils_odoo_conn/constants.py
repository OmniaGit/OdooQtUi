'''
Created on 17 Feb 2017

@author: dsmerghetto
'''
# Form color
#old_violet = #875a7b
VIOLET_BACKGROUND = 'background-color:#875a7b;'
BACKGROUND_RED = 'background-color:#f7a5a5;'
BACKGROUND_WHITE = 'background-color:white;'
BACKGROUND_GREY = 'background-color:#dfd9d9;'
BACKGROUND_LIGHT_BLUE = 'background-color: #cdd6fc;'
READONLY_STYLE = 'background-color:#ebebeb;'
COMMON_FIELDS_REQUIRED_BACKGROUND = 'background-color: rgb(210,210,255)'


BOLD_FONT = 'font-weight: bold;'
COMMON_FIELDS_BORDER = 'border: 2px solid #cfcfcf;'
NO_RIGHT_BORDER = 'border-right-style: none;'
NO_LEFT_BORDER = 'border-left-style: none;'
NO_TOP_BORDER = 'border-top-style: none;'
COMMON_FIELDS_BOTTOM_BORDER = COMMON_FIELDS_BORDER + NO_RIGHT_BORDER + NO_LEFT_BORDER + NO_TOP_BORDER


BUTTON_COMMON = 'border-radius: 0px;border: none;color: white;padding: 5px 10px;font-size: 12px;'
BUTTON_STYLE = 'background-color: #21b799;border-color: #21b799;' + BOLD_FONT + BUTTON_COMMON
BUTTON_STYLE_OK = 'background-color: #59be50;border-color: #21b799;' + BUTTON_COMMON
BUTTON_STYLE_CANCEL = ';background-color: #f05050;border-color: #21b799;' + BUTTON_COMMON
BUTTON_STYLE_MANY_2_ONE = 'background-color: #3eb2df;border-color: #21b799;max-width:30px;max-height:10px;' + BOLD_FONT + BUTTON_COMMON
BUTTON_ADD_AN_ITEM = 'border: none;color:blue;background-color:white;' + BOLD_FONT
LABEL_STYLE = 'margin-right: 0px;font-size: 12px;line-height: 1.42857143;' + BOLD_FONT
LABEL_STYLE_STATUSBAR = 'background-color: grey;color:white;max-width:100px;border: 0.1px solid white;border-bottom-right-radius: 10px;border-top-right-radius: 10px;'
LABEL_STYLE_STATUSBAR_ACTIVE = LABEL_STYLE_STATUSBAR + 'background-color:blue;'
LABEL_SEPARATOR = LABEL_STYLE + 'font-size:14px;' + BOLD_FONT
MANY_2_MANY_H_HEADER = 'vertical-align: middle;color:black;background-color:#dfdfdf;' + BOLD_FONT
CHAR_STYLE = COMMON_FIELDS_BOTTOM_BORDER
FLOAT_STYLE = COMMON_FIELDS_BOTTOM_BORDER
INTEGER_STYLE = COMMON_FIELDS_BOTTOM_BORDER
SELECTION_STYLE = COMMON_FIELDS_BOTTOM_BORDER
DATE_STYLE = COMMON_FIELDS_BOTTOM_BORDER
TEXT_STYLE = BACKGROUND_WHITE
NOOTEBOOK_STYLE = 'border-left-style: none;border-right-style: none;border-bottom-style: none;border-top-style: none;'
NOOTEBOOK_TABBAR_STYLE = 'QTabBar::tab:!selected {border: 3px solid grey;border-left-style: none;border-right-style: none;border-top-style: none;min-width:180px;} QTabBar::tab:selected {border: 3px solid #875a7b;border-left-style: none;border-right-style: none;border-top-style: none;color: #875a7b;font-size: 12px;min-width:150px} QTabBar::tab:hover {border: 3px solid #875a7b;border-left-style: none;border-right-style: none;border-top-style: none;color: #875a7b;font-size: 12px;font-weight: bold;min-width:150px}'
TABLE_LIST_LIST = """QScrollBar {background-color:#875a7b} QTableWidget {border-left: 3px solid #875a7b; border-right: 3px solid #875a7b; border-bottom: 3px solid #875a7b;}"""
FONT_SIZE_LIST_WIDGET = 8

TAG_TEXT_STYLE = 'background-color: #c5c5c5;color: black;padding: 0px 5px 0px 5px;font-size: large;max-width: 500px;border: 1px solid black;'
TAG_BUTTON_STYLE = 'color: black;margin-left:20px;display: flex;padding: 0px 5px 0px 0px;font-size: large;background-color:#3eb2df' + BOLD_FONT



# Search view
SEARCH_FILTER_TOOLBUTTON = 'background-color: #7c7bad;min-width: 130px;min-height:30px;color: white;font-size: large;border: 3px solid black;' + BOLD_FONT
SEARCH_ADVANCED_BUTTON = 'background-color:white;color:#875a7b;font-size: 18px;border: 4px solid #875a7b;min-width: 25px;min-height:25px;' + BOLD_FONT
OPERATOR_LABEL = 'background-color: #7c7bad;border: 1px solid black;width:30px;color:white;'

# Login dialog
LOGIN_LINEEDIT_STYLE = 'min-width:200px;height: 16px;padding: 6px 12px;font-size: 14px;border: 1px solid #ccc;border-radius: 4px;background-color: rgb(250, 255, 189);color: rgb(0, 0, 0);'
LOGIN_COMBO_STYLE = 'QComboBox {background-color: #eee;color: rgb(0, 0, 0);height: 16px;padding: 6px 12px;font-size: 14px;border-radius: 4px;border: 1px solid #ccc;} QScrollBar {background-color:#875a7b} '
LOGIN_ACCEPT_BUTTON = 'border-radius: 4px;color: white;background-color: #337ab7;border: 2px solid black;padding: 5px 10px;font-size: 12px;'
LOGIN_NEXT_BACK_BUTTONS = LOGIN_ACCEPT_BUTTON + 'background-color: #59be50;'
LOGIN_CANCEL_BUTTON = LOGIN_ACCEPT_BUTTON + 'background-color: #f05050;'
LOGIN_LABEL = BOLD_FONT
LOGIN_MAIN = 'background-color:#875a7b;'
LOGIN_STACKED_WIDGET = 'background-color:white;'

TREE_LIST_BACKGROUND_COLOR = 'background-color:#ffffff;'

