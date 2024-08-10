from fasthtml.common import *
import yfinance as yf
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
EXCHANGE_RATE_API_KEY = os.getenv('EXCHANGE_RATE_API_KEY')
EXCHANGE_RATE_API_URL = f'https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/pair'

# List of NASDAQ 100 stock symbols (abbreviated list for example)
NASDAQ_100_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "PYPL",
    "ADBE", "CMCSA", "NFLX", "INTC", "PEP", "CSCO", "AVGO", "COST",
    "TXN", "QCOM", "CHTR", "AMD", "INTU", "SBUX", "AMGN", "ISRG",
    "MDLZ", "BKNG", "AMAT", "ADI", "MU", "LRCX", "GILD", "MRNA"
]

app, Rt = fast_app()

@Rt('/')
def get():
    return Div(
        Link(href="/static/style.css", rel="stylesheet"),  # Include the CSS
        Style('''
            * {
                color: black; /* Set all text to black */
            }

            .autocomplete {
                position: relative;
                display: inline-block;
            }

            .autocomplete-items {
                position: absolute;
                border: 1px solid #d4d4d4;
                border-bottom: none;
                border-top: none;
                z-index: 99;
                top: 100%;
                left: 0;
                right: 0;
                background-color: #fff;
            }

            .autocomplete-items div {
                padding: 10px;
                cursor: pointer;
                background-color: #fff; 
                border-bottom: 1px solid #d4d4d4; 
            }

            .autocomplete-items div:hover {
                background-color: #e9e9e9; 
            }

            .autocomplete-active {
                background-color: DodgerBlue !important; 
                color: #ffffff; 
            }

            .modal {
                display: none;
                position: fixed;
                z-index: 1;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                overflow: auto;
                background-color: rgb(0,0,0);
                background-color: rgba(0,0,0,0.4);
                padding-top: 60px;
            }

            .modal-content {
                background-color: #13171f;
                margin: 5% auto;
                padding: 20px;
                border: 1px solid #888;
                width: 50%;
                border-radius: 10px;
            }

            .close {
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
            }

            .close:hover,
            .close:focus {
                color: black;
                text-decoration: none;
                cursor: pointer;
            }
        '''),
        Script(f'''
            function openModal(content) {{
                document.getElementById('modal-content').innerHTML = content;
                document.getElementById('modal').style.display = 'block';
            }}

            function closeModal() {{
                document.getElementById('modal').style.display = 'none';
            }}

            var nasdaq100 = {NASDAQ_100_SYMBOLS};

            function autocomplete(inp) {{
                var currentFocus;
                inp.addEventListener("input", function(e) {{
                    var a, b, i, val = this.value;
                    closeAllLists();
                    if (!val) {{ return false; }}
                    currentFocus = -1;
                    a = document.createElement("DIV");
                    a.setAttribute("id", this.id + "autocomplete-list");
                    a.setAttribute("class", "autocomplete-items");
                    this.parentNode.appendChild(a);
                    for (i = 0; i < nasdaq100.length; i++) {{
                        if (nasdaq100[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {{
                            b = document.createElement("DIV");
                            b.innerHTML = "<strong>" + nasdaq100[i].substr(0, val.length) + "</strong>";
                            b.innerHTML += nasdaq100[i].substr(val.length);
                            b.innerHTML += "<input type='hidden' value='" + nasdaq100[i] + "'>";
                            b.addEventListener("click", function(e) {{
                                inp.value = this.getElementsByTagName("input")[0].value;
                                closeAllLists();
                            }});
                            a.appendChild(b);
                        }}
                    }}
                }});
                inp.addEventListener("keydown", function(e) {{
                    var x = document.getElementById(this.id + "autocomplete-list");
                    if (x) x = x.getElementsByTagName("div");
                    if (e.keyCode == 40) {{
                        currentFocus++;
                        addActive(x);
                    }} else if (e.keyCode == 38) {{
                        currentFocus--;
                        addActive(x);
                    }} else if (e.keyCode == 13) {{
                        e.preventDefault();
                        if (currentFocus > -1) {{
                            if (x) x[currentFocus].click();
                        }}
                    }}
                }});
                function addActive(x) {{
                    if (!x) return false;
                    removeActive(x);
                    if (currentFocus >= x.length) currentFocus = 0;
                    if (currentFocus < 0) currentFocus = (x.length - 1);
                    x[currentFocus].classList.add("autocomplete-active");
                }}
                function removeActive(x) {{
                    for (var i = 0; i < x.length; i++) {{
                        x[i].classList.remove("autocomplete-active");
                    }}
                }}
                function closeAllLists(elmnt) {{
                    var x = document.getElementsByClassName("autocomplete-items");
                    for (var i = 0; i < x.length; i++) {{
                        if (elmnt != x[i] && elmnt != inp) {{
                            x[i].parentNode.removeChild(x[i]);
                        }}
                    }}
                }}
                document.addEventListener("click", function (e) {{
                    closeAllLists(e.target);
                }});
            }}

            function toggleInputs() {{
                var stockDiv = document.getElementById('stock-symbol-div');
                var customRateDiv = document.getElementById('custom-rate-div');
                var rateSource = document.querySelector('input[name="rate_source"]:checked').value;
                if (rateSource === 'stock') {{
                    stockDiv.style.display = 'block';
                    customRateDiv.style.display = 'none';
                }} else {{
                    stockDiv.style.display = 'none';
                    customRateDiv.style.display = 'block';
                }}
            }}

            document.addEventListener('DOMContentLoaded', function() {{
                autocomplete(document.getElementById('stock'));
                toggleInputs();  // Set initial visibility based on default selection
            }});
        '''),
        Div(
            H1('DCA Investment Calculator'),
            Form(
                P('Currency:'),
                Select(
                    Option('THB', value='THB'),
                    Option('USD', value='USD'),
                    Option('EUR', value='EUR'),
                    Option('JPY', value='JPY'),
                    Option('GBP', value='GBP'),
                    name='currency'
                ),
                P('Choose interest rate source:'),
                Label(
                    Input(name='rate_source', type='radio', value='stock', checked=True, onclick="toggleInputs()"),
                    'Use stock historical growth rate'
                ),
                Label(
                    Input(name='rate_source', type='radio', value='custom', onclick="toggleInputs()"),
                    'Use custom annual interest rate'
                ),
                Div(
                    P('Stock Symbol:'),
                    Div(
                        Input(name='stock', type='text', id='stock'),  # Added id for autocomplete
                        _class='autocomplete'  # Wrap input in a div for relative positioning
                    ),
                    id='stock-symbol-div'  # This div will be toggled
                ),
                Div(
                    P('Custom Annual Interest Rate (%):'),
                    Input(name='custom_interest_rate', type='number', step='0.01', value='10'),
                    id='custom-rate-div'  # This div will be toggled
                ),
                P('Initial Investment (per month):'),
                Input(name='initialInvestment', type='number', value='5000'),
                P('Duration (years):'),
                Input(name='duration', type='number', value='15'),
                P('Annual Increase (%):'),
                Input(name='annualIncrease', type='number', value='25'),
                Button('Calculate', type='submit'),
                action='/calculate', method='post', hx_post='/calculate', hx_target='#result'
            ),
            Div(id='result'),
            _class='container'  # Add a class to the container
        ),
        # Modal structure
        Div(
            Div(
                Span('X', _class='close', onclick='closeModal()'),
                Div(id='modal-content'),
                _class='modal-content'
            ),
            _class='modal',
            id='modal'
        ),
        _class='wrapper'  # Add a class to the wrapper for centering
    )

# Route to serve static files
@Rt('/static/<path:filename>')
async def static_files(request, filename):
    static_folder = 'static'
    file_path = os.path.join(static_folder, filename)
    with open(file_path, 'rb') as file:
        return Response(file.read(), media_type='text/css')

@Rt('/calculate', methods=['POST'])
async def calculate(request):
    form_data = await request.form()  # Extract form data
    rate_source = form_data['rate_source']  # Get rate source choice
    currency = form_data['currency']  # Get selected currency
    custom_interest_rate = float(form_data['custom_interest_rate'])  # Custom interest rate if selected
    initial_investment = float(form_data['initialInvestment'])
    duration = int(form_data['duration'])
    annual_increase = float(form_data['annualIncrease'])

    if rate_source == 'stock':
        stock = form_data['stock'].upper()  # Access stock symbol and ensure it's uppercase
        if stock not in NASDAQ_100_SYMBOLS:
            return Div(
                P(f'Error: The stock symbol "{stock}" is not valid or not part of the NASDAQ 100.')
            )

        # Fetch maximum available historical stock data
        stock_data = yf.Ticker(stock)
        hist = stock_data.history(period='max')['Close']

        # Remove timezone information to make the index tz-naive
        hist.index = hist.index.tz_localize(None)

        # Filter to only use data from the last `duration` years
        hist = hist[hist.index >= pd.Timestamp.now() - pd.DateOffset(years=duration)]

        if len(hist) < duration:
            return Div(
                P('Not enough data to cover the specified duration.'),
            )
    else:
        hist = None

    # Get currency conversion rate if needed
    conversion_rate = 1  # Default to no conversion
    if currency != 'USD':  # Assuming stock prices are in USD
        try:
            response = requests.get(f'{EXCHANGE_RATE_API_URL}/USD/{currency}')
            if response.status_code == 200:
                data = response.json()
                conversion_rate = data['conversion_rate']
            else:
                return Div(
                    P(f'Error fetching conversion rate: {response.status_code} - {response.text}'),
                )
        except Exception as e:
            return Div(
                P(f'Error fetching conversion rate: {str(e)}'),
            )

    total_value = 0

    for year in range(duration):
        # Calculate yearly investment considering annual increase
        yearly_investment = initial_investment * ((1 + annual_increase / 100) ** year)
        
        if rate_source == 'stock' and hist is not None:
            # Calculate the return based on the last closing prices of each year
            start_price = hist.iloc[0] if year == 0 else hist.iloc[year - 1]
            end_price = hist.iloc[year]
            yearly_return = (end_price - start_price) / start_price
        else:
            yearly_return = custom_interest_rate / 100  # Use the custom interest rate

        total_value += yearly_investment * (1 + yearly_return)

    # Convert the final value back to the selected currency
    total_value_converted = total_value * conversion_rate

    # Format the result with commas
    formatted_value = f"{total_value_converted:,.2f}"

    # Inject the result into the modal and open it
    modal_content = f'''
    <h2>Total Investment Value: {formatted_value} {currency}</h2>
    <p>Calculation complete.</p>
    '''
    return Script(f'openModal(`{modal_content}`);')

serve(host="127.0.0.1", port=9090)
