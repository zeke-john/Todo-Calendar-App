let nav = 0;
let clicked = null;
let events = localStorage.getItem('events') ? JSON.parse(localStorage.getItem('events')) : [];

const calendar = document.getElementById('calendar');
const weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

function openModal(date) {
clicked = date;

const eventForDay = events.find(e => e.date === clicked);

if (eventForDay) {
    document.getElementById('eventText').innerText = eventForDay.title;
}

backDrop.style.display = 'block';
}

function load() {
const dt = new Date();

if (nav !== 0) {
    dt.setMonth(new Date().getMonth() + nav);
}

const day = dt.getDate();
const month = dt.getMonth();
const year = dt.getFullYear();

const firstDayOfMonth = new Date(year, month, 1);
const daysInMonth = new Date(year, month + 1, 0).getDate();

const dateString = firstDayOfMonth.toLocaleDateString('en-us', {
    weekday: 'long',
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
});
const paddingDays = weekdays.indexOf(dateString.split(', ')[0]);    

document.getElementById('monthDisplay').innerText = 

`${dt.toLocaleDateString('en-us', { month: 'long' })} ${year}`;
calendar.innerHTML = '';

for(let i = 1; i <= paddingDays + daysInMonth; i++) {
    const daySquare = document.createElement('div');
    daySquare.classList.add('day');
    daySquare.id = i - paddingDays
    const dayString = `${month + 1}/${i - paddingDays}/${year}`;

    if (i > paddingDays) {
    daySquare.innerText = i - paddingDays;
    const eventForDay = events.find(e => e.date === dayString);

    if (i - paddingDays === day && nav === 0) {
        daySquare.id = 'currentDay';
    }
    
    
    if(daySquare.id !='currentDay'){
        function sendUserInfo(){
            var userInfo = daySquare.id
            console.log(userInfo)
            var userMonth = month + 1
            //console.log(daysInMonth)
            const request = new XMLHttpRequest()
            request.open('POST',   `/calendar/${JSON.stringify(userInfo)}/${JSON.stringify(daysInMonth)}/${JSON.stringify(userMonth)}`)
            request.onload = () => {
                const options = { 
                    month: 'long', 
                };  
                
                date = new Date().toLocaleDateString('en-US', options);
                date = date + " " + userInfo
                date = date
                //console.log(date)
                localStorage.setItem("date", date);
            }
            request.send()

            daySquare.addEventListener('click', () => location = `/calendar/${JSON.stringify(userInfo)}/${JSON.stringify(daysInMonth)}/${JSON.stringify(userMonth)}`);
        }
        daySquare.addEventListener('mouseenter', () => sendUserInfo());

    } 

    if (daySquare.id == 'currentDay'){
        daySquare.addEventListener('click', () => location = "http://192.168.1.20:5000/home");
    }
    

    }
    else {
    daySquare.classList.add('padding');
    }

    calendar.appendChild(daySquare);    
}
}

load();