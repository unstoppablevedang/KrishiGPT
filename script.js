/* =================================
   KRISHIGPT FRONTEND CONFIG
================================= */

/*
   IMPORTANT:
   Replace this URL with your Codespaces
   forwarded HTTPS URL after we start Flask.

   Example:
   https://your-codespace-5000.app.github.dev
*/

const API_BASE =
    "https://legendary-giggle-jjvq4x6rjpr9fgvv-5000.app.github.dev";


/* =================================
   STATE
================================= */

let city = "";
let conversationId = "";


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

    if (city === "") {
        return;
    }

    cityButton.innerText = "✓ Set";

    setTimeout(function () {
        cityButton.innerText = "Set city";
    }, 1500);
}


/* =================================
   DISPLAY RESPONSE
================================= */

function showProcessing(question) {

    response.style.display = "block";

    response.innerHTML = "";

    const questionElement =
        document.createElement("div");

    questionElement.innerHTML =
        "<b>Question:</b> " +
        escapeHTML(question);

    response.appendChild(questionElement);

    const cityElement =
        document.createElement("div");

    cityElement.innerHTML =
        "<br><b>City:</b> " +
        escapeHTML(city);

    response.appendChild(cityElement);

    const answerTitle =
        document.createElement("div");

    answerTitle.innerHTML =
        "<br><b>🌱 KrishiGPT:</b>";

    response.appendChild(answerTitle);

    const answerElement =
        document.createElement("div");

    answerElement.id = "answerText";

    answerElement.style.marginTop = "10px";

    answerElement.textContent =
        "Thinking...";

    response.appendChild(answerElement);

    return answerElement;
}


/* =================================
   SHOW WEATHER
================================= */

function showWeather(weather) {

    if (!weather) {
        return;
    }

    try {

        const current =
            weather.forecast.current;

        const location =
            weather.location.name;

        const weatherElement =
            document.createElement("div");

        weatherElement.style.marginTop = "15px";

        weatherElement.innerHTML =
            "<b>🌤 Weather:</b> " +
            escapeHTML(location) +
            " — " +
            escapeHTML(
                String(current.temperature_2m)
            ) +
            "°C, humidity " +
            escapeHTML(
                String(current.relative_humidity_2m)
            ) +
            "%";

        response.appendChild(weatherElement);

    } catch (error) {

        console.log(
            "Weather display skipped:",
            error
        );

    }
}


/* =================================
   SHOW SOURCES
================================= */

function showSources(sources) {

    if (!sources || sources.length === 0) {
        return;
    }

    const sourceTitle =
        document.createElement("div");

    sourceTitle.style.marginTop = "15px";

    sourceTitle.innerHTML =
        "<b>📚 Sources:</b>";

    response.appendChild(sourceTitle);


    const sourceList =
        document.createElement("ul");

    sourceList.style.marginTop = "5px";


    sources.forEach(function (source) {

        const item =
            document.createElement("li");

        let text =
            source.source ||
            "Agriculture knowledge source";

        if (source.page) {
            text +=
                " — page " +
                source.page;
        }


        if (source.url) {

            const link =
                document.createElement("a");

            link.href =
                source.url;

            link.target = "_blank";

            link.rel =
                "noopener noreferrer";

            link.textContent =
                text;

            item.appendChild(link);

        } else {

            item.textContent =
                text;

        }


        sourceList.appendChild(item);

    });


    response.appendChild(sourceList);
}


/* =================================
   SEND QUESTION
================================= */

async function sendQuestion() {

    const question =
        questionInput.value.trim();


    if (question === "") {
        return;
    }


    if (city === "") {

        response.style.display = "block";

        response.innerHTML =
            "<b>Please enter your city first.</b>";

        response.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

        return;
    }


    /* Disable button while processing */

    sendButton.disabled = true;

    sendButton.innerText =
        "Thinking...";


    const answerElement =
        showProcessing(question);


    questionInput.value = "";


    response.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });


    try {

        const result =
            await fetch(
                API_BASE +
                "/api/chat/stream",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        conversation_id:
                            conversationId || null,

                        city: city,

                        message: question

                    })
                }
            );


        if (!result.ok) {

            throw new Error(
                "Backend returned HTTP " +
                result.status
            );

        }


        if (!result.body) {

            throw new Error(
                "Streaming is not supported by this browser."
            );

        }


        const reader =
            result.body.getReader();

        const decoder =
            new TextDecoder("utf-8");

        let buffer = "";

        let metadata = null;

        let firstToken = true;


        while (true) {

            const {
                value,
                done
            } = await reader.read();


            if (done) {
                break;
            }


            buffer +=
                decoder.decode(
                    value,
                    {
                        stream: true
                    }
                );


            const lines =
                buffer.split("\n");


            buffer =
                lines.pop();


            for (const line of lines) {

                if (!line.trim()) {
                    continue;
                }


                try {

                    const data =
                        JSON.parse(line);


                    /* -------------------------
                       META
                    ------------------------- */

                    if (
                        data.type === "meta"
                    ) {

                        metadata = data;

                        conversationId =
                            data.conversation_id ||
                            conversationId;

                        answerElement.textContent =
                            "";

                        showWeather(
                            data.weather
                        );

                    }


                    /* -------------------------
                       TOKEN
                    ------------------------- */

                    else if (
                        data.type === "token"
                    ) {

                        if (firstToken) {

                            answerElement.textContent =
                                "";

                            firstToken = false;

                        }

                        answerElement.textContent +=
                            data.text;

                    }


                    /* -------------------------
                       DONE
                    ------------------------- */

                    else if (
                        data.type === "done"
                    ) {

                        if (metadata) {

                            showSources(
                                metadata.sources
                            );

                        }

                    }


                    /* -------------------------
                       ERROR
                    ------------------------- */

                    else if (
                        data.type === "error"
                    ) {

                        throw new Error(
                            data.message ||
                            "Unknown backend error"
                        );

                    }

                } catch (parseError) {

                    console.log(
                        "Stream line error:",
                        parseError,
                        line
                    );

                }

            }

        }


        /*
           Process any final buffered line.
        */

        buffer =
            buffer.trim();

        if (buffer) {

            try {

                const data =
                    JSON.parse(buffer);

                if (
                    data.type === "token"
                ) {

                    answerElement.textContent +=
                        data.text;

                }

            } catch (error) {

                console.log(
                    "Final stream parse error:",
                    error
                );

            }

        }


    } catch (error) {

        console.error(
            "KrishiGPT error:",
            error
        );


        answerElement.textContent =
            "Unable to connect to KrishiGPT backend.\n\n" +
            "Please check that the Codespaces backend is running.";


        const errorElement =
            document.createElement("div");

        errorElement.style.marginTop = "10px";

        errorElement.textContent =
            "Error: " + error.message;

        response.appendChild(
            errorElement
        );

    }


    /* Re-enable button */

    sendButton.disabled = false;

    sendButton.innerText =
        "Send";

}


/* =================================
   ENTER KEY
================================= */

questionInput.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Enter") {

            event.preventDefault();

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

    div.textContent =
        text;

    return div.innerHTML;

}
