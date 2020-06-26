# mniam! SMS sending service

### Prerequisites

- A compatible Huawei modem (for a list see https://github.com/Salamek/huawei-lte-api)

- A python3 interpreter

### Usage

- Clone this repo: `git clone https://github.com/marektopolewski/mniam-sms`

- Install python dependencies: `pip install -r requirements.txt.`

- Start the service: `./server.py <BACKEND_URL> <ROUTER_PSW>`
  
    * `BACKEND_URL` - URL address of the server SMS requests are fetched from and confirmed to.

    * `ROUTER_PSW` - password of the `admin` user to authenticate with the router

(You can also use a chron job, supervisor or simply `./server.py <BACKEND_URL> <ROUTER_PSW> -` to run in the background.)