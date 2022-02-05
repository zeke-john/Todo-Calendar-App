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
calendar.innerText = '';

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
    var monthdisplay = (`${dt.toLocaleDateString('en-us', { month: 'long' })}`)
    var yeardisplay = `${year}`

    let toString = date_of_todo.toString()
    let split = toString.split(/[!,?,.]/);
    user_id = user_id
    split.forEach((element) => {
        if (" 39" + monthdisplay +  " " + daySquare.id + " " +yeardisplay + "39" == element || "39" + monthdisplay +  " " + daySquare.id + " " +yeardisplay + "39" == element) {
            daySquare.id = 'HasTasks';
        }
    });

    split.forEach((element) => {
        if (" 39" + monthdisplay +  " " + daySquare.id + " " +yeardisplay + "s" + "39" == element || "39" + monthdisplay +  " " + daySquare.id + " " +yeardisplay + "s" + "39" == element) {
            daySquare.id = 'compTasks';
        }
    });

    if(daySquare.id !='currentDay' && daySquare.id != 'less'){
        function sendUserInfo(){
            var day_hover = daySquare.id
            if (day_hover == 'HasTasks' || day_hover == 'compTasks'){   
                day_hover = i - paddingDays
            }
            var monthuser = `${dt.toLocaleDateString('en-us', { month: 'numeric' })}`
            var yearuser = `${year}`

            const request = new XMLHttpRequest()
            request.open('POST',   `/calendar/${JSON.stringify(day_hover)}/${JSON.stringify(monthuser)}/${JSON.stringify(yearuser)}`)
            request.onload = () => {
                var monthuser = `${dt.toLocaleDateString('en-us', { month: 'long' })}`
                var yearuser = `${year}`
                dateuser = monthuser + " " + day_hover + ", " + yearuser
                dateuser = dateuser
                localStorage.setItem("date", dateuser);
            }
            request.send()
            
            daySquare.addEventListener('click', () => location = `/calendar/${JSON.stringify(day_hover)}/${JSON.stringify(monthuser)}/${JSON.stringify(yearuser)}`);
        }
        sendUserInfo()
        daySquare.addEventListener('mouseenter', () => sendUserInfo());
    } 
    
    if (daySquare.id == 'currentDay'){
        daySquare.addEventListener('click', () => location = "http://192.168.1.11:5000/today");
    }
    if (daySquare.id == 'less'){
        daySquare.addEventListener('click', () => location = "#");
    }
    

    }
    else {
        daySquare.classList.add('padding');
        daySquare.id = 'less';
    }

    calendar.appendChild(daySquare);    
}
}
function initButtons() {
    document.getElementById('nextbutton').addEventListener('click', ()=> {
        nav++;
        load();
    });
    document.getElementById('backbutton').addEventListener('click', () => {
        nav--;
        load();
    });
    }

initButtons()
load();