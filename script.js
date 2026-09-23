/* =================================
   CITY VARIABLE
================================= */

let city = "";


/* =================================
   GET ELEMENTS
================================= */

const cityInput =
    document.getElementById("cityInput");

const cityButton =
    document.getElementById("cityButton");

const questionInput =
    document.getElementById("questionInput");

const sendButton =
    document.getElementById("sendButton");

const response =
    document.getElementById("response");


/* =================================
   SET CITY
================================= */

function setCity() {

    city = cityInput.value.trim();


    /* If city is empty */

    if (city === "") {
        return;
    }


    /* Change button */

    cityButton.innerText = "✓ Set";


    /* Change back after 1.5 seconds */

    setTimeout(function () {

        cityButton.innerText = "Set city";

    }, 1500);
}


/* =================================
   SEND QUESTION
================================= */

function sendQuestion() {

    const question =
        questionInput.value.trim();


    /* Empty question */

    if (question === "") {
        return;
    }


    /* =================================
       CITY NOT ENTERED
    ================================= */

    if (city === "") {

        response.style.display = "block";

        response.innerHTML =
            "<b>Please enter your city first.</b>";


        /* Scroll to response */

        setTimeout(function () {

            response.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

        }, 100);


        return;
    }


    /* =================================
       SHOW RESPONSE
    ================================= */

    response.style.display = "block";


    response.innerHTML =

        "<b>Question:</b> " +

        escapeHTML(question) +

        "<br><br>" +

        "<b>City:</b> " +

        escapeHTML(city) +

        "<br><br>" +

        "🌱 KrishiGPT is processing your agricultural question...";


    /* Clear question box */

    questionInput.value = "";


    /* =================================
       SCROLL TO RESPONSE
    ================================= */

    setTimeout(function () {

        response.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

    }, 100);
}


/* =================================
   ENTER KEY
================================= */

questionInput.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Enter") {

            sendQuestion();

        }

    }
);


/* =================================
   CITY BUTTON
================================= */

cityButton.addEventListener(
    "click",
    setCity
);


/* =================================
   SEND BUTTON
================================= */

sendButton.addEventListener(
    "click",
    sendQuestion
);


/* =================================
   HTML SECURITY
================================= */

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}