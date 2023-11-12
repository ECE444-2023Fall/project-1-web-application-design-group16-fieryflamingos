const daysContainer = document.querySelector(".days"),
    nextBtn = document.querySelector(".next-btn"),
    prevBtn = document.querySelector(".prev-btn"),
    month = document.getElementById("month"),
    todayBtn = document.querySelector(".today-btn"),
    calendarInfo = document.querySelector(".calendar_info");


    var eventsThisYear = [];
    var eventsThisMonth = [];
    var eventsThisDay = [];
    //const allUserEvents = [];

    //var events = JSON.parse('{{events|tojson|safe}}');
        //var output = eventSetup(events);

const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
];

const weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu",  "Fri", "Sat"];

const date = new Date();

//Copy all of the user's events for ease of reference
/*function eventSetup(events){
    for(var i = 0; i < events.length; i++){
        allUserEvents.push(events[i]);
    }
}*/

//Variables for current calendar being displayed
let currentDate = date.getDate();
let currentMonth = date.getMonth();
let currentYear = date.getFullYear();


//Variables for the current calendar event information being displayed
let calInfoDate = date.getDate();
let calInfoMonth = date.getMonth();
let calInfoYear = date.getFullYear();

//Grab the events for the current displayed year indicated by currentYear
function getEventsThisYear(){
    eventsThisYear = [];
    for(i = 0; i < allUserEvents.length; i++){
        console.log(allUserEvents[i].year);
        if(allUserEvents[i].year == currentYear){
            eventsThisYear.push(allUserEvents[i]);
            console.log(allUserEvents[i].title);
            console.log('Im here');
        }
    }
}

//Grab the events for the current displayed month indicated by currentMonth
function getEventsThisMonth(){
    eventsThisMonth = []
    for(i = 0; i < eventsThisMonth.length; i++){
        if(eventsThisYear[i].month == currentMonth){
            eventsThisMonth.push(eventsThisYear[i]);
            console.log(eventsThisYear[i].title)
        }
    }
}

//Grab the events for the current displayed month indicated by calInfoDate
function getEventsThisDay(){
    for(i = 0; i < eventsThisMonth.length; i++){
        if(eventsThisMonth[i].day == Number(calInfoDate)){
            eventsThisDay.push(eventsThisMonth[i]);
            console.log(eventsThisMonth[i].title)
        }
    }
}

//Function for updating the calendar
function renderCalendar() {
    date.setDate(1);
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const lastDayIndex = lastDay.getDay();
    const lastDayDate = lastDay.getDate();
    const prevLastDay = new Date(currentYear, currentMonth, 0);
    const prevLastDayDate = prevLastDay.getDate();
    const nextDays = 7 - lastDayIndex - 1;
    thisDate = date.getDate();
    thisMonth = date.getMonth();
    thisYear = date.getFullYear();

    month.innerHTML = `${months[currentMonth]} ${currentYear}`;

    let days = "";
    
    for(let x = firstDay.getDay(); x > 0; x--){
        days += `<div class="day prev"> ${prevLastDayDate - x + 1}</div>`;
    }

    for(let i = 1; i <= lastDayDate; i++){
        if(i === currentDate && currentMonth === thisMonth && currentYear === thisYear){
            days += `<div class="day today day_info" id=${i}>${i}</div>`;
        }else{
            days += `<div class="day day_info" id=${i}>${i}</div>`;
        }
    }

    for(let j = 1; j <= nextDays; j++){
        days += `<div class="day next">${j}</div>`;
    }

    hideTodayBtn();
    daysContainer.innerHTML = days;
}


renderCalendar();
attach_day_click();
getEventsThisYear();
getEventsThisMonth();
render_day_info();

nextBtn.addEventListener("click", () => {
    currentMonth++;
    if(currentMonth > 11){
        currentMonth = 0;
        currentYear++;
        getEventsThisYear();
    }
    getEventsThisMonth();
    renderCalendar();
    attach_day_click();
});

prevBtn.addEventListener("click", () => {
    currentMonth--;
    if(currentMonth < 0){
        currentMonth = 11;
        currentYear--;
        geteEventsThisYear();
    }
    getEventsThisMonth();
    renderCalendar();
    attach_day_click();
});

todayBtn.addEventListener("click", () => {
    currentMonth = date.getMonth();
    currentYear = date.getFullYear();
    getEventsThisYear();
    getEventsThisMonth();
    renderCalendar();
    attach_day_click();
});

function hideTodayBtn(){
    if(
        currentMonth === new Date().getMonth() &&
        currentYear === new Date().getFullYear()
    ){
        todayBtn.style.display = "none";
    }else {
        todayBtn.style.display = "flex";
    }
}

function attach_day_click (){
    [...document.querySelectorAll('.day_info')].forEach(function(item) {
        item.addEventListener('click', function(item) {
          calInfoDate = item.target.id;
          calInfoMonth = currentMonth;
          calInfoYear = currentYear;
          render_day_info();
        });
         });
}

function render_day_info(){
    let calendar_info = "";
    calendar_info += `<div class="title" style="color: var(--White); margin-bottom: 0px;">
        ${months[calInfoMonth]} ${calInfoDate}, ${calInfoYear}</div>`;
    calendar_info += `<hr class="underline_white" style="width:100%; margin-bottom: 0px;"></hr>`;
    getEventsThisDay();
    for(var i = 0; i < eventsThisDay.length; i++){
        calendar_info +=  `<div class="row"> <div class="col-11 subtitle" style="color: var(--White); 
        margin-top: 32px; margin-left: 20px;"> ${eventsThisDay[i].from_time} - ${eventsThisDay[i].to_time}
        </div></div><div class = "row"> <div class="col-11 label" style="text-overflow: ellipsis; 
        overflow: hidden; text-wrap: nowrap; color: var(--White); margin-top: 8px; margin-left: 20px;">
        ${eventsThisDay[i].title}</div></div>`;
    }
    calendarInfo.innerHTML = calendar_info;
}