'''
Created on 17 Feb 2017

@author: dsmerghetto
'''
FONT_SIZE = 'font-size: 14px;'
# Form color
VIOLET_BACKGROUND = 'background-color:#875a7b;'
LOGIN_MAIN = VIOLET_BACKGROUND
BACKGROUND_RED = 'background-color:#94313d;'
BACKGROUND_WHITE = 'background-color:white;'
BACKGROUND_GREY = 'background-color:#dfd9d9;'
BACKGROUND_LIGHT_BLUE = 'background-color: #cdd6fc;'
READONLY_STYLE = 'background-color:#ebebeb;'
COMMON_FIELDS_REQUIRED_BACKGROUND = 'background-color: rgb(210,210,255)'
LAY_OUT_SPACING = 6

COLOR_WHITE = 'color:white;'
BOLD_FONT = 'font-weight: bold;'
COMMON_FIELDS_BORDER = 'border: 2px solid #cfcfcf;'
NO_RIGHT_BORDER = 'border-right-style: none;'
NO_LEFT_BORDER = 'border-left-style: none;'
NO_TOP_BORDER = 'border-top-style: none;'
COMMON_FIELDS_BOTTOM_BORDER = COMMON_FIELDS_BORDER + NO_RIGHT_BORDER + NO_LEFT_BORDER + NO_TOP_BORDER
MAIN_STYLE = 'background-color:#ffffff;'
FONT_COLOR_WHITE = 'font-color:black;'

BUTTON_ODOO_DEFAULT_COLOR = 'background-color: #00A09D;'
BUTTON_COMMON = 'border-radius: 0px;border: none;color: white;padding: 5px 10px;' + FONT_SIZE
BUTTON_STYLE = 'background-color: white;border-color: #21b799;' + BOLD_FONT + FONT_COLOR_WHITE  # Color green
BUTTON_STYLE_HOVER = 'background-color: #21b780;border-color: #21b799;' + BOLD_FONT + BUTTON_COMMON  # Color green
BUTTON_STYLE_REVERSED = 'background-color: #000000; color: #ffffff; border-radius: 10px; padding: 4px 10px; font-weight: bold; border: none; margin: 1px;'
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
MANY_2_MANY_H_HEADER = '::section {color:#000000;padding:6px 8px;background-color:#eef0f1;text-align:left;border:none;border-bottom:2px solid #a8aab0;%s}' % BOLD_FONT
TABLE_LIST_LIST = """QScrollBar:horizontal {
    background-color: #e4e4e6;
    border-top: 1px solid #c7ccd1;
    height: 12px;
}
QScrollBar::handle:horizontal {
    background-color: #FF0505;
    border: 1px solid #8B0000;
    border-radius: 0px;
    min-width: 20px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal, QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
    width: 0px;
    height: 0px;
}
QScrollBar:vertical {
    background-color: #e4e4e6;
    border-left: 1px solid #c7ccd1;
    width: 12px;
}
QScrollBar::handle:vertical {
    background-color: #FF0505;
    border: 1px solid #8B0000;
    border-radius: 0px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical, QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
    width: 0px;
    height: 0px;
}
QTableWidget {border: 2px solid #2c2c2c;
                border-radius: 6px;
                alternate-background-color: #f2f2f3;
                background-color: white;
                font-size:12px;}
QTableWidget::item {
    padding: 4px 8px;
}
QTableWidget::item:hover {
    background-color: #f3f4f6;
    color: #000000;
}
QTableWidget::item:selected, QTableWidget::item:focus, QTableWidget::item:active {
    background-color: transparent;
    color: #000000;
    outline: none;
}
"""
TABLE_VIEW_LIST_LIST = """QTreeView {border: 2px solid #2c2c2c;
                border-radius: 6px;
                alternate-background-color: #f2f2f3;
                background-color: white;
                font-size:14px;}
QTreeView::item {
    padding: 4px 8px 4px 0px;
}
QTreeView::item:hover {
    background-color: #f3f4f6;
    color: #000000;
}
QTreeView::item:selected, QTreeView::item:focus, QTreeView::item:active {
    background-color: transparent;
    color: #000000;
    outline: none;
}
"""
# #167F92
# hover
# QTableWidget::item::hover {
# color:white;background-color:#167F92;
FONT_SIZE_LIST_WIDGET = "12px"

TAG_TEXT_STYLE = 'background-color: #c5c5c5;color: black;padding: 0px 5px 0px 5px;max-width: 500px;border: 1px solid black;' + FONT_SIZE
TAG_BUTTON_STYLE = 'color: black;margin-left:20px;display: flex;padding: 0px 5px 0px 0px;background-color:#3eb2df' + BOLD_FONT + FONT_SIZE
# Search view
# Shared by "Filters" (QToolButton) and "Advanced Filter" (QPushButton), hence the
# universal "*" selector so :hover/:pressed apply to both widget types.
SEARCH_FILTER_TOOLBUTTON = ('* {'
    'background-color: #a8aab0;'
    'color: #000000;'
    'min-width: 130px;'
    'min-height: 25px;'
    'border: 2px solid #7d7f85;'
    'border-radius: 12px;'
    '%s%s'
    '}'
    '*:hover {'
    'background-color: #b5b7bc;'
    'border: 2px solid #65676c;'
    '}'
    '*:pressed {'
    'background-color: #7d7f85;'
    'border: 2px solid #5a5c61;'
    '}') % (BOLD_FONT, FONT_SIZE)
SEARCH_ADVANCED_BUTTON = ('QPushButton {'
    'background-color: #a8aab0;'
    'color: #000000;'
    'width: 25px;'
    'min-height: 25px;'
    'border: 2px solid #7d7f85;'
    'border-radius: 12px;'
    '%s%s'
    '}'
    'QPushButton:hover {'
    'background-color: #b5b7bc;'
    'border: 2px solid #65676c;'
    '}'
    'QPushButton:pressed {'
    'background-color: #7d7f85;'
    'border: 2px solid #5a5c61;'
    '}') % (BOLD_FONT, FONT_SIZE)
# Flat mid-gray pill style shared by the "Or" / "Apply" / "X" condition buttons
SEARCH_OR_BUTTON = ('QPushButton {'
    'background-color: #a8aab0;'
    'color: #000000;'
    'min-height: 25px;'
    'border: 2px solid #7d7f85;'
    'border-radius: 12px;'
    'padding: 2px 14px;'
    '%s%s'
    '}'
    'QPushButton:hover {'
    'background-color: #b5b7bc;'
    'border: 2px solid #65676c;'
    '}'
    'QPushButton:pressed {'
    'background-color: #7d7f85;'
    'border: 2px solid #5a5c61;'
    '}') % (BOLD_FONT, FONT_SIZE)

SEARCH_APPLY_BUTTON = ('QPushButton {'
    'background-color: #22c55e;'
    'color: #ffffff;'
    'min-height: 25px;'
    'border: 2px solid #16a34a;'
    'border-radius: 12px;'
    'padding: 2px 14px;'
    '%s%s'
    '}'
    'QPushButton:hover {'
    'background-color: #16a34a;'
    'border: 2px solid #15803d;'
    '}'
    'QPushButton:pressed {'
    'background-color: #15803d;'
    '}') % (BOLD_FONT, FONT_SIZE)

SEARCH_REMOVE_BUTTON = ('QPushButton {'
    'background-color: #ef4444;'
    'color: #ffffff;'
    'min-height: 25px;'
    'border: 2px solid #dc2626;'
    'border-radius: 12px;'
    'padding: 2px 10px;'
    '%s%s'
    '}'
    'QPushButton:hover {'
    'background-color: #dc2626;'
    'border: 2px solid #b91c1c;'
    '}'
    'QPushButton:pressed {'
    'background-color: #b91c1c;'
    '}') % (BOLD_FONT, FONT_SIZE)

BUTTON_STYLE_OK = SEARCH_APPLY_BUTTON
BUTTON_STYLE_CANCEL = SEARCH_REMOVE_BUTTON

OPERATOR_LABEL = 'background-color: #000000;border: 1px solid black;width:30px;color:white;'
# Advanced Filter dialog (kept separate from LOGIN_* so the login screen is untouched)
ADV_FILTER_COMBO_STYLE = ('QComboBox {background-color: #ffffff;color: #000000;padding: 4px 8px;'
    'min-height: 20px;border-radius: 4px;border: 2px solid #7d7f85;} '
    'QComboBox QAbstractItemView {background-color: #ffffff;color: #000000;'
    'selection-background-color: #a8aab0;selection-color: #000000;} '
    'QScrollBar:vertical {background-color:#e4e4e6; width: 8px;} '
    'QScrollBar::handle:vertical {background-color:#FF0505; border: 1px solid #8B0000;}')
ADV_FILTER_LINEEDIT_STYLE = ('min-width:200px;height: 16px;padding: 6px 12px;border: 2px solid #7d7f85;'
    'border-radius: 4px;background-color: #ffffff;color: #000000;' + FONT_SIZE)
ADV_FILTER_ACTION_BUTTON = ('border-radius: 12px;color: #000000;background-color: #a8aab0;'
    'border: 2px solid #7d7f85;padding: 5px 14px;font-weight: bold;' + FONT_SIZE)
ADV_FILTER_CANCEL_BUTTON = ('border-radius: 12px;color: #ffffff;background-color: #8B0000;'
    'border: 2px solid #5a5c61;padding: 5px 14px;font-weight: bold;' + FONT_SIZE)
ADV_FILTER_ROW_BACKGROUND = 'background-color: #eef0f1;'
# Login dialog
LOGIN_LINEEDIT_STYLE = 'min-width:200px;height: 16px;padding: 6px 12px;border: 1px solid #ccc;border-radius: 4px;background-color: rgb(250, 255, 189);color: rgb(0, 0, 0);' + FONT_SIZE
LOGIN_COMBO_STYLE = 'QComboBox {background-color: #ffffff;color: rgb(0, 0, 0);padding: 4px 8px;min-height: 20px;border-radius: 4px;border: 1px solid #ccc;} QComboBox QAbstractItemView {background-color: #ffffff;color: #000000;selection-background-color: #ef4444;selection-color: #ffffff;} QScrollBar:vertical {background-color:#fee2e2; width: 8px;} QScrollBar::handle:vertical {background-color:#ef4444; border-radius: 3px;}'
LOGIN_ACCEPT_BUTTON = 'border-radius: 4px;color: white;background-color: #337ab7;border: 2px solid black;padding: 5px 10px;' + FONT_SIZE
LOGIN_NEXT_BACK_BUTTONS = LOGIN_ACCEPT_BUTTON + 'background-color: #59be50;'
LOGIN_CANCEL_BUTTON = LOGIN_ACCEPT_BUTTON + 'background-color: #a30e0e;'
LOGIN_LABEL = BOLD_FONT
LOGIN_STACKED_WIDGET = 'background-color:white;'

TREE_LIST_BACKGROUND_COLOR = 'background-color:#ffffff;'

DEBUG = False

# ODOO_STYLE ="""
# QDialog {{background-color:#875a7b;}}
# QPushButton {{{push_button}}}
# QPushButton:hover {{{push_button_hover}}}
# QTreeView {{border-left: 3px solid #875a7b;
#                 border-right: 3px solid #875a7b;
#                 border-bottom: 3px solid #875a7b;
#                 alternate-background-color: #DDEDF0;
#                 background-color: white;
#                 font-size:16px;}}
#
# """.format(push_button=BUTTON_STYLE,
#            push_button_hover=BUTTON_STYLE_REVERSED)

ODOO_STYLE = """QDialog {border-radius: 5px;
                         color: #875a7b;
                        background-color:  #A583A5;
                        }
                            QProgressBar{text-align: center;
                                         border-radius: 5px;  
                                         border: 1px solid grey; 
                                         }
                            QProgressBar::chunk {background-color:  #9d5e96;
                                                color:white;
                                                border: 1px solid grey;
                                                }
                            QScrollBar::handle:horizontal {
                                color:  #9d5e96;
                            }
                            QScrollBar::handle:vertical {
                                color: #9d5e96;
                            }  
                            QTreeView {
                                alternate-background-color: #DDEDF0;
                                background-color: solid grey;
                                font-size:12px;
                                icon-size: 16px;
                            }     
                        """
