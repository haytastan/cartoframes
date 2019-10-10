from carto.do_subscriptions import DOSubscriptionManager


def get_subscription_ids(credentials):
    purchased_datasets = fetch_subscriptions(credentials)
    purchased_dataset_ids = list(map(lambda pd: pd.id, purchased_datasets))
    return ','.join(["'" + id + "'" for id in purchased_dataset_ids])


def fetch_subscriptions(credentials):
    if credentials:
        api_key_auth_client = credentials.get_api_key_auth_client()
        do_manager = DOSubscriptionManager(api_key_auth_client)
        if do_manager is not None:
            return do_manager.all()
    return []


def display_subscription_form():
    if is_ipython_notebook():
        display_notebook_subscription_form()
    else:
        display_cli_subscription_form()


def display_notebook_subscription_form():
    from IPython.display import display
    from ipywidgets.widgets import HTML, GridspecLayout, Button, Layout

    def create_expanded_button(description, button_style):
        return Button(description=description, button_style=button_style, layout=Layout(height='32px', width='176px'))

    message = '''
    <h3>Subscription contract</h3>
    You are about to subscribe to <b>%{dataset_name}</b>.
    The cost of this dataset is <b>$%{price}/%{update_frequency}</b>.
    If you want to proceed, a Request will be sent to CARTO who will order the data and load it into your account.
    This dataset is available for Instant Order for your organization, so it will automatically process the order and you will get inmediate access to the dataset.
    In order to proceed we need you to agree to the License of the dataset available at <b><a href=http://carto.com>http://carto.com</a></b>.
    <br>Do you want to proceed?
    '''
    text = HTML(message)

    button_yes = create_expanded_button('Yes', 'info')
    button_no = create_expanded_button('No', '')

    buttons = GridspecLayout(1, 5)
    buttons[0, 0] = button_yes
    buttons[0, 1] = button_no

    def disable_buttons():
        button_yes.disabled = True
        button_no.disabled = True

    def on_button_yes_clicked(b):
        disable_buttons()
        display(HTML('Yes'))

    def on_button_no_clicked(b):
        disable_buttons()
        display(HTML('No'))

    button_yes.on_click(on_button_yes_clicked)
    button_no.on_click(on_button_no_clicked)

    display(text, buttons)


def display_cli_subscription_form():
    print('This method is not yet implemented in CLI')


def is_ipython_notebook():
    """
    Detect whether we are in a Jupyter notebook.
    """
    try:
        cfg = get_ipython().config
        if 'IPKernelApp' in cfg:
            return True
        else:
            return False
    except NameError:
        return False
