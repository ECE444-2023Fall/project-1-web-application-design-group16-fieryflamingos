const daysContainer = document.querySelector(".days"),
    nextBtn = document.querySelector(".next-btn"),
    prevBtn = document.querySelector(".prev-btn"),
    month = document.getElementById("month");
    todayBtn = document.querySelector(".today-btn");

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


date.setMonth(monthIdx-1);
date.setFullYear(year);
let currentMonth = date.getMonth();
let currentYear = date.getFullYear();
console.log(monthIdx)
console.log(year)


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
        if(i === thisDate && currentMonth === thisMonth && currentYear === thisYear){
            days += `<div class="day today">${i}</div>`;
        }else{
            days += `<div class="day">${i}</div>`;
        }
    }

    for(let j = 1; j <= nextDays; j++){
        days += `<div class="day next">${j}</div>`;
    }

    hideTodayBtn();
    daysContainer.innerHTML = days;
}

renderCalendar();

nextBtn.addEventListener("click", () => {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('month', `${monthAsNumber+1}`);
    urlParams.set('year', `${yearAsNumber}`);
    let url = `${window.location.pathname}?${urlParams}`;

    window.location = url;
});

prevBtn.addEventListener("click", () => {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('month', `${monthAsNumber-1}`);
    urlParams.set('year', `${yearAsNumber}`);
    let url = `${window.location.pathname}?${urlParams}`;
    
    window.location = url;
});

todayBtn.addEventListener("click", () => {
    currentMonth = date.getMonth();
    currentYear = date.getFullYear();
    renderCalendar();
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
