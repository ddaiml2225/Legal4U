var ws = new WebSocket('ws://127.0.0.1:8000/ws/ac/')
var log = document.getElementById("chat-log")

ws.onopen = function () {
    console.log("Connected to server")
    ws.send("initial message decided by developers")
}

ws.onmessage = function (event) {
    log.insertAdjacentHTML('beforeend',
    `<article class="msg-container msg-remote" id="msg-0">
        <div class="msg-box">
            <img class="user-img" id="user-0" src="/static/images/other/bot.png" />
            <div class="flr">
                <div class="messages">
                    <p class="msg" id="msg-0">
                        ${event['data']}
                    </p>
                </div>
                <span class="timestamp"><span class="username">Didi</span>&bull;<span class="posttime">${getDate()}</span></span>
            </div>
        </div>
    </article>`);
}

ws.onerror = function (event) {
    console.log("Error occured...",event)
}

ws.onclose = function (event) {
    console.log("Disconnected...")
}

function getDate(){
    var today = new Date();
    var day = today.getDate() + "";
    var month = (today.getMonth() + 1) + "";
    var year = today.getFullYear() + "";
    var hour = today.getHours() + "";
    var minutes = today.getMinutes() + "";
    var seconds = today.getSeconds() + "";

    day = checkZero(day);
    month = checkZero(month);
    year = checkZero(year);
    hour = checkZero(hour);
    minutes = checkZero(minutes);
    seconds = checkZero(seconds);
    
    var finalDate = day + "/" + month + "/" + year + " " + hour + ":" + minutes + ":" + seconds;
    return finalDate
}


function checkZero(data){
    if(data.length == 1){
      data = "0" + data;
    }
    return data;
}

document.getElementById("chat-message-submit").onclick = function (event){
    const input = document.getElementById("chat-message-input")
    const mssg = input.value
    ws.send(mssg)
    log.insertAdjacentHTML('beforeend',
    `<article class="msg-container msg-self" id="msg-0">
        <div class="msg-box">
            <div class="flr">
                <div class="messages">
                    <p class="msg" id="msg-1">
                        ${mssg}
                    </p>
                </div>
                <span class="timestamp"><span class="username">User</span>&bull;<span class="posttime">${getDate()}</span></span>
            </div>
            <img class="user-img" id="user-0" src="/static/images/other/woman.png" />
        </div>
    </article>`);
    input.value = ""
}


document.getElementById('chat-message-input').onkeydown = function(e){
    if(e.key == 'Enter'){
      // submit
      document.getElementById("chat-message-submit").click();
    }
 };