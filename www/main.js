$(document).ready(function () {
    // Initialize Eel and animations
    eel.init()();

    // Text animations
    $('.text').textillate({
        loop: true,
        sync: true,
        in: { effect: "bounceIn" },
        out: { effect: "bounceOut" }
    });

    // Siri Wave configuration
    const siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 800,
        height: 200,
        style: "ios9",
        amplitude: "1",
        speed: "0.30",
        autostart: true
    });

    // Siri message animation
    $('.siri-message').textillate({
        autoStart: false,
        in: { effect: "fadeInUp", sync: true, delay: 50 },
        out: { effect: "fadeOutUp", sync: true, delay: 50 }
    });

    // Ensure mic button is visible on load
    $("#MicBtn").attr('hidden', false);
    $("#SendBtn").attr('hidden', true);

    // Mic button click handler
    $("#MicBtn").click(function () {
        if (!$("#MicBtn").attr("hidden")) {
            startVoiceCommand();
        }
    });

    // Keyboard shortcut (Cmd/Ctrl + J)
    $(document).keyup(function (e) {
        if ((e.key === 'j' && e.metaKey) || (e.key === 'j' && e.ctrlKey)) {
            startVoiceCommand();
        }
    });

    function startVoiceCommand() {
        eel.playAssistantSound();
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        $("#MicBtn").attr('hidden', true); // Hide mic while processing
        processCommand(1); // 1 indicates voice command
    }

    // Process commands (voice or text)
    async function processCommand(mode) {
        try {
            const result = await new Promise((resolve) => {
                eel.allCommands(mode)((response) => resolve(response))
                    .catch((error) => {
                        console.error('Command error:', error);
                        resolve(false);
                    });
            });
            
            if (!result) {
                DisplayMessage("I didn't catch that. Please try again.");
            }
        } catch (error) {
            console.error('Process command error:', error);
            DisplayMessage("Sorry, something went wrong.");
        } finally {
            // Always restore mic button after command processing
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        }
    }

    // Toggle between mic and send button based on input
    function ShowHideButton(message) {
        if (!message || message.length === 0) {
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        } else {
            $("#MicBtn").attr('hidden', true);
            $("#SendBtn").attr('hidden', false);
        }
    }

    // Handle text input changes
    $("#chatbox").keyup(function () {
        ShowHideButton($(this).val());
    });

    // Send button handler
    $("#SendBtn").click(function () {
        const message = $("#chatbox").val().trim();
        if (message) {
            eel.playAssistantSound();
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            $("#SendBtn").attr('hidden', true);
            processCommand(message); // Pass text directly
            $(this).val("");
        }
    });

    // Enter key handler
    $("#chatbox").keypress(function (e) {
        if (e.which === 13) { // Enter key
            const message = $(this).val().trim();
            if (message) {
                eel.playAssistantSound();
                $("#Oval").attr("hidden", true);
                $("#SiriWave").attr("hidden", false);
                $("#SendBtn").attr('hidden', true);
                processCommand(message); // Pass text directly
                $(this).val("");
            }
        }
    });
});