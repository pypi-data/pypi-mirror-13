import wtforms


class FakeSelectMultipleField(wtforms.fields.SelectMultipleField):
    # prevent validation for value in choices
    def pre_validate(self, *args, **kwargs):
        return None


class Filter:
    def filter(self, query, value):
        raise NotImplementedError

    def get_form_field(self, key, query):
        raise NotImplementedError


class Controller:
    per_page = 100

    def __init__(self, filters=None, actions=None, per_page=None):
        self.filters = filters
        self.actions = actions
        if per_page is not None:
            self.per_page = per_page

    def get_filter_form(self):
        raise NotImplementedError

    def get_filters(self, params):
        if not self.filters:
            return []
        return [
            (self.filters[key], value)
            for key, value in params.items()
            if key in self.filters and value
        ]

    def get_action_form(self):
        choices = [('', '')]
        if self.actions is not None:
            choices.extend(
                (key, key.title()) for key, action in self.actions.items())

        class ActionsForm(wtforms.Form):
            ids = FakeSelectMultipleField('ids', coerce=int, choices=[])
            action = wtforms.fields.SelectField(choices=choices)
        return ActionsForm

    def execute_action(self, params):
        form = self.get_action_form()(params)
        if form.validate():
            self.actions[form.action.data](form.ids.data)

    def get_items(self, page=1, order_by=None, filters=None):
        """Return a paginated list of columns."""
        raise NotImplementedError

    def get_item(self, pk):
        """Return a entry with PK."""
        raise NotImplementedError

    def create_item(self, form):
        """Create a new entry in the storage."""
        raise NotImplementedError

    def update_item(self, item, form):
        """Update a entry in storage."""
        raise NotImplementedError

    def delete_item(self, item):
        """Delete a new entry in storage."""
        raise NotImplementedError
