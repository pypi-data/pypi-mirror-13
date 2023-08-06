"""
Widgets for parameters and attributes
"""

# Standard library modules.

# Third party modules.
from qtpy.QtGui import \
    QRegExpValidator, QValidator
from qtpy.QtWidgets import \
    QWidget, QLineEdit, QPushButton, QVBoxLayout, QFormLayout
from qtpy.QtCore import QRegExp, Signal

import six

# Local modules.
from pyhmsa.type.numerical import convert_value
from pyhmsa.type.unit import validate_unit
from pyhmsa.util.element_properties import get_symbol, get_atomic_number

from pyhmsa.gui.util.periodictable import PeriodicTableDialog

from pyhmsa.gui.util.human import camelcase_to_words

# Globals and constants variables.

class _ParameterAttributeMixin(object):

    def __init__(self):
        self._attribute = None

    def parameterAttribute(self):
        return self._attribute

    def setParameterAttribute(self, attribute):
        self._attribute = attribute
        self.setAccessibleName(attribute.name)
        self.setToolTip(attribute.__doc__.title())

class _ParameterAttributeLineEdit(QLineEdit, _ParameterAttributeMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setParameterAttribute(self, attribute):
        _ParameterAttributeMixin.setParameterAttribute(self, attribute)

        if attribute.is_required():
            pattern = QRegExp(r"^(?!\s*$).+")
            validator = QRegExpValidator(pattern)
            self.setValidator(validator)

        self.textChanged.connect(self._onTextChanged)
        self.textChanged.emit('')

    def _onTextChanged(self):
        if self.hasAcceptableInput():
            self.setStyleSheet("background: none")
        else:
            self.setStyleSheet("background: pink")

class TextAttributeLineEdit(_ParameterAttributeLineEdit):

    def __init__(self, attribute, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setParameterAttribute(attribute)

    def text(self):
        text = _ParameterAttributeLineEdit.text(self)
        if len(text.strip()) == 0:
            return None
        return text

    def setText(self, text):
        if text is None:
            text = ''
        return _ParameterAttributeLineEdit.setText(self, text)

class NumericalAttributeLineEdit(_ParameterAttributeLineEdit):

    class _Validator(QValidator):

        def __init__(self, attribute):
            QValidator.__init__(self)
            self._attribute = attribute

        def validate(self, text, pos):
            parts = text.split()
            if len(parts) == 0:
                if self._attribute.is_required():
                    return (QValidator.Intermediate, text, pos)
                else:
                    return (QValidator.Acceptable, text, pos)

            elif len(parts) == 1:
                try:
                    float(parts[0])
                except ValueError:
                    return (QValidator.Intermediate, text, pos)
                else:
                    return (QValidator.Acceptable, text, pos)

            elif len(parts) == 2:
                try:
                    float(parts[0])
                    validate_unit(parts[1])
                except ValueError:
                    return (QValidator.Intermediate, text, pos)
                else:
                    return (QValidator.Acceptable, text, pos)

            else:
                return (QValidator.Invalid, text, pos)

        def fixup(self, text):
            return text

    def __init__(self, attribute, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setParameterAttribute(attribute)

        self._format = '{0:g}'

        self.setValidator(self._Validator(attribute))

        tooltip = attribute.__doc__.title()
        if attribute.default_unit is not None:
            tooltip += ' (default unit: %s)' % attribute.default_unit
        self.setToolTip(tooltip)

        self.editingFinished.connect(self._onEditingFinished)

    def _onEditingFinished(self):
        if not self.hasAcceptableInput():
            return
        self.setText(self.text())

    def _parse(self, text):
        parts = text.split()
        if len(parts) == 0:
            value = unit = None
        elif len(parts) == 1:
            value = float(parts[0])
            unit = None
        elif len(parts) == 2:
            value = float(parts[0])
            unit = parts[1]

        return convert_value(value, unit or self._attribute.default_unit)

    def format(self):
        return self._format

    def setFormat(self, fmt):
        self._format = fmt

    def text(self):
        if not self.hasAcceptableInput():
            raise ValueError('Invalid text')
        return self._parse(_ParameterAttributeLineEdit.text(self))

    def setText(self, value):
        if isinstance(value, six.string_types):
            value = self._parse(value)

        if value is None:
            return _ParameterAttributeLineEdit.setText(self, '')

        text = self._format.format(value)
        unit = getattr(value, 'unit', None)
        if unit is not None:
            text += ' ' + unit

        return _ParameterAttributeLineEdit.setText(self, text)

class UnitAttributeLineEdit(_ParameterAttributeLineEdit):

    class _Validator(QValidator):

        def __init__(self, attribute, valid_units=None):
            QValidator.__init__(self)
            self._attribute = attribute
            self._valid_units = valid_units

        def validate(self, text, pos):
            if not text:
                if self._attribute.is_required():
                    return (QValidator.Intermediate, text, pos)
                else:
                    return (QValidator.Acceptable, text, pos)

            try:
                validate_unit(text)
            except ValueError:
                return (QValidator.Intermediate, text, pos)

            if self._valid_units is not None and \
                    text not in self._valid_units:
                return (QValidator.Intermediate, text, pos)

            return (QValidator.Acceptable, text, pos)

        def fixup(self, text):
            return text

    def __init__(self, attribute, valid_units=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setParameterAttribute(attribute)

        self.setValidator(self._Validator(attribute, valid_units))

    def text(self):
        text = _ParameterAttributeLineEdit.text(self)
        if len(text.strip()) == 0:
            return None
        return text

    def setText(self, text):
        if text is None:
            text = ''
        return _ParameterAttributeLineEdit.setText(self, text)

class AtomicNumberAttributePushButton(QPushButton, _ParameterAttributeMixin):

    selectionChanged = Signal()

    def __init__(self, attribute, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setParameterAttribute(attribute)

        self.setText(str(None))

        self.clicked.connect(self._onClick)

    def _onClick(self):
        dialog = PeriodicTableDialog(self.parent())
        dialog.setMultipleSelection(False)
        dialog.setRequiresSelection(False)

        symbol = self.text()
        if symbol == str(None):
            symbol = None
        dialog.setSelection(symbol)

        if dialog.exec_():
            newsymbol = str(dialog.selectionSymbol())
            self.setText(newsymbol)

            if newsymbol != symbol:
                self.selectionChanged.emit()

    def hasAcceptableInput(self):
        return self.text() != str(None)

    def setAtomicNumber(self, z):
        self.setText(get_symbol(z))

    def atomicNumber(self):
        symbol = self.text()
        if symbol == str(None):
            return None
        return get_atomic_number(symbol)

class ParameterWidget(QWidget):

    edited = Signal()

    def __init__(self, clasz, parent=None):
        super().__init__(parent)
        self.setAccessibleName(' '.join(camelcase_to_words(clasz.__name__)))

        # Variable
        self._class = clasz

        # Layout
        layout = QVBoxLayout()
        layout.addLayout(self._init_ui()) # Initialize widgets
        layout.addStretch()
        self.setLayout(layout)

    def _init_ui(self):
        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow) # Fix for Mac OS
        return layout

    def _create_parameter(self):
        return self.CLASS()

    def isReadOnly(self):
        return False

    def setReadOnly(self, state):
        pass

    def hasAcceptableInput(self):
        return True

    def parameter(self, parameter=None):
        if parameter is None:
            parameter = self._create_parameter()
        return parameter

    def setParameter(self, parameter):
        pass

    @property
    def CLASS(self):
        return self._class


