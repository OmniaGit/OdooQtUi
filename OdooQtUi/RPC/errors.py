# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""What a failed call to Odoo raises.

The RPC layer used to open a modal dialog itself and answer None: a script
without a display waited for ever, ten failing fields opened ten dialogs, and
the caller carried on with a None it could not tell from "nothing found". Now
it raises one of these, and shows nothing. A window is the business of the code
the user acted through -- see utilsUi.rpcErrorBoundary and showRpcError.

    try:
        connector.rpc_connector.write('res.partner', {'name': ''}, [7])
    except OdooServerError as error:
        print(error.summary)            # what Odoo said, in one line

Nothing here imports Qt.
"""


class OdooRpcError(Exception):
    """A call to Odoo that did not answer.

    :model       the model called, e.g. 'res.partner'
    :method      the method called, e.g. 'write'
    :faultCode   and faultString as xmlrpc.client.Fault names them, so the code
                 that already reads a Fault reads this too
    """

    def __init__(self, message, model='', method='', faultCode='', faultString=''):
        super(OdooRpcError, self).__init__(message)
        self.model = model
        self.method = method
        self.faultCode = faultCode
        self.faultString = faultString or message

    @property
    def summary(self):
        """The last line that says something: the error itself, not its traceback."""
        lines = [line.strip() for line in str(self.faultString).splitlines() if line.strip()]
        return lines[-1] if lines else str(self)

    def __str__(self):
        where = '%s.%s' % (self.model, self.method) if self.model else self.method
        message = super(OdooRpcError, self).__str__()
        return '%s: %s' % (where, message) if where else message


class OdooServerError(OdooRpcError):
    """Odoo received the call and refused it: a UserError, an AccessError, a bug."""


class OdooConnectionError(OdooRpcError):
    """The call did not reach Odoo, or its answer did not come back."""
