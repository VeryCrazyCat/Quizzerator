var socket = io();
var currentRoomID = null;
var quizName = null;
var quizData = null;
var userParent = null;
var currentQuestionData = null;
var totalUsers = 0;
var answersEnded = false;

$(document).ready(function(){ 
    createRoom();

    // Get quiz data from meta tags
    let quizDataMeta = document.querySelector("meta[name='host-quiz-data']");
    quizName = quizDataMeta.dataset.quiz_name;
    quizData = quizDataMeta.dataset.quiz_data;

    userParent = document.querySelector(".user-list");
    console.log("initialised document");

    document.querySelector(".quiz-results").hidden = true

    document.querySelector(".active-room").hidden = true
    document.querySelector(".inactive-room").hidden = false


    document.querySelector(".user-answer-display").hidden = true
    

    socket.on('room_data', function(msg) {
        updateRoomList(msg.data);
    });

    socket.on('room_creation_data', function(msg) {
        updateRoomIDDisplay(msg.data);
    });

    socket.on('receive_message_from_host', function(msg) {
        updateMessageDisplay(msg.data);
    });
    
    socket.on('receive_question', function(msg) {
        updateCurrentQuestion(msg.data);
    });

    socket.on('end_quiz', function(msg) {
        endHostQuiz(msg.data);
    });

    socket.on('host_get_answers', function(msg) {
        updateUserAnswerDisplay(msg.data, msg.number_of_answers);
    });
});

function createRoom() {
    document.querySelector(".active-room").hidden = false
    socket.emit("create", {});
    setInterval(function() {
        if (currentRoomID != null) {
            updateRoomListForAllUsers();
        }
    }, 5000);
}

function startLiveQuiz() {
    socket.emit("start_quiz");
    document.querySelector('.start-quiz').disabled = true;
    document.querySelector('.start-quiz').textContent = 'Quiz Started';
    document.querySelector(".quiz-results").hidden = true;
    document.querySelector(".user-answer-display").hidden = false;
    document.querySelector(".question-management").hidden = false;

    document.querySelector(".active-room").hidden = false
    document.querySelector(".inactive-room").hidden = true
    
    document.querySelector(".user-answer-display-message").innerHTML = `Waiting for Question Send!`
    nextQuestion()
}

function updateCurrentQuestion(questionData) {
    currentQuestionData = questionData;
    const questionNumber = document.querySelector('.question-number');
    const questionText = document.querySelector('.question-text');
    
    if (questionData && questionData.question) {
        questionNumber.textContent = `Question ${questionData.question_num+1}`;
        questionText.textContent = questionData.question;
    } else {
        questionNumber.textContent = 'No Question';
        questionText.textContent = 'No question sent yet';
    }
    document.querySelector(".user-answer-display-message").innerHTML = `0 of ${totalUsers} have answered:`
}

function updateRoomIDDisplay(room_id) {
    let roomIDDisplay = document.querySelector(".room-id-display");
    roomIDDisplay.innerHTML = `ID: ${room_id}`;
    currentRoomID = room_id;
    console.log("Updated room ID to:", room_id);
}

function updateRoomListForAllUsers() {
    socket.emit("get_room_info", {});
}

function updateRoomList(room_users) {
    totalUsers = 0
    userParent.innerHTML = "";
    for (let user of room_users.values()) {
        totalUsers++;
        createUserElement(user["display_name"]);
    }
}

function updateMessageDisplay(message) {
    let message_display = document.querySelector(".message-display");
    message_display.innerHTML = message;
}

function createUserElement(user) {
    let newUserDiv = document.createElement("div");
    let newUserName = document.createElement("p");
    newUserName.innerHTML = user;
    newUserDiv.appendChild(newUserName);
    userParent.appendChild(newUserDiv);
}

function updateUserAnswerDisplay(user, num_users) {
    let newUserName = document.createElement("p");
    newUserName.innerHTML = user;
    document.querySelector(".user-answers").appendChild(newUserName);
    document.querySelector(".user-answer-display-message").innerHTML = `${num_users} of ${totalUsers} have answered:`
}

function nextQuestion() {
    socket.emit("host_send_question");

    document.querySelector(".send-question").hidden = true;
    
    // Reset the end answers button
    const endAnswersButton = document.querySelector('.end-answers');
    endAnswersButton.disabled = false;
    endAnswersButton.textContent = 'End Answers';


    document.querySelector(".user-answers").innerHTML = ""
}

function endAnswers() {
    socket.emit("host_end_answers");
    const endAnswersButton = document.querySelector('.end-answers');
    endAnswersButton.disabled = true;
    endAnswersButton.textContent = 'Answers Ended';
    answersEnded = true;

    document.querySelector(".send-question").hidden = false;
}

function sendMessage() {
    let messageInput = document.querySelector(".message-input");
    let message = messageInput.value.trim();
    
    if (message) {
        socket.emit("host_send_message", {message: message});
        messageInput.value = '';
    }
}

function endHostQuiz(data) {
    document.querySelector(".create-room").hidden = false
    document.querySelector(".active-room").hidden = true
    document.querySelector(".user-answer-display").hidden = true;
    let quiz_results = document.querySelector(".quiz-results")
    quiz_results.hidden = false
    console.log(data)

    leaderboard = {}
    points_ = []

    for (user of data["users"]) {
        leaderboard[user["points"]] = user["display_name"]
        points_.push(user["points"])
    }

    points_.sort(function(a, b) {
        return b - a;
      });

    let i = 1
    for (points of points_) {
        user = leaderboard[points]
        let newUserName = document.createElement("p");
        newUserName.innerHTML = `${i}. ${user} - ${points} points`;
        document.querySelector(".quiz-results").appendChild(newUserName);
        i++
    }
}

