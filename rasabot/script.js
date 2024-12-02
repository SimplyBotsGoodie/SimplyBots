document.addEventListener('DOMContentLoaded', function() {
    // Select elements from the DOM
    const chatContainer = document.querySelector('.chat-container');
    const chatWindow = document.getElementById('chat-window');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const minimizeButton = document.querySelector('.minimize-button');

    // Debug logs
    console.log('Elements found:', {
        minimizeButton,
        chatContainer,
        chatWindow,
        userInput,
        sendButton
    });

    // Create and add toggle button
    const toggleButton = document.createElement('div');
    toggleButton.className = 'chat-toggle';
    toggleButton.innerHTML = '💬';
    document.body.appendChild(toggleButton);

    // Minimize/Maximize functionality with debug
    minimizeButton.addEventListener('click', (event) => {
        console.log('Minimize button clicked!');
        event.preventDefault();
        event.stopPropagation();
        chatContainer.style.display = 'none';
        toggleButton.style.display = 'flex';
    });

    toggleButton.addEventListener('click', (event) => {
        console.log('Toggle button clicked!');
        event.preventDefault();
        event.stopPropagation();
        chatContainer.style.display = 'block';
        toggleButton.style.display = 'none';
    });

    // Keep your existing event listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });

    // Rest of your existing code stays exactly the same
    function renderMarkdown(text) {
        return text.replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
                   .replace(/\n/g, '<br>');
    }

    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessageToChat('User', message);

            fetch("https://140f-142-110-39-187.ngrok-free.app/webhooks/rest/webhook", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Origin': 'https://renounding.github.io',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({ sender: 'user', message: message })
            })
            .then(response => response.json())
            .then(data => {
                if (data && data.length > 0) {
                    data.forEach(response => {
                        addMessageToChat('Goodie-Bot', response.text);
                    });
                } else {
                    addMessageToChat('Goodie-Bot', "I apologize, I didn't understand that. Could you please rephrase?");
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessageToChat('Goodie-Bot', 'Error connecting to the server. Please try again later.');
            });

            userInput.value = '';
        }
    }

    function addMessageToChat(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender.toLowerCase().replace(' ', '-'));
        messageElement.innerHTML = `<strong>${sender}:</strong> ${renderMarkdown(message)}`;
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // Add greeting message with topic buttons
    function addGreetingWithTopics() {
        // Greeting message
        addMessageToChat('Goodie-Bot', 'Welcome to our fake website. My name is Goodie and Im your Academic Assistant! Please select a topic below:');

        // Create a container for the topic buttons
        const topicsContainer = document.createElement('div');
        topicsContainer.classList.add('topics-container');

        // Define topics and create buttons
        const topics = ['Programs', 'Admissions', 'Fees'];
        topics.forEach(topic => {
            const button = document.createElement('button');
            button.className = 'topic-button';
            button.innerText = topic;
            button.addEventListener('click', () => handleTopicSelection(topic));
            topicsContainer.appendChild(button);
        });

        // Append the topics container to the chat window
        chatWindow.appendChild(topicsContainer);
    }

    // Handle topic selection by sending the selected topic to the bot
    function handleTopicSelection(topic) {
        addMessageToChat('User', topic); // Display selected topic as user message

        fetch("https://140f-142-110-39-187.ngrok-free.app/webhooks/rest/webhook", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Origin': 'https://renounding.github.io',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({ sender: 'user', message: topic })
        })
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                data.forEach(response => {
                    addMessageToChat('Goodie-Bot', response.text);
                });
            } else {
                addMessageToChat('Goodie-Bot', "I apologize, I didn't understand that. Could you please rephrase?");
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessageToChat('Goodie-Bot', 'Error connecting to the server. Please try again later.');
        });
    }

    // Initialize the chatbot with the greeting and topic buttons
    addGreetingWithTopics();
});
