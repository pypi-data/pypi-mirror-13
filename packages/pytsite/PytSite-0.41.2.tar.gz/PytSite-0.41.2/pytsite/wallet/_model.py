"""PytSite Wallet Package Models.
"""
from datetime import datetime as _datetime
from decimal import Decimal as _Decimal
from pytsite import odm as _odm, odm_ui as _odm_ui, currency as _currency, auth as _auth, auth_ui as _auth_ui, \
    widget as _widget, html as _html
from . import _error, _widget as _wallet_widget

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

_main_currency = _currency.get_main()


class Account(_odm_ui.UIModel):
    """Wallet ODM Model.
    """

    def _setup(self):
        """Hook.
        """
        self._define_field(_odm.field.String('aid', nonempty=True))
        self._define_field(_odm.field.String('currency', nonempty=True))
        self._define_field(_odm.field.String('description'))
        self._define_field(_odm.field.Decimal('balance', round=8))
        self._define_field(_odm.field.Ref('owner', model='user', nonempty=True))
        self._define_field(_odm.field.RefsUniqueList('pending_transactions', model='wallet_transaction'))
        self._define_field(_odm.field.RefsUniqueList('cancelling_transactions', model='wallet_transaction'))
        self._define_field(_odm.field.Dict('options'))

        self._define_index([('aid', _odm.I_ASC)], True)

    @property
    def aid(self) -> str:
        return self.f_get('aid')

    @property
    def currency(self) -> str:
        return self.f_get('currency')

    @property
    def description(self) -> str:
        return self.f_get('description')

    @property
    def balance(self) -> _Decimal:
        return self.f_get('balance')

    @property
    def owner(self) -> _auth.model.User:
        return self.f_get('owner')

    @property
    def pending_transactions(self):
        return self.f_get('pending_transactions')

    @property
    def cancelling_transactions(self):
        return self.f_get('cancelling_transactions')

    @property
    def options(self) -> dict:
        return self.f_get('options')

    def _on_f_set(self, field_name: str, value, **kwargs):
        if field_name == 'currency':
            if value not in _currency.get_all():
                raise _currency.error.CurrencyNotDefined("Currency '{}' is not defined.".format(value))

        return value

    def _pre_delete(self, **kwargs):
        """Hook.

        :param force: only for testing purposes.
        """
        if not kwargs.get('force'):
            f = _odm.find('wallet_transaction').or_where('source', '=', self).or_where('destination', '=', self)
            if f.count():
                raise _odm.error.ForbidEntityDelete('Cannot delete account due to its usage in transaction(s).')

    @classmethod
    def ui_browser_setup(cls, browser):
        """Setup ODM UI browser hook.

        :type browser: pytsite.odm_ui._browser.Browser
        :return: None
        """
        browser.data_fields = ('aid', 'description', 'currency', 'balance', 'owner')

    def ui_browser_get_row(self) -> tuple:
        """Get single UI browser row hook.
        """
        balance = _currency.fmt(self.currency, self.balance)
        return self.aid, self.description, self.currency, balance, self.owner.full_name

    def ui_mass_action_get_entity_description(self) -> str:
        return '{} ({})'.format(self.aid, self.description)

    def ui_m_form_setup(self, form, stage: str):
        """Modify form setup hook.

        :type form: pytsite.form.Form
        """
        form.add_widget(_widget.input.Text(
                uid='aid',
                weight=10,
                label=self.t('aid'),
                required=True,
                value=self.aid,
        ))
        form.add_rule('aid', _odm.validation.FieldUnique(msg_id='pytsite.wallet@validation_account_id',
                                                         model=self.model, field='aid', exclude_ids=self.id))

        form.add_widget(_widget.input.Text(
                uid='description',
                weight=20,
                label=self.t('description'),
                value=self.description,
        ))

        if self.is_new:
            form.add_widget(_currency.widget.Select(
                    uid='currency',
                    weight=30,
                    label=self.t('currency'),
                    required=True,
                    value=self.currency,
                    h_size='col-sm-4 col-md-3 col-lg-2',
            ))
        else:
            form.add_widget(_widget.static.Text(
                    uid='currency',
                    weight=30,
                    label=self.t('currency'),
                    title=self.currency,
                    value=self.currency,
            ))

        form.add_widget(_auth_ui.widget.UserSelect(
                uid='owner',
                weight=40,
                label=self.t('owner'),
                required=True,
                value=self.owner,
                h_size='col-sm-6 col-md-5 col-lg-4',
        ))


class Transaction(_odm_ui.UIModel):
    """Transaction ODM Model.
    """

    def _setup(self):
        """Hook.
        """
        self._define_field(_odm.field.DateTime('time', nonempty=True, default=_datetime.now()))
        self._define_field(_odm.field.Ref('source', model='wallet_account', nonempty=True))
        self._define_field(_odm.field.Ref('destination', model='wallet_account', nonempty=True))
        self._define_field(_odm.field.String('state', default='new'))
        self._define_field(_odm.field.Decimal('amount', round=8))
        self._define_field(_odm.field.Decimal('exchange_rate', round=8, default=1))
        self._define_field(_odm.field.String('description'))
        self._define_field(_odm.field.Dict('options'))

        self._define_index([('time', _odm.I_DESC)])

    @property
    def time(self) -> _datetime:
        return self.f_get('time')

    @property
    def source(self) -> Account:
        return self.f_get('source')

    @property
    def destination(self) -> Account:
        return self.f_get('destination')

    @property
    def state(self) -> str:
        return self.f_get('state')

    @property
    def amount(self) -> _Decimal:
        return self.f_get('amount')

    @property
    def exchange_rate(self) -> _Decimal:
        return self.f_get('exchange_rate')

    @property
    def description(self) -> str:
        return self.f_get('description')

    @property
    def options(self) -> dict:
        return self.f_get('options')

    def _on_f_set(self, field_name: str, value, **kwargs):
        """Hook.
        """
        if not self.is_new and field_name in ('source', 'destination', 'amount'):
            raise ValueError('Transaction cannot be changed.')

        return value

    def _pre_save(self):
        """Hook.
        """
        if self.is_new and self.exchange_rate == 1:
            self.f_set('exchange_rate', _currency.get_rate(self.source.currency, self.destination.currency))

    def _pre_delete(self, **kwargs):
        """Hook.
        :param force: only for testing purposes.
        """
        if not kwargs.get('force'):
            raise _odm.error.ForbidEntityDelete('Wallet transactions cannot be deleted.')

    def cancel(self):
        if self.state != 'committed':
            raise _error.ImproperTransactionState('It is possible to cancel only committed transactions.')

        self.f_set('state', 'cancel').save()

        return self

    @classmethod
    def ui_browser_setup(cls, browser):
        """Setup ODM UI browser hook.

        :type browser: pytsite.odm_ui._browser.Browser
        :return: None
        """
        browser.data_fields = ('time', 'source', 'destination', 'amount', 'state')
        browser.default_sort_field = 'time'

    @classmethod
    def ui_browser_get_mass_action_buttons(cls):
        return {
                   'ep': 'pytsite.wallet.ep.transactions_cancel', 'icon': 'undo', 'color': 'danger',
                   'title': Transaction.t('odm_ui_form_title_delete_wallet_transaction'),
               },

    def ui_browser_get_row(self) -> tuple:
        """Get single UI browser row hook.
        """
        time = self.f_get('time', fmt='pretty_date_time')
        source = '{} ({})'.format(self.source.description, self.source.aid)
        destination = '{} ({})'.format(self.destination.description, self.destination.aid)

        amount = _currency.fmt(self.source.currency, self.amount)
        if self.source.currency != self.destination.currency:
            amount += ' ({})'.format(_currency.fmt(self.destination.currency, self.amount * self.exchange_rate))

        state_cls = 'primary'
        if self.state in ('pending', 'cancel', 'cancelling'):
            state_cls = 'warning'
        if self.state == 'committed':
            state_cls = 'success'
        if self.state == 'cancelled':
            state_cls = 'default'
        state = '<span class="label label-{}">'.format(state_cls) + self.t('transaction_state_' + self.state) + '</div>'

        return time, source, destination, amount, state

    def ui_browser_get_entity_actions(self) -> tuple:
        if self.state == 'committed':
            return {'icon': 'undo', 'ep': 'pytsite.wallet.ep.transactions_cancel', 'color': 'danger',
                    'title': self.t('cancel')},

        return ()

    @classmethod
    def ui_is_modification_allowed(cls) -> bool:
        return False

    @classmethod
    def ui_is_deletion_allowed(cls) -> bool:
        return False

    def ui_m_form_setup(self, form, stage: str):
        """Modify form setup hook.

        :type form: pytsite.form.Form
        """
        form.add_widget(_wallet_widget.AccountSelect(
                uid='source',
                weight=10,
                label=self.t('source'),
                required=True,
                value=self.source,
        ))

        form.add_widget(_wallet_widget.AccountSelect(
                uid='destination',
                weight=20,
                label=self.t('destination'),
                required=True,
                value=self.destination,
        ))

        form.add_widget(_widget.input.Float(
                uid='amount',
                weight=30,
                label=self.t('amount'),
                value=self.amount,
                required=True,
                min=0.01,
                h_size='col-sm-4 col-md-3 col-lg-2',
        ))
