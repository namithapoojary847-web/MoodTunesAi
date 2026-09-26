/* =====================================
   MOODTUNES AI PREMIUM LANDING PAGE JS
===================================== */


/* ===============================
   CURSOR GLOW EFFECT
================================ */


const cursorGlow = document.querySelector(".cursor-glow");


document.addEventListener("mousemove", (e)=>{


    cursorGlow.style.left = e.clientX + "px";

    cursorGlow.style.top = e.clientY + "px";


});





/* ===============================
   ANIMATED WAVE CANVAS
================================ */


const canvas = document.getElementById("waveCanvas");

const ctx = canvas.getContext("2d");


let width;
let height;


function resizeCanvas(){

    width = canvas.width = window.innerWidth;

    height = canvas.height = window.innerHeight;

}


resizeCanvas();


window.addEventListener(
    "resize",
    resizeCanvas
);



let waveOffset = 0;



function drawWave(){


    ctx.clearRect(
        0,
        0,
        width,
        height
    );


    ctx.beginPath();



    for(let x=0; x<width; x++){


        let y =

        height/2 +

        Math.sin(
            x*0.008 +
            waveOffset
        )
        *
        80;


        ctx.lineTo(
            x,
            y
        );


    }



    ctx.strokeStyle =
    "rgba(0,245,255,0.25)";


    ctx.lineWidth = 2;


    ctx.stroke();



    waveOffset +=0.02;


    requestAnimationFrame(drawWave);


}


drawWave();







/* ===============================
   PARTICLE SYSTEM
================================ */


const particleContainer =
document.getElementById("particles");



const particleCount = 45;



for(let i=0;i<particleCount;i++){


    let particle =
    document.createElement("span");


    particle.className =
    "particle";


    particle.style.left =
    Math.random()*100+"%";


    particle.style.top =
    Math.random()*100+"%";



    particle.style.animationDelay =
    Math.random()*5+"s";



    particleContainer.appendChild(
        particle
    );


}






/* ===============================
   ADD PARTICLE CSS
================================ */


const style =
document.createElement("style");


style.innerHTML = `


.particle{


position:absolute;


width:5px;

height:5px;


background:#00f5ff;


border-radius:50%;


box-shadow:

0 0 15px #00f5ff;


animation:

particleMove 10s infinite linear;


opacity:.7;


}



@keyframes particleMove{


0%{

transform:

translateY(0)
translateX(0);


opacity:0;


}



20%{

opacity:1;

}



100%{


transform:

translateY(-120vh)
translateX(100px);



opacity:0;


}



}



`;



document.head.appendChild(style);








/* ===============================
   MUSIC CARD BUTTON
================================ */


const musicButton =
document.querySelector(".music-card button");



let playing=false;



if(musicButton){


musicButton.addEventListener(
"click",
()=>{


playing=!playing;



if(playing){


musicButton.innerHTML =
`
<i class="fa-solid fa-pause"></i>
`;



musicButton.style.boxShadow =
"0 0 40px #ff00c8";



}

else{


musicButton.innerHTML =
`
<i class="fa-solid fa-play"></i>
`;



musicButton.style.boxShadow =
"0 0 20px #00f5ff";



}



});


}







/* ===============================
   SCROLL REVEAL ANIMATION
================================ */


const observer = new IntersectionObserver(
(entries)=>{


entries.forEach(entry=>{


if(entry.isIntersecting){


entry.target.style.opacity=1;

entry.target.style.transform=
"translateY(0)";


}


});


},
{
threshold:.2
}
);



document.querySelectorAll(
".hero-left,.hero-right,.music-card"
)
.forEach(el=>{


el.style.opacity=0;


el.style.transform=
"translateY(40px)";


el.style.transition=
"1s ease";


observer.observe(el);


});








/* ===============================
   BUTTON RIPPLE EFFECT
================================ */


document.querySelectorAll(
".primary-btn,.secondary-btn,.nav-btn"
)
.forEach(button=>{


button.addEventListener(
"click",
function(e){


let ripple =
document.createElement("span");


ripple.className="ripple";


this.appendChild(ripple);



setTimeout(()=>{

ripple.remove();

},600);



});

});




const rippleCSS =
document.createElement("style");


rippleCSS.innerHTML=`


.primary-btn,
.secondary-btn,
.nav-btn{

position:relative;

overflow:hidden;

}



.ripple{


position:absolute;


width:10px;

height:10px;


background:white;


border-radius:50%;


transform:scale(0);


animation:ripple .6s linear;


}



@keyframes ripple{


to{


transform:scale(30);

opacity:0;


}



}



`;



document.head.appendChild(rippleCSS);







console.log(
"✨ MoodTunes AI Welcome Page Loaded"
);