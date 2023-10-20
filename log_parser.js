const TUTOR_CONNECTION = /ConferenceManager_ConferenceMemberJoined! \((.+)\(Tutor\)/;
const TUTOR_DISCONNECTION = /ConferenceManager_ConferenceMemberLeft! \((.+)\(Tutor\)/;
const CUSTOMER_CONNECTION = /ConferenceManager_ConferenceMemberJoined! \((.+)\(Customer\)/;
const CUSTOMER_DISCONNECTION = /ConferenceManager_ConferenceMemberLeft! \((.+)\(Customer\)/;
const TIMESTAMP = /^(\d{1,2}\/\d{1,2}\/\d{4} \d{1,2}:\d{2}:\d{2} (?:AM|PM))/;

const TIME_DELTA = 5;

function parseTime(line) {
    const match = line.match(TIMESTAMP);
    return new Date(Date.parse(match[0]));
}

function displayMessage(message) {
    const resultsDiv = document.getElementById("results");
    const cardHtml = `
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">Possible missing pay on ${message.sessionStartTime}:</h5>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item">Customer: ${message.customerNameWhoLeft}</li>
                    <li class="list-group-item">Customer disconnect registered at: ${message.customerLeftTime}</li>
                    <li class="list-group-item">Tutor disconnect registered at: ${message.tutorLeftTime}</li>
                    <li class="list-group-item">Paid time: ${(message.paidTime / (1000 * 60)).toFixed(2)}</li>
                    <li class="list-group-item">Unpaid time: ${message.unpaidTime.toFixed(2)}</li>
                </ul>
            </div>
        </div>
    `;
    resultsDiv.innerHTML += cardHtml;
}
class ChatStateMachine {
    constructor() {
        this.state = this.initialState;
        this.sessionStartTime = null;
        this.customerLeftTime = null;
        this.customerNameWhoJoined = "";
        this.customerNameWhoLeft = "";
    }

    initialState(line) {
        if (this.customerJoined(line)) {
            this.state = this.initialState;
            return;
        }

        const match = CUSTOMER_DISCONNECTION.exec(line);
        if (match) {
            this.customerNameWhoLeft = match[1];
            this.customerLeftTime = parseTime(line);
            this.state = this.customerLeft;
        }
    }

    customerLeft(line) {
        if (this.customerJoined(line)) {
            this.state = this.initialState;
            return;
        }

        if (TUTOR_DISCONNECTION.test(line)) {
            const tutorLeftTime = parseTime(line);
            const timeBetweenEvents = (tutorLeftTime - this.customerLeftTime) / (1000 * 60); // in minutes

            if (timeBetweenEvents > TIME_DELTA) {

            const information = {
                sessionStartTime: this.sessionStartTime,
                customerNameWhoLeft: this.customerNameWhoLeft,
                customerLeftTime: this.customerLeftTime,
                tutorLeftTime: tutorLeftTime,
                paidTime: parseFloat((this.customerLeftTime - this.sessionStartTime).toFixed(2)),
                unpaidTime: timeBetweenEvents
            };
            displayMessage(information);
                displayMessage(information);
                this.customerNameWhoLeft = "";
                this.customerNameWhoJoined = "";
                this.sessionStartTime = null;
                this.customerLeftTime = null;
            }

            this.state = this.initialState;
        }
    }

    customerJoined(line) {
        const match = CUSTOMER_CONNECTION.exec(line);
        if (match) {
            if (match[1] !== this.customerNameWhoJoined) {
                this.customerNameWhoJoined = match[1];
                this.sessionStartTime = parseTime(line);
            }
            return true;
        }
        return false;
    }

    process(lines) {
        lines.forEach(line => {
            this.state(line);
        });
    }
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        const logContents = e.target.result.split("\n");
        const parser = new ChatStateMachine();
        parser.process(logContents);
    };

    reader.readAsText(file);
}
