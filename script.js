// const API_URL = "https://miniature-space-happiness-5v5q6grq65w2pppq-5000.app.github.dev";

async function askAI() {
    const input = document.getElementById("userInput");
        const chatBox = document.getElementById("chatBox");

            const message = input.value.trim();

                if (!message) return;

                    chatBox.innerHTML += `<p><b>You:</b> ${message}</p>`;
                        input.value = "";

                            try {
                                    const response = await fetch(API_URL + "/api/chat", {
                                                method: "POST",
                                                            headers: {
                                                                            "Content-Type": "application/json"
                                                                                        },
                                                                                                    body: JSON.stringify({
                                                                                                                    message: message
                                                                                                                                })
                                                                                                                                        });

                                                                                                                                                const data = await response.json();

                                                                                                                                                        chatBox.innerHTML += `<p><b>BongBrowser AI:</b> ${data.reply}</p>`;

                                                                                                                                                            } catch (error) {
                                                                                                                                                                    chatBox.innerHTML += `<p><b>Error:</b> AI Server Connect হচ্ছে না</p>`;
                                                                                                                                                                            console.log(error);
                                                                                                                                                                                }
                                                                                                                                                                                }