let currentRepo = "";

function copyCode(id) {
    navigator.clipboard.writeText(
        document.getElementById(id).innerText
    );
}

async function setRepository() {

    const repo = document.getElementById("repoLink").value;

    if (!repo) return;

    const btn = document.getElementById("repoBtn");

    btn.innerText = "Indexing...";

    try {

        await fetch("/indexRepo", {
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                repoLink:repo
            })
        });

        currentRepo = repo;

        localStorage.setItem("repo", repo);

        document.getElementById("repoLink").disabled = true;

        btn.innerText = "Change Repo";

        btn.onclick = () => {
            document.getElementById("repoLink").disabled = false;
            btn.innerText = "Set Repo";
            btn.onclick = setRepository;
        };

    } catch(e){
        btn.innerText = "Failed";
    }
}

function addMessage(text, cls){

    const chat = document.getElementById("chatWindow");

    const div = document.createElement("div");

    div.className = `message ${cls}`;

    div.textContent = text;

    chat.appendChild(div);

    chat.scrollTop = chat.scrollHeight;
}

async function sendMessage(){

    const input = document.getElementById("messageInput");

    const apiKey = document.getElementById("apiKey").value;

    const question = input.value;

    if(!question || !currentRepo) return;

    addMessage(question,"user");

    input.value = "";

    try{

        const response = await fetch("/ask",{
            method:"POST",
            headers:{
                "Content-Type":"application/json",
                "Authorization":"Bearer " + apiKey
            },
            body:JSON.stringify({
                repoLink:currentRepo,
                question:question
            })
        });

        const data = await response.json();

        addMessage(
            data.answer || data.error,
            "bot"
        );

    }catch(err){
        addMessage("Request failed.","bot");
    }
}

window.onload = () => {

    const savedRepo =
        localStorage.getItem("repo");

    if(savedRepo){

        currentRepo = savedRepo;

        document.getElementById("repoLink").value =
            savedRepo;

        document.getElementById("repoLink").disabled =
            true;

        const btn =
            document.getElementById("repoBtn");

        btn.innerText = "Change Repo";

        btn.onclick = () => {
            document.getElementById("repoLink").disabled = false;
            btn.innerText = "Set Repo";
            btn.onclick = setRepository;
        };
    }
};