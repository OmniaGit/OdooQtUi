'''
Created on 17 Feb 2017

@author: dsmerghetto
'''
FONT_SIZE = "font-size: 11px;"
# Form color
VIOLET_BACKGROUND = 'background-color:#875a7b;'
LOGIN_MAIN = VIOLET_BACKGROUND
BACKGROUND_RED = 'background-color:#94313d;'
BACKGROUND_WHITE = 'background-color:white;'
BACKGROUND_GREY = 'background-color:#dfd9d9;'
BACKGROUND_LIGHT_BLUE = 'background-color: #cdd6fc;'
READONLY_STYLE = 'background-color:#ebebeb;'
COMMON_FIELDS_REQUIRED_BACKGROUND = 'background-color: rgb(210,210,255)'
LAY_OUT_SPACING = 4

COLOR_WHITE = 'color:white;'
BOLD_FONT = 'font-weight: bold;'
COMMON_FIELDS_BORDER = 'border: 2px solid #cfcfcf;'
NO_RIGHT_BORDER = 'border-right-style: none;'
NO_LEFT_BORDER = 'border-left-style: none;'
NO_TOP_BORDER = 'border-top-style: none;'
COMMON_FIELDS_BOTTOM_BORDER = COMMON_FIELDS_BORDER + NO_RIGHT_BORDER + NO_LEFT_BORDER + NO_TOP_BORDER
MAIN_STYLE = 'background-color:#ffffff;'

BUTTON_ODOO_DEFAULT_COLOR = 'background-color: #00A09D;'
BUTTON_COMMON = 'border-radius: 0px;border: none;color: white;padding: 5px 10px;' + FONT_SIZE
BUTTON_STYLE = 'background-color: #21b799;border-color: #21b799;' + BOLD_FONT + BUTTON_COMMON   # Color green
BUTTON_STYLE_HOVER = 'background-color: #21b780;border-color: #21b799;' + BOLD_FONT + BUTTON_COMMON   # Color green
BUTTON_STYLE_REVERSED = 'background-color:white; color: #21b799; border: 2px solid #21b799;padding: 3px; margin:1px;' + BOLD_FONT   # Color green
BUTTON_STYLE_OK = 'background-color: #59be50;border-color: #21b799;' + BUTTON_COMMON
BUTTON_STYLE_CANCEL = 'background-color: #f05050;border-color: #21b799;' + BUTTON_COMMON
BUTTON_STYLE_MANY_2_ONE = 'background-color: #3eb2df;border-color: #21b799;max-width:30px;max-height:10px;' + BOLD_FONT + BUTTON_COMMON
BUTTON_STYLE_MANY_2_ONE__2 = 'background-color: #3eb2df;border-color: #21b799;' + BOLD_FONT + BUTTON_COMMON
BUTTON_STYLE_LINK = 'color: #008784;' + BOLD_FONT
BUTTON_ADD_AN_ITEM = 'border: none;color:blue;background-color:white;' + BOLD_FONT
LABEL_STYLE = 'margin-right: 0px;' + BOLD_FONT + FONT_SIZE
LABEL_STYLE_STATUSBAR = 'background-color: grey;color:white;max-width:100px;border: 0.1px solid white;border-bottom-right-radius: 10px;border-top-right-radius: 10px;'
LABEL_STYLE_STATUSBAR_ACTIVE = LABEL_STYLE_STATUSBAR + 'background-color:blue;'
LABEL_SEPARATOR = LABEL_STYLE + FONT_SIZE + BOLD_FONT
CHAR_STYLE = COMMON_FIELDS_BOTTOM_BORDER
FLOAT_STYLE = COMMON_FIELDS_BOTTOM_BORDER
INTEGER_STYLE = COMMON_FIELDS_BOTTOM_BORDER
SELECTION_STYLE = COMMON_FIELDS_BOTTOM_BORDER
DATE_STYLE = COMMON_FIELDS_BOTTOM_BORDER
TEXT_STYLE = BACKGROUND_WHITE
NOOTEBOOK_STYLE = 'border-left-style: none;border-right-style: none;border-bottom-style: none;border-top-style: none;'
NOOTEBOOK_TABBAR_STYLE = 'QTabBar::tab:!selected {border: 3px solid grey;border-left-style: none;border-right-style: none;border-top-style: none;min-width:180px;} QTabBar::tab:selected {border: 3px solid #875a7b;border-left-style: none;border-right-style: none;border-top-style: none;color: #875a7b;' + FONT_SIZE + 'min-width:150px} QTabBar::tab:hover {border: 3px solid #875a7b;border-left-style: none;border-right-style: none;border-top-style: none;color: #875a7b;' + FONT_SIZE + 'font-weight: bold;min-width:150px}'
MANY_2_MANY_H_HEADER = '::section {color:white;padding:3px;background-color:#7C7BAD;text-align:left;border:none;%s}' % BOLD_FONT
TABLE_LIST_LIST = """QScrollBar {background-color:#875a7b}
QTableWidget {border-left: 3px solid #875a7b;
                border-right: 3px solid #875a7b;
                border-bottom: 3px solid #875a7b;
                alternate-background-color: #DDEDF0;
                background-color: white;} 
}
"""
TABLE_VIEW_LIST_LIST = """QTreeView {border-left: 3px solid #875a7b;
                border-right: 3px solid #875a7b;
                border-bottom: 3px solid #875a7b;
                alternate-background-color: #DDEDF0;
                background-color: white;} 
"""
# #167F92
#hover
#QTableWidget::item::hover {
#color:white;background-color:#167F92;
FONT_SIZE_LIST_WIDGET = 8

TAG_TEXT_STYLE = 'background-color: #c5c5c5;color: black;padding: 0px 5px 0px 5px;max-width: 500px;border: 1px solid black;' + FONT_SIZE
TAG_BUTTON_STYLE = 'color: black;margin-left:20px;display: flex;padding: 0px 5px 0px 0px;background-color:#3eb2df' + BOLD_FONT + FONT_SIZE
# Search view
SEARCH_FILTER_TOOLBUTTON = 'background-color: #7c7bad;min-width: 130px;min-height:25px;color: white;' + BOLD_FONT + FONT_SIZE
SEARCH_ADVANCED_BUTTON = 'background-color: #7c7bad;color:white;width: 25px;min-height:25px;%s%s' % (BOLD_FONT, FONT_SIZE)
OPERATOR_LABEL = 'background-color: #7c7bad;border: 1px solid black;width:30px;color:white;'
# Login dialog
LOGIN_LINEEDIT_STYLE = 'min-width:200px;height: 16px;padding: 6px 12px;border: 1px solid #ccc;border-radius: 4px;background-color: rgb(250, 255, 189);color: rgb(0, 0, 0);' + FONT_SIZE
LOGIN_COMBO_STYLE = 'QComboBox {background-color: #eee;color: rgb(0, 0, 0);height: 16px;padding: 6px 12px;' + FONT_SIZE + 'border-radius: 4px;border: 1px solid #ccc;} QScrollBar {background-color:#875a7b} '
LOGIN_ACCEPT_BUTTON = 'border-radius: 4px;color: white;background-color: #337ab7;border: 2px solid black;padding: 5px 10px;' + FONT_SIZE
LOGIN_NEXT_BACK_BUTTONS = LOGIN_ACCEPT_BUTTON + 'background-color: #59be50;'
LOGIN_CANCEL_BUTTON = LOGIN_ACCEPT_BUTTON + 'background-color: #a30e0e;'
LOGIN_LABEL = BOLD_FONT
LOGIN_STACKED_WIDGET = 'background-color:white;'

TREE_LIST_BACKGROUND_COLOR = 'background-color:#ffffff;'

DEBUG = False

ODOO_STYLE ="""
QDialog {{background-color:#875a7b;}}
QPushButton {{{push_button}}}
QPushButton:hover {{{push_button_hover}}}
QTreeView {{border-left: 3px solid #875a7b;
                border-right: 3px solid #875a7b;
                border-bottom: 3px solid #875a7b;
                alternate-background-color: #DDEDF0;
                background-color: white;}} 

""".format(push_button=BUTTON_STYLE,
           push_button_hover=BUTTON_STYLE_REVERSED)
