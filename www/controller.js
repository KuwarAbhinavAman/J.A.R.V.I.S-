$(document).ready(function () {
    // Track the current command ID for response pairing
    let currentCommandId = 0;
    let isProcessing = false;

    // Display messages in both chat and Siri wave
    eel.expose(DisplayMessage);
    function DisplayMessage(message) {
        try {
            if (!message) return;
            
            $('.siri-message').textillate('stop');
            $(".siri-message").html(`<li>${message}</li>`);
            $('.siri-message').textillate({
                loop: false,
                in: { effect: "fadeInUp", sync: true },
                out: { effect: "fadeOutUp", sync: true, delay: 2000 }
            }).textillate('start');
        } catch (e) {
            console.error("DisplayMessage error:", e);
        }
    }

    // Show the hood/mic interface
    eel.expose(ShowHood);
    function ShowHood() {
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
        isProcessing = false;
    }

    // Display user messages in chat
    eel.expose(senderText);
    function senderText(message) {
        try {
            if (!message || message.trim() === "") return;
            
            currentCommandId++;
            const chatBox = document.getElementById("chat-canvas-body");
            const messageDiv = document.createElement('div');
            messageDiv.className = 'row justify-content-end mb-4';
            messageDiv.setAttribute('data-command-id', currentCommandId);
            messageDiv.innerHTML = `
                <div class="width-size">
                    <div class="sender_message">${message}</div>
                </div>
            `;
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
            
            return currentCommandId;
        } catch (e) {
            console.error("senderText error:", e);
        }
    }

    // Display Jarvis responses in chat
    eel.expose(receiverText);
    function receiverText(message, commandId = currentCommandId) {
        try {
            if (!message || message.trim() === "") return;
            
            const chatBox = document.getElementById("chat-canvas-body");
            let targetElement = document.querySelector(`[data-command-id="${commandId}"]`);
            
            if (!targetElement) {
                targetElement = document.createElement('div');
                targetElement.className = 'row justify-content-start mb-4';
                targetElement.setAttribute('data-command-id', commandId);
                chatBox.appendChild(targetElement);
            }
            
            const responseDiv = document.createElement('div');
            responseDiv.className = 'row justify-content-start mb-4';
            responseDiv.innerHTML = `
                <div class="width-size">
                    <div class="receiver_message">${message}</div>
                </div>
            `;
            
            // Insert after the user's message
            targetElement.parentNode.insertBefore(responseDiv, targetElement.nextSibling);
            chatBox.scrollTop = chatBox.scrollHeight;
            
            // Also display in the Siri message area
            DisplayMessage(message);
        } catch (e) {
            console.error("receiverText error:", e);
        }
    }

    // UI control functions
    eel.expose(hideLoader);
    function hideLoader() {
        $("#Loader").attr("hidden", true);
        $("#FaceAuth").attr("hidden", false);
    }

    eel.expose(hideFaceAuth);
    function hideFaceAuth() {
        $("#FaceAuth").attr("hidden", true);
        $("#FaceAuthSuccess").attr("hidden", false);
    }

    eel.expose(hideFaceAuthSuccess);
    function hideFaceAuthSuccess() {
        $("#FaceAuthSuccess").attr("hidden", true);
        $("#HelloGreet").attr("hidden", false);
    }

    eel.expose(hideStart);
    function hideStart() {
        $("#Start").attr("hidden", true);
        setTimeout(function () {
            $("#Oval").addClass("animate__animated animate__zoomIn");
        }, 1000);
        setTimeout(function () {
            $("#Oval").attr("hidden", false);
        }, 1000);
    }
});