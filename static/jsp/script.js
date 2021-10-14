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

            var day_hover = daySquare.id
            console.log(day_hover)
            var dateObj = new Date()
            var monthuser = dateObj.toLocaleString("default", { month: "long" })
            console.log(monthuser)
            var yearuser = dateObj.toLocaleString("default", { year: "numeric" })
            console.log(yearuser)
            const options = { 
                month: 'long',
                year: 'numeric' 
            };

            const request = new XMLHttpRequest()
            request.open('POST',   `/calendar/${JSON.stringify(day_hover)}/${JSON.stringify(monthuser)}/${JSON.stringify(yearuser)}`)
            request.onload = () => {
                const options = { 
                    month: 'long', 
                };  
                
                monthdisplay = new Date().toLocaleDateString('en-US', options);
                const sss = { 
                    year: 'numeric',
                };  
                
                yeardisplay = new Date().toLocaleDateString('en-US', sss);
                dateuser = monthdisplay + " " + day_hover + ", " + yeardisplay
                dateuser = dateuser

                //console.log(date)
                localStorage.setItem("date", dateuser);
            }
            request.send()
            daySquare.addEventListener('click', () => location = `/calendar/${JSON.stringify(day_hover)}/${JSON.stringify(monthuser)}/${JSON.stringify(yearuser)}`);
        }
        daySquare.addEventListener('mouseenter', () => sendUserInfo());

    } 

    if (daySquare.id == 'currentDay'){
        daySquare.addEventListener('click', () => location = "http://192.168.1.10:2000/home");
    }
    

    }
    else {
    daySquare.classList.add('padding');
    }

    calendar.appendChild(daySquare);    
}
}

load();