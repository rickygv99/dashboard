# DAO Governance Dashboard

## Setup and Installation

Running the dashboard in your local environment requires Python 3+. It is highly recommended that you setup and run the dashboard within a virtual environment. In order to install Python 3 and create a virtual environment, we highly recommend following [this guide](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-programming-environment-on-an-ubuntu-20-04-server).

To begin, clone this GitHub repository to your local computer and navigate to the project root:

`git clone https://github.com/rickygv99/dashboard.git`  
`cd dashboard`

Then, run the following commands to install necessary dependencies:

`pip install --upgrade pip`  
`pip install -r requirements.txt`

Next, run the following command to create a file to store your API keys:

`cp .env.example .env`

To run the dashboard, you will need to generate the necessary keys.
 - You can fill in any value you would like for `SECRET_KEY` -- this will be your Django secret key.
 - To generate an Etherscan API key, navigate to [Etherscan's API keys instructions page here](https://info.etherscan.com/api-keys/) and follow the instructions shown.
 - To generate a Coin API key, navigate to [Coin API's website here](https://www.coinapi.io/), click the "GET A FREE API KEY" button, and follow the instructions shown.

Once you have done so, to verify that you have set up the dashboard correctly, run the following command:

`python manage.py runserver`

Then, run the following command to create and set up the database:

`python manage.py migrate`

Finally, you can load the dashboard. Open the dashboard in the browser at http://localhost:8000. 
